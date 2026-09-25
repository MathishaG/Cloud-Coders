import re
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def load_activities(path):
    return pd.read_csv(path)


# The chatbot looks for hobbies and interests that may not be academic.
# A student does not have to say "I want to join a dance club" explicitly.
# Natural descriptions such as "I like dancing" or "I enjoy performing" are enough.
INTEREST_KEYWORDS = {
    "Dance & Performing Arts": [
        "dance", "dancing", "dancer", "choreography", "choreograph",
        "performing", "performance", "stage", "folk dance", "classical dance",
        "hip hop", "ballet", "bharatanatyam", "kathak"
    ],
    "Music": [
        "music", "singing", "sing", "singer", "guitar", "piano", "drums",
        "keyboard", "violin", "instrument", "song", "compose", "composing"
    ],
    "Sports & Fitness": [
        "sport", "sports", "football", "cricket", "basketball", "badminton",
        "volleyball", "tennis", "running", "cycling", "swimming", "fitness",
        "gym", "yoga", "athletics"
    ],
    "Art & Design": [
        "art", "drawing", "draw", "painting", "paint", "sketch", "sketching",
        "design", "graphics", "poster", "illustration", "craft", "creative"
    ],
    "Photography & Media": [
        "photography", "photograph", "camera", "photo", "videography", "video",
        "editing", "edit videos", "film", "filmmaking", "content creation",
        "content creator"
    ],
    "Communication": [
        "public speaking", "speaking", "speech", "debate", "debating", "presentation",
        "presenting", "communication", "discussion", "storytelling"
    ],
    "Leadership & Events": [
        "leadership", "leader", "organizing", "organising", "event management",
        "events", "management", "volunteering", "volunteer", "community service"
    ],
    "Drama & Theatre": [
        "acting", "actor", "drama", "theatre", "theater", "play", "stage acting",
        "monologue"
    ],
    "Technology": [
        "coding", "programming", "python", "java", "software", "developer",
        "robotics", "technology", "hackathon", "web development"
    ],
    "Entrepreneurship": [
        "entrepreneurship", "startup", "business", "business ideas", "innovation",
        "marketing", "startup ideas"
    ]
}


def _normalise_text(text):
    return re.sub(r"\s+", " ", str(text).lower()).strip()


def detect_interests(user_text):
    """Return hobby/interest categories detected from natural-language text."""
    text = _normalise_text(user_text)
    detected = []

    for category, keywords in INTEREST_KEYWORDS.items():
        if any(re.search(r"\b" + re.escape(keyword) + r"\b", text) for keyword in keywords):
            detected.append(category)

    return detected



def _keyword_scores(user_text, activities):
    """Give an additional score when a detected hobby category matches an activity."""
    detected = detect_interests(user_text)
    scores = []

    for _, activity in activities.iterrows():
        category = str(activity.get("category", "")).lower()
        activity_text = _normalise_text(
            " ".join(
                [
                    str(activity.get("activity_name", "")),
                    str(activity.get("description", "")),
                    str(activity.get("search_text", ""))
                ]
            )
        )

        score = 0.0
        for interest in detected:
            interest_words = interest.lower().replace("&", " ").split()
            if any(word in category for word in interest_words):
                score += 1.0
            if any(word in activity_text for word in interest_words):
                score += 0.5

        scores.append(score)

    return scores, detected


def recommend_activities(user_text, activities, top_n=5):
    """Recommend extracurricular activities using both TF-IDF and hobby keywords."""
    activities = activities.copy()
    corpus = activities["search_text"].fillna("").astype(str).tolist()
    text = _normalise_text(user_text)

    vectorizer = TfidfVectorizer(
        stop_words="english",
        ngram_range=(1, 2)
    )

    matrix = vectorizer.fit_transform(corpus + [text])
    similarities = cosine_similarity(matrix[-1], matrix[:-1]).flatten()

    keyword_scores, detected = _keyword_scores(text, activities)

    # Keyword matching is deliberately given more weight for explicit hobbies.
    # This makes phrases such as "I like dancing" reliably surface dance-related
    # activities even when the rest of the sentence contains unrelated wording.
    max_keyword = max(keyword_scores) if keyword_scores else 0
    if max_keyword > 0:
        keyword_normalised = [score / max_keyword for score in keyword_scores]
        combined = (similarities * 0.45) + (pd.Series(keyword_normalised).to_numpy() * 0.55)
    else:
        combined = similarities

    activities["similarity"] = combined
    activities["detected_interest"] = ", ".join(detected) if detected else "General interest"

    return activities.sort_values(
        "similarity",
        ascending=False
    ).head(top_n)


def chatbot_reply(user_text, activities):
    """Generate an interest summary and personalized extracurricular recommendations."""
    detected = detect_interests(user_text)

    if detected:
        reply = (
            "I detected these interests: "
            + ", ".join(detected)
            + ". Based on them, here are some extracurricular activities you may enjoy."
        )
    else:
        reply = (
            "I could not identify a specific hobby yet. I can still recommend activities "
            "from the details you shared."
        )

    recommendations = recommend_activities(
        user_text,
        activities,
        top_n=5
    )

    return reply, recommendations
