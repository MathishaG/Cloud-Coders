"""
styles.py - Design system and reusable UI components for EduPulse AI
Provides custom CSS injection and HTML components for modern, hackathon-ready UI.
"""

CUSTOM_CSS = """
<style>
/* Import modern typography */
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

/* Global Reset & Typography */
html, body, .stApp {
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif !important;
    color: #0f172a;
    background-color: #f8fafc;
}

/* Ensure Material Symbols / Icons are never overridden by custom fonts */
[data-testid="stIconMaterial"], .material-symbols-rounded, .material-symbols-outlined, .material-icons {
    font-family: 'Material Symbols Rounded', 'Material Icons' !important;
}


/* Main Container spacing */
.main .block-container {
    padding-top: 1.5rem !important;
    padding-bottom: 3.5rem !important;
    max-width: 1280px !important;
}

/* Sidebar Styling */
[data-testid="stSidebar"] {
    background-color: #0f172a !important;
    border-right: 1px solid #1e293b !important;
}

[data-testid="stSidebar"] * {
    color: #e2e8f0 !important;
}

[data-testid="stSidebar"] hr {
    border-color: #334155 !important;
}

[data-testid="stSidebar"] .stButton > button {
    background: #1e293b !important;
    color: #f8fafc !important;
    border: 1px solid #334155 !important;
    border-radius: 8px !important;
    transition: all 0.2s ease;
}

[data-testid="stSidebar"] .stButton > button:hover {
    background: #ef4444 !important;
    color: #ffffff !important;
    border-color: #ef4444 !important;
    transform: translateY(-1px);
}

/* Header & Typography */
h1, h2, h3, h4, h5, h6 {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    font-weight: 700 !important;
    color: #0f172a !important;
    letter-spacing: -0.02em;
}

h1 {
    font-size: 2rem !important;
}

h2 {
    font-size: 1.5rem !important;
    margin-top: 1rem !important;
}

h3 {
    font-size: 1.25rem !important;
}

p, span, label {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
}

/* Modern Tabs */
.stTabs [data-baseweb="tab-list"] {
    gap: 8px;
    background-color: #f1f5f9;
    padding: 6px;
    border-radius: 12px;
    border: 1px solid #e2e8f0;
}

.stTabs [data-baseweb="tab"] {
    height: auto;
    padding: 10px 20px;
    border-radius: 8px;
    font-weight: 600;
    font-size: 0.92rem;
    color: #475569;
    background-color: transparent;
    border: none;
    transition: all 0.2s ease;
}

.stTabs [data-baseweb="tab"]:hover {
    color: #4f46e5;
    background-color: rgba(255, 255, 255, 0.6);
}

.stTabs [aria-selected="true"] {
    background-color: #ffffff !important;
    color: #4f46e5 !important;
    box-shadow: 0 2px 4px rgba(0, 0, 0, 0.06);
}

/* Buttons */
.stButton > button {
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-size: 0.95rem !important;
    padding: 0.6rem 1.4rem !important;
    transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
    border: 1px solid transparent !important;
}

/* Primary Button Styling */
div.stButton > button[kind="primary"], div.stFormSubmitButton > button {
    background: linear-gradient(135deg, #4f46e5 0%, #4338ca 100%) !important;
    color: #ffffff !important;
    box-shadow: 0 4px 6px -1px rgba(79, 70, 229, 0.25), 0 2px 4px -2px rgba(79, 70, 229, 0.25) !important;
}

div.stButton > button[kind="primary"]:hover, div.stFormSubmitButton > button:hover {
    background: linear-gradient(135deg, #4338ca 0%, #3730a3 100%) !important;
    box-shadow: 0 6px 10px -1px rgba(79, 70, 229, 0.35) !important;
    transform: translateY(-1px);
}

div.stButton > button[kind="secondary"] {
    background: #ffffff !important;
    color: #334155 !important;
    border: 1px solid #cbd5e1 !important;
}

div.stButton > button[kind="secondary"]:hover {
    border-color: #4f46e5 !important;
    color: #4f46e5 !important;
    background: #f8fafc !important;
    transform: translateY(-1px);
}

/* Explicit, High-Contrast Labels for All Input Widgets */
label,
[data-testid="stWidgetLabel"],
[data-testid="stWidgetLabel"] p,
[data-testid="stWidgetLabel"] span,
[data-testid="stWidgetLabel"] div,
.stTextInput label,
.stNumberInput label,
.stSelectbox label,
.stTextArea label {
    font-family: 'Plus Jakarta Sans', sans-serif !important;
    color: #0f172a !important;
    font-size: 0.88rem !important;
    font-weight: 700 !important;
    letter-spacing: -0.01em !important;
    margin-bottom: 0.35rem !important;
    display: block !important;
    visibility: visible !important;
    opacity: 1 !important;
}

/* Text Inputs & Text Areas */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
[data-testid="stTextInput"] input,
[data-testid="stTextArea"] textarea {
    border-radius: 10px !important;
    border: 1.5px solid #cbd5e1 !important;
    background-color: #ffffff !important;
    color: #0f172a !important;
    font-size: 0.95rem !important;
    padding: 0.65rem 1rem !important;
    transition: border-color 0.2s ease, box-shadow 0.2s ease;
}

.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus,
[data-testid="stTextInput"] input:focus,
[data-testid="stTextArea"] textarea:focus {
    border-color: #4f46e5 !important;
    box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.15) !important;
    outline: none !important;
}

/* Number Inputs - Crisp White Background & High Contrast */
.stNumberInput,
[data-testid="stNumberInput"] {
    background-color: transparent !important;
}

[data-testid="stNumberInput"] > div,
.stNumberInput > div,
.stNumberInput div[data-baseweb="input"],
.stNumberInput div[data-baseweb="base-input"] {
    background-color: #ffffff !important;
    border-radius: 10px !important;
    border: 1.5px solid #cbd5e1 !important;
    color: #0f172a !important;
    overflow: hidden !important;
    transition: border-color 0.2s ease, box-shadow 0.2s ease !important;
}

[data-testid="stNumberInput"] > div:focus-within,
.stNumberInput > div:focus-within {
    border-color: #4f46e5 !important;
    box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.15) !important;
}

[data-testid="stNumberInput"] input,
.stNumberInput input {
    background-color: #ffffff !important;
    color: #0f172a !important;
    font-size: 0.95rem !important;
    font-weight: 600 !important;
    padding: 0.65rem 1rem !important;
    border: none !important;
}

[data-testid="stNumberInput"] button,
.stNumberInput button {
    background-color: #f1f5f9 !important;
    color: #1e293b !important;
    border: none !important;
    transition: background 0.15s ease !important;
}

[data-testid="stNumberInput"] button:hover,
.stNumberInput button:hover {
    background-color: #e2e8f0 !important;
    color: #0f172a !important;
}

/* Selectboxes & Multiselect */
[data-baseweb="select"] {
    background-color: #ffffff !important;
    border-radius: 10px !important;
}

[data-baseweb="select"] > div {
    border-radius: 10px !important;
    border: 1.5px solid #cbd5e1 !important;
    background-color: #ffffff !important;
    color: #0f172a !important;
    min-height: 42px !important;
}

[data-baseweb="select"] span,
[data-baseweb="select"] div {
    color: #0f172a !important;
    font-weight: 500 !important;
}

[data-baseweb="popover"], [data-baseweb="menu"], [data-baseweb="menu"] li {
    background-color: #ffffff !important;
    color: #0f172a !important;
}

/* Metric component override */
[data-testid="stMetric"] {
    background-color: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 1rem 1.25rem;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
}

[data-testid="stMetricLabel"] {
    font-size: 0.85rem !important;
    font-weight: 600 !important;
    color: #64748b !important;
    text-transform: uppercase;
    letter-spacing: 0.04em;
}

[data-testid="stMetricValue"] {
    font-size: 1.75rem !important;
    font-weight: 700 !important;
    color: #0f172a !important;
}

/* Dataframe styling */
[data-testid="stDataFrame"] {
    border: 1px solid #e2e8f0 !important;
    border-radius: 12px !important;
    overflow: hidden !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.04) !important;
}

/* Progress bar styling */
.stProgress > div > div > div > div {
    background: linear-gradient(90deg, #4f46e5 0%, #06b6d4 100%) !important;
    border-radius: 9999px !important;
}

/* Custom Card Classes */
.saas-card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 14px;
    padding: 1.5rem;
    margin-bottom: 1.25rem;
    box-shadow: 0 1px 3px rgba(15, 23, 42, 0.05);
    transition: transform 0.2s ease, box-shadow 0.2s ease;
}

.saas-card:hover {
    box-shadow: 0 4px 6px -1px rgba(15, 23, 42, 0.08);
}

.stat-kpi-card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 14px;
    padding: 1.25rem;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.04);
    position: relative;
    overflow: hidden;
    height: 100%;
}

.stat-kpi-card::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 4px;
}

.kpi-indigo::before { background: linear-gradient(90deg, #4f46e5, #6366f1); }
.kpi-emerald::before { background: linear-gradient(90deg, #059669, #10b981); }
.kpi-amber::before { background: linear-gradient(90deg, #d97706, #f59e0b); }
.kpi-rose::before { background: linear-gradient(90deg, #e11d48, #f43f5e); }
.kpi-cyan::before { background: linear-gradient(90deg, #0284c7, #06b6d4); }

.kpi-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.5rem;
}

.kpi-title {
    font-size: 0.8rem;
    font-weight: 700;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

.kpi-icon {
    font-size: 1.3rem;
    width: 36px;
    height: 36px;
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    background: #f8fafc;
}

.kpi-value {
    font-size: 1.85rem;
    font-weight: 800;
    color: #0f172a;
    line-height: 1.2;
    margin-bottom: 0.25rem;
}

.kpi-footer {
    font-size: 0.8rem;
    color: #64748b;
    display: flex;
    align-items: center;
    gap: 4px;
}

/* Badges */
.badge {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    padding: 4px 10px;
    border-radius: 9999px;
    font-size: 0.78rem;
    font-weight: 700;
    letter-spacing: 0.02em;
}

.badge-low {
    background-color: #ecfdf5;
    color: #047857;
    border: 1px solid #a7f3d0;
}

.badge-medium {
    background-color: #fffbeb;
    color: #b45309;
    border: 1px solid #fde68a;
}

.badge-high {
    background-color: #fff1f2;
    color: #be123c;
    border: 1px solid #fecdd3;
}

.badge-indigo {
    background-color: #eef2ff;
    color: #4338ca;
    border: 1px solid #c7d2fe;
}

.badge-neutral {
    background-color: #f1f5f9;
    color: #475569;
    border: 1px solid #cbd5e1;
}

/* Activity Recommendation Card */
.activity-card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 1.25rem;
    margin-bottom: 1rem;
    transition: all 0.2s ease;
}

.activity-card:hover {
    border-color: #cbd5e1;
    box-shadow: 0 4px 12px rgba(15, 23, 42, 0.06);
    transform: translateY(-2px);
}

.activity-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 0.5rem;
}

.activity-title {
    font-size: 1.05rem;
    font-weight: 700;
    color: #0f172a;
}

.activity-desc {
    font-size: 0.9rem;
    color: #475569;
    line-height: 1.5;
    margin-bottom: 0.75rem;
}

/* Faculty Candidate Card */
.faculty-card {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 1.25rem;
    margin-bottom: 0.75rem;
    transition: all 0.2s ease;
}

.faculty-card:hover {
    border-color: #a5b4fc;
    background: #faf5ff;
}

/* Hero Section */
.hero-banner {
    background: linear-gradient(135deg, #1e1b4b 0%, #312e81 50%, #4338ca 100%);
    border-radius: 16px;
    padding: 2.25rem 2.5rem;
    color: #ffffff;
    margin-bottom: 2rem;
    box-shadow: 0 10px 25px -5px rgba(49, 46, 129, 0.3);
    position: relative;
    overflow: hidden;
}

.hero-banner h1 {
    color: #ffffff !important;
    font-size: 2.2rem !important;
    margin-bottom: 0.5rem !important;
}

.hero-banner p {
    color: #e0e7ff !important;
    font-size: 1.05rem !important;
    max-width: 780px;
    line-height: 1.6;
    margin-bottom: 0 !important;
}

.hero-tag {
    display: inline-block;
    background: rgba(255, 255, 255, 0.15);
    backdrop-filter: blur(8px);
    border: 1px solid rgba(255, 255, 255, 0.25);
    color: #ffffff;
    padding: 4px 12px;
    border-radius: 9999px;
    font-size: 0.8rem;
    font-weight: 600;
    margin-bottom: 0.8rem;
    letter-spacing: 0.03em;
}

/* Prompt inspiration pill */
.prompt-chip {
    display: inline-block;
    background: #f1f5f9;
    border: 1px solid #e2e8f0;
    color: #334155;
    padding: 6px 14px;
    border-radius: 9999px;
    font-size: 0.82rem;
    margin-right: 6px;
    margin-bottom: 8px;
    cursor: pointer;
    transition: all 0.15s ease;
}

.prompt-chip:hover {
    background: #e0e7ff;
    color: #4338ca;
    border-color: #c7d2fe;
}

/* Diagnostic Box */
.diagnostic-box {
    border-radius: 12px;
    padding: 1.25rem 1.5rem;
    margin: 1rem 0;
}

.diagnostic-high {
    background-color: #fff1f2;
    border: 1.5px solid #fda4af;
    color: #9f1239;
}

.diagnostic-medium {
    background-color: #fffbeb;
    border: 1.5px solid #fcd34d;
    color: #92400e;
}

.diagnostic-low {
    background-color: #ecfdf5;
    border: 1.5px solid #6ee7b7;
    color: #065f46;
}

/* Feature grid on login */
.feature-box {
    background: #ffffff;
    border: 1px solid #e2e8f0;
    border-radius: 12px;
    padding: 1.25rem;
    height: 100%;
    box-shadow: 0 1px 3px rgba(0,0,0,0.03);
}

.feature-box h4 {
    color: #0f172a !important;
    font-size: 1rem !important;
    margin-top: 0.5rem !important;
    margin-bottom: 0.35rem !important;
}

.feature-box p {
    color: #64748b !important;
    font-size: 0.85rem !important;
    line-height: 1.4 !important;
    margin: 0 !important;
}
</style>
"""


def get_risk_badge(risk_level: str) -> str:
    """Return styled HTML badge for risk levels."""
    risk = str(risk_level).strip().capitalize()
    if risk == "Low":
        return '<span class="badge badge-low">🟢 Low Risk (Safe)</span>'
    elif risk == "Medium":
        return '<span class="badge badge-medium">🟡 Medium Risk (Watchlist)</span>'
    elif risk == "High":
        return '<span class="badge badge-high">🔴 High Risk (Urgent Action)</span>'
    return f'<span class="badge badge-neutral">{risk}</span>'


def clean_html(html_text: str) -> str:
    """Safely unindent all lines so Markdown parsers never treat HTML as an indented code block."""
    import re
    return re.sub(r'^[ \t]+', '', html_text, flags=re.MULTILINE).strip()


def render_stat_card(title: str, value: str, footer: str = "", icon: str = "📊", theme: str = "indigo") -> str:
    """Render a KPI statistic card."""
    theme_class = f"kpi-{theme}"
    return (
        f'<div class="stat-kpi-card {theme_class}">'
        f'<div class="kpi-header">'
        f'<span class="kpi-title">{title}</span>'
        f'<span class="kpi-icon">{icon}</span>'
        f'</div>'
        f'<div class="kpi-value">{value}</div>'
        f'<div class="kpi-footer">{footer}</div>'
        f'</div>'
    )


def render_hero_banner(title: str, subtitle: str, tag: str = "", icon: str = "") -> str:
    """Render the top hero banner."""
    tag_html = f'<span class="hero-tag">{icon} {tag}</span>' if tag else ''
    return (
        f'<div class="hero-banner">'
        f'{tag_html}'
        f'<h1>{title}</h1>'
        f'<p>{subtitle}</p>'
        f'</div>'
    )


def render_activity_card(name: str, category: str, description: str, score_pct: float, interest_tag: str) -> str:
    """Render an extracurricular recommendation card."""
    score_display = f"{int(score_pct * 100)}%" if score_pct > 0 else "Curated Fit"
    return (
        f'<div class="activity-card">'
        f'<div class="activity-header">'
        f'<span class="activity-title">🎯 {name}</span>'
        f'<span class="badge badge-indigo">📂 {category}</span>'
        f'</div>'
        f'<p class="activity-desc">{description}</p>'
        f'<div style="display: flex; justify-content: space-between; align-items: center; border-top: 1px solid #f1f5f9; padding-top: 0.6rem;">'
        f'<span style="font-size: 0.8rem; color: #64748b;">Matched Interest: <strong style="color: #4338ca;">{interest_tag}</strong></span>'
        f'<span class="badge badge-low">✨ {score_display} Match Score</span>'
        f'</div>'
        f'</div>'
    )

