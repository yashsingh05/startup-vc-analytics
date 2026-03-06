import streamlit as st
import json
import numpy as np
from pathlib import Path

st.set_page_config(page_title="Startup Scorer", page_icon="🎯", layout="wide")

PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data" / "processed"
MODELS_DIR = PROJECT_ROOT / "data" / "models"

FEATURES = [
    "batch_year_int", "company_age_years", "is_recent_batch", "batch_season_num",
    "is_b2b_flag", "is_b2c_flag", "is_ai", "is_saas",
    "is_fintech", "is_healthcare", "is_opensource",
    "team_size", "has_team_data",
    "has_github", "has_producthunt", "has_sec_filing", "has_news_mention",
    "total_github_stars", "ph_votes", "news_mention_count",
    "num_sources", "visibility_score",
    "description_length", "description_word_count", "has_description",
    "is_us", "is_sf_bay", "is_nyc",
    "num_tags", "is_hiring", "top_company",
]

TRACTION_FEATURES = [
    "batch_year_int", "company_age_years", "is_recent_batch",
    "is_b2b_flag", "is_b2c_flag", "is_ai", "is_saas",
    "is_fintech", "is_healthcare", "is_opensource",
    "team_size", "has_team_data",
    "is_us", "is_sf_bay", "is_nyc",
    "num_tags", "description_word_count",
    "has_description", "is_hiring", "top_company",
]

@st.cache_resource
def train_models():
    """Train models fresh from the data — avoids pickle incompatibility."""
    from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
    from sklearn.model_selection import train_test_split

    with open(DATA_DIR / "master_companies.json", encoding="utf-8") as f:
        companies = json.load(f)

    # Build feature matrix
    X_data, y_data = [], []
    for c in companies:
        row = []
        for feat in FEATURES:
            val = c.get(feat, 0)
            if val is None or val == "":
                val = 0
            if isinstance(val, bool):
                val = int(val)
            try:
                row.append(float(val))
            except:
                row.append(0.0)
        target = c.get("is_success", 0)
        if target is None:
            continue
        X_data.append(row)
        y_data.append(int(target))

    X = np.array(X_data)
    y = np.array(y_data)

    # Train success classifier
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    clf = RandomForestClassifier(n_estimators=200, max_depth=10, min_samples_split=5,
                                  class_weight="balanced", random_state=42, n_jobs=-1)
    clf.fit(X_train, y_train)

    # Train traction model
    tX, ty = [], []
    for c in companies:
        vis = c.get("visibility_score", 0) or 0
        row = []
        for feat in TRACTION_FEATURES:
            val = c.get(feat, 0)
            if val is None or val == "":
                val = 0
            if isinstance(val, bool):
                val = int(val)
            try:
                row.append(float(val))
            except:
                row.append(0.0)
        tX.append(row)
        ty_cat = 0
        if vis > 0:
            ty_cat = 1
        if vis >= 5:
            ty_cat = 2
        ty.append(ty_cat)

    tX = np.array(tX)
    ty = np.array(ty)
    traction_model = GradientBoostingClassifier(n_estimators=150, max_depth=5, random_state=42)
    traction_model.fit(tX, ty)

    # Feature importances
    importances = {f: float(i) for f, i in zip(FEATURES, clf.feature_importances_)}

    return clf, traction_model, importances

with st.spinner("Training models (first load only)..."):
    classifier, traction_model, feature_importances = train_models()

st.title("🎯 Startup Success Scorer")
st.markdown("*Input startup characteristics and our ML model predicts success probability*")
st.markdown("---")

# ═══════════════════════════════════════════
# INPUT FORM
# ═══════════════════════════════════════════
st.subheader("Enter Startup Details")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("### Company Info")
    batch_year = st.slider("Batch / Founded Year", 2005, 2026, 2024)
    company_age = 2026 - batch_year
    is_recent = 1 if batch_year >= 2023 else 0
    batch_season = st.selectbox("Season", ["Winter", "Spring", "Summer", "Fall"])
    season_map = {"Winter": 1, "Spring": 2, "Summer": 3, "Fall": 4}
    batch_season_num = season_map[batch_season]
    team_size = st.number_input("Team Size", min_value=1, max_value=10000, value=10)

with col2:
    st.markdown("### Industry & Type")
    is_b2b = st.checkbox("B2B", value=True)
    is_b2c = st.checkbox("B2C")
    is_ai = st.checkbox("AI / Machine Learning")
    is_saas = st.checkbox("SaaS")
    is_fintech = st.checkbox("Fintech")
    is_healthcare = st.checkbox("Healthcare")
    is_opensource = st.checkbox("Open Source")

with col3:
    st.markdown("### Traction Signals")
    has_github = st.checkbox("Has GitHub presence")
    github_stars = st.number_input("GitHub Stars", 0, 500000, 0) if has_github else 0
    has_ph = st.checkbox("Launched on ProductHunt")
    ph_votes = st.number_input("ProductHunt Upvotes", 0, 20000, 0) if has_ph else 0
    has_sec = st.checkbox("Has SEC filing")
    has_news = st.checkbox("Mentioned in news")
    news_count = st.number_input("News mentions", 0, 100, 0) if has_news else 0
    is_hiring = st.checkbox("Currently hiring")
    is_top = st.checkbox("YC Top Company")

col4, col5 = st.columns(2)
with col4:
    st.markdown("### Location")
    is_us = st.checkbox("US-based", value=True)
    is_sf = st.checkbox("SF Bay Area")
    is_nyc = st.checkbox("New York")

with col5:
    st.markdown("### Description")
    desc_length = st.slider("Description length (chars)", 0, 2000, 500)
    desc_words = desc_length // 5
    has_desc = 1 if desc_length > 10 else 0
    num_tags = st.slider("Number of tags", 0, 20, 3)

st.markdown("---")

# ═══════════════════════════════════════════
# PREDICTION
# ═══════════════════════════════════════════
if st.button("🚀 Predict Success", type="primary", use_container_width=True):
    num_sources = sum([has_github, has_ph, has_sec, has_news]) + 1
    visibility = (
        min(github_stars / 1000, 10) * 3 +
        min(ph_votes / 500, 10) * 2 +
        news_count * 1.5 +
        (5 if has_sec else 0) +
        (3 if is_hiring else 0) +
        (5 if is_top else 0)
    )

    feature_map = {
        "batch_year_int": batch_year, "company_age_years": company_age,
        "is_recent_batch": is_recent, "batch_season_num": batch_season_num,
        "is_b2b_flag": int(is_b2b), "is_b2c_flag": int(is_b2c),
        "is_ai": int(is_ai), "is_saas": int(is_saas),
        "is_fintech": int(is_fintech), "is_healthcare": int(is_healthcare),
        "is_opensource": int(is_opensource),
        "team_size": team_size, "has_team_data": 1,
        "has_github": int(has_github), "has_producthunt": int(has_ph),
        "has_sec_filing": int(has_sec), "has_news_mention": int(has_news),
        "total_github_stars": github_stars, "ph_votes": ph_votes,
        "news_mention_count": news_count,
        "num_sources": num_sources, "visibility_score": visibility,
        "description_length": desc_length, "description_word_count": desc_words,
        "has_description": has_desc,
        "is_us": int(is_us), "is_sf_bay": int(is_sf), "is_nyc": int(is_nyc),
        "num_tags": num_tags, "is_hiring": int(is_hiring), "top_company": int(is_top),
    }

    # Success prediction
    X_input = np.array([[feature_map.get(f, 0) for f in FEATURES]])
    success_prob = classifier.predict_proba(X_input)[0][1]
    success_pred = classifier.predict(X_input)[0]

    # Traction prediction
    X_traction = np.array([[feature_map.get(f, 0) for f in TRACTION_FEATURES]])
    traction_pred = traction_model.predict(X_traction)[0]
    traction_labels = {0: "Low", 1: "Medium", 2: "High"}

    # ─── Display Results ───
    st.markdown("---")
    st.subheader("📊 Prediction Results")

    r1, r2, r3 = st.columns(3)

    with r1:
        color = "#2ecc71" if success_prob >= 0.7 else "#f39c12" if success_prob >= 0.4 else "#e74c3c"
        st.markdown(f"""
        <div style="background-color:{color}22; border: 2px solid {color}; 
                    border-radius:10px; padding:20px; text-align:center;">
            <h2 style="color:{color}; margin:0;">Success Probability</h2>
            <h1 style="color:{color}; margin:0; font-size:3em;">{success_prob*100:.1f}%</h1>
            <p style="color:{color};">{'LIKELY SUCCESS' if success_pred else 'AT RISK'}</p>
        </div>
        """, unsafe_allow_html=True)

    with r2:
        traction_color = {"Low": "#e74c3c", "Medium": "#f39c12", "High": "#2ecc71"}
        traction_label = traction_labels.get(traction_pred, "Unknown")
        tc = traction_color.get(traction_label, "#95a5a6")
        st.markdown(f"""
        <div style="background-color:{tc}22; border: 2px solid {tc}; 
                    border-radius:10px; padding:20px; text-align:center;">
            <h2 style="color:{tc}; margin:0;">Traction Level</h2>
            <h1 style="color:{tc}; margin:0; font-size:3em;">{traction_label}</h1>
            <p style="color:{tc};">Predicted visibility tier</p>
        </div>
        """, unsafe_allow_html=True)

    with r3:
        st.markdown(f"""
        <div style="background-color:#3498db22; border: 2px solid #3498db; 
                    border-radius:10px; padding:20px; text-align:center;">
            <h2 style="color:#3498db; margin:0;">Visibility Score</h2>
            <h1 style="color:#3498db; margin:0; font-size:3em;">{visibility:.1f}</h1>
            <p style="color:#3498db;">Cross-source signal strength</p>
        </div>
        """, unsafe_allow_html=True)

    # ─── Feature Impact ───
    st.markdown("---")
    st.subheader("🔍 Top Factors Driving Success")

    import plotly.express as px
    sorted_imp = sorted(feature_importances.items(), key=lambda x: -x[1])[:12]
    fig = px.bar(
        x=[v for _, v in sorted_imp],
        y=[k for k, _ in sorted_imp],
        orientation="h",
        color=[v for _, v in sorted_imp],
        color_continuous_scale="Blues",
    )
    fig.update_layout(
        height=400, xaxis_title="Importance", yaxis_title="",
        margin=dict(t=20, l=180), showlegend=False,
    )
    fig.update_coloraxes(showscale=False)
    st.plotly_chart(fig, use_container_width=True)

    # ─── Recommendations ───
    st.subheader("💡 Recommendations")
    recs = []
    if not has_github:
        recs.append("🔧 Create a GitHub presence — companies with GitHub have higher visibility")
    if not is_hiring:
        recs.append("👥 Start hiring — it signals growth and correlates with success")
    if not has_ph:
        recs.append("🚀 Launch on ProductHunt — it boosts visibility significantly")
    if desc_length < 200:
        recs.append("📝 Write a longer, more detailed company description")
    if team_size < 5:
        recs.append("📈 Growing your team beyond 5 correlates with higher success rates")
    if not is_ai and not is_saas:
        recs.append("🤖 Consider AI/SaaS positioning — these tags correlate with higher traction")
    if github_stars < 100 and has_github:
        recs.append("⭐ Focus on growing GitHub stars — open source traction is a strong signal")

    if recs:
        for rec in recs:
            st.markdown(f"- {rec}")
    else:
        st.success("This startup profile looks strong across all dimensions!")