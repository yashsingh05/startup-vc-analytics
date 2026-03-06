import streamlit as st
import json
import pickle
from pathlib import Path

# ─── Page Config ───
st.set_page_config(
    page_title="US Startup & VC Analytics Platform",
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Paths ───
PROJECT_ROOT = Path(__file__).parent
DATA_DIR = PROJECT_ROOT / "data" / "processed"
MODELS_DIR = PROJECT_ROOT / "data" / "models"
RAW_DIR = PROJECT_ROOT / "data" / "raw"

# ─── Load Data (cached) ───
@st.cache_data
def load_master_data():
    with open(DATA_DIR / "master_companies.json", encoding="utf-8") as f:
        return json.load(f)

@st.cache_data
def load_founders():
    path = RAW_DIR / "yc_directory" / "yc_founders_data.json"
    if path.exists():
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return {}

@st.cache_data
def load_model_results():
    results = {}
    for name in ["model1_success_classifier.json", "model2_sector_clusters.json",
                  "model3_founder_analysis.json", "model4_traction_predictor.json"]:
        path = MODELS_DIR / name
        if path.exists():
            with open(path) as f:
                results[name.replace(".json", "")] = json.load(f)
    return results

companies = load_master_data()
founders_data = load_founders()
model_results = load_model_results()

# ─── Sidebar ───
st.sidebar.title("🚀 Startup Analytics")
st.sidebar.markdown("---")
st.sidebar.markdown("### Data Sources")
st.sidebar.markdown(f"- **YC Companies:** {len(companies):,}")

total_founders = sum(len(v.get("founders", [])) for v in founders_data.values())
st.sidebar.markdown(f"- **Founders:** {total_founders:,}")

# Count other sources
gh_count = sum(1 for c in companies if c.get("has_github"))
ph_count = sum(1 for c in companies if c.get("has_producthunt"))
sec_count = sum(1 for c in companies if c.get("has_sec_filing"))
news_count = sum(1 for c in companies if c.get("has_news_mention"))
st.sidebar.markdown(f"- **GitHub Linked:** {gh_count}")
st.sidebar.markdown(f"- **ProductHunt:** {ph_count}")
st.sidebar.markdown(f"- **SEC Filings:** {sec_count}")
st.sidebar.markdown(f"- **News Articles:** {news_count}")

st.sidebar.markdown("---")
st.sidebar.markdown("Built by **Yash Singh Thakur**")
st.sidebar.markdown("[GitHub](https://github.com/yashsingh05) | [LinkedIn](https://www.linkedin.com/in/yashsingh02)")

# ─── Main Content ───
st.title("🚀 US Startup & VC Analytics Platform")
st.markdown("*End-to-end data intelligence system built from 100% raw data — zero Kaggle*")
st.markdown("---")

# ─── KPI Row ───
col1, col2, col3, col4, col5 = st.columns(5)

total = len(companies)
active = sum(1 for c in companies if c.get("status") == "Active")
acquired = sum(1 for c in companies if c.get("status") == "Acquired")
public = sum(1 for c in companies if c.get("status") == "Public")
inactive = sum(1 for c in companies if c.get("status") == "Inactive")

col1.metric("Total Startups", f"{total:,}")
col2.metric("Active", f"{active:,}", f"{active/total*100:.0f}%")
col3.metric("Acquired", f"{acquired:,}", f"{acquired/total*100:.0f}%")
col4.metric("Public", f"{public:,}")
col5.metric("Inactive", f"{inactive:,}", f"-{inactive/total*100:.0f}%", delta_color="inverse")

st.markdown("---")

# ─── ML Model Performance ───
st.subheader("🤖 ML Model Performance")
m1, m2, m3, m4 = st.columns(4)

model1 = model_results.get("model1_success_classifier", {})
model3 = model_results.get("model3_founder_analysis", {})
model4 = model_results.get("model4_traction_predictor", {})

m1.metric("Success Classifier F1", f"{model1.get('f1_score', 0):.3f}")
m2.metric("Success Classifier AUC", f"{model1.get('auc_roc', 0):.3f}")
m3.metric("Founder Model F1", f"{model3.get('model_f1', 0):.3f}")
m4.metric("Traction Predictor Acc", f"{model4.get('accuracy', 0):.3f}")

st.markdown("---")

# ─── Quick Stats ───
st.subheader("📊 Ecosystem Overview")

col_a, col_b = st.columns(2)

with col_a:
    st.markdown("### Industry Breakdown")
    from collections import Counter
    ind_counts = Counter(c.get("industry", "Unknown") for c in companies if c.get("industry"))
    for ind, count in ind_counts.most_common(10):
        pct = count / total * 100
        st.markdown(f"**{ind}**: {count:,} ({pct:.1f}%)")

with col_b:
    st.markdown("### Status by Numbers")
    success_rate = (active + acquired + public) / total * 100
    st.markdown(f"**Overall Success Rate:** {success_rate:.1f}%")
    st.markdown(f"**Companies in 2+ data sources:** {sum(1 for c in companies if c.get('num_sources', 1) >= 2):,}")
    st.markdown(f"**Companies hiring:** {sum(1 for c in companies if c.get('is_hiring')):,}")
    st.markdown(f"**Top YC companies:** {sum(1 for c in companies if c.get('top_company')):,}")
    st.markdown(f"**Total GitHub Stars:** {sum(c.get('total_github_stars', 0) for c in companies):,}")
    st.markdown(f"**Total PH Votes:** {sum(c.get('ph_votes', 0) for c in companies):,}")

st.markdown("---")

# ─── Data Pipeline ───
st.subheader("🔧 Data Pipeline Architecture")
st.markdown("""
```
┌─────────────────────────────────────────────────────────┐
│                 5 RAW DATA SOURCES                       │
├──────────┬──────────┬───────────┬──────────┬────────────┤
│SEC EDGAR │ YC Dir.  │ProductHunt│GitHub API│ News APIs  │
│ 700 co.  │ 5,690 co.│ 1,740     │ 168 orgs │ 435 arts   │
└────┬─────┴────┬─────┴─────┬─────┴────┬─────┴──────┬─────┘
     │          │           │          │            │
     ▼          ▼           ▼          ▼            ▼
┌─────────────────────────────────────────────────────────┐
│     DATA CLEANING + ENTITY RESOLUTION + 63 FEATURES      │
└────────────────────────┬────────────────────────────────┘
                         ▼
┌─────────────────────────────────────────────────────────┐
│                    4 ML MODELS                           │
│  Success Classifier │ Sector Clusters │ Founder Analysis │
│                     │ Traction Predictor                 │
└─────────────────────────────────────────────────────────┘
```
""")

st.markdown("---")
st.markdown("👈 **Navigate using the sidebar** to explore sectors, founders, and predict startup success!")