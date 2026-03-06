import streamlit as st
import json
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
from collections import Counter

st.set_page_config(page_title="Founder Insights", page_icon="👤", layout="wide")

PROJECT_ROOT = Path(__file__).parent.parent
RAW_DIR = PROJECT_ROOT / "data" / "raw"
MODELS_DIR = PROJECT_ROOT / "data" / "models"

@st.cache_data
def load_founders():
    path = RAW_DIR / "yc_directory" / "yc_founders_data.json"
    if path.exists():
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return {}

@st.cache_data
def load_model3():
    path = MODELS_DIR / "model3_founder_analysis.json"
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return {}

founders_raw = load_founders()
model3 = load_model3()

st.title("👤 Founder Insights & Analysis")
st.markdown(f"*Analyzing founders from {len(founders_raw):,} YC companies*")
st.markdown("---")

# ─── Parse all founders ───
all_founders = []
company_stats = []

for slug, data in founders_raw.items():
    founders = data.get("founders", [])
    status = data.get("status", "Unknown")
    is_success = 1 if status in ("Active", "Acquired", "Public") else 0
    industry = data.get("industry", "Unknown") or "Unknown"
    num_f = len(founders)

    has_tech = False
    has_ceo = False
    has_cto = False
    li_count = 0

    for f in founders:
        title = (f.get("title", "") or "").lower()
        if any(t in title for t in ["cto", "engineer", "technical"]):
            has_tech = True
        if "cto" in title:
            has_cto = True
        if any(t in title for t in ["ceo", "chief executive"]):
            has_ceo = True
        if f.get("linkedin_url"):
            li_count += 1

        all_founders.append({
            "name": f.get("full_name", ""),
            "title": f.get("title", ""),
            "is_success": is_success,
            "industry": industry,
            "status": status,
        })

    company_stats.append({
        "name": data.get("company_name", ""),
        "status": status,
        "is_success": is_success,
        "industry": industry,
        "num_founders": num_f,
        "has_tech": has_tech,
        "has_ceo": has_ceo,
        "has_cto": has_cto,
        "all_linkedin": li_count == num_f and num_f > 0,
    })

total_founders = len(all_founders)

# ═══════════════════════════════════════════
# KPIs
# ═══════════════════════════════════════════
c1, c2, c3, c4 = st.columns(4)
c1.metric("Total Founders", f"{total_founders:,}")
c2.metric("Avg per Company", f"{total_founders/len(company_stats):.1f}")
c3.metric("With Tech Founder", f"{sum(1 for c in company_stats if c['has_tech']):,}")
c4.metric("CEO + CTO Combo", f"{sum(1 for c in company_stats if c['has_ceo'] and c['has_cto']):,}")

st.markdown("---")

# ═══════════════════════════════════════════
# ROW 1: Founder Count vs Success
# ═══════════════════════════════════════════
col1, col2 = st.columns(2)

with col1:
    st.subheader("Founder Count vs Success Rate")
    fc = {}
    for cs in company_stats:
        n = min(cs["num_founders"], 5)
        key = str(n) if n < 5 else "5+"
        if key not in fc:
            fc[key] = {"total": 0, "success": 0}
        fc[key]["total"] += 1
        fc[key]["success"] += cs["is_success"]

    labels = sorted(fc.keys())
    rates = [fc[k]["success"] / fc[k]["total"] * 100 for k in labels]
    counts = [fc[k]["total"] for k in labels]

    fig = go.Figure()
    fig.add_trace(go.Bar(x=labels, y=counts, name="Companies", opacity=0.3, yaxis="y"))
    fig.add_trace(go.Scatter(x=labels, y=rates, name="Success Rate %", yaxis="y2",
                             line=dict(color="red", width=3), mode="lines+markers",
                             marker=dict(size=10)))
    fig.update_layout(
        height=400,
        yaxis=dict(title="Companies", side="left"),
        yaxis2=dict(title="Success Rate %", side="right", overlaying="y", range=[0, 100]),
        xaxis_title="Number of Founders",
        margin=dict(t=20, b=20),
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Technical Founder Impact")
    tech_data = [
        {"Group": "With Tech Founder",
         "Success Rate": sum(c["is_success"] for c in company_stats if c["has_tech"]) / max(sum(1 for c in company_stats if c["has_tech"]), 1) * 100,
         "Count": sum(1 for c in company_stats if c["has_tech"])},
        {"Group": "Without Tech Founder",
         "Success Rate": sum(c["is_success"] for c in company_stats if not c["has_tech"]) / max(sum(1 for c in company_stats if not c["has_tech"]), 1) * 100,
         "Count": sum(1 for c in company_stats if not c["has_tech"])},
    ]
    fig = px.bar(
        tech_data, x="Group", y="Success Rate",
        color="Group",
        color_discrete_sequence=["#2ecc71", "#e74c3c"],
        text=[f"{d['Success Rate']:.1f}%" for d in tech_data],
    )
    fig.update_layout(height=400, margin=dict(t=20, b=20), showlegend=False,
                      yaxis_range=[0, 100], yaxis_title="Success Rate %")
    st.plotly_chart(fig, use_container_width=True)

# ═══════════════════════════════════════════
# ROW 2: Archetypes
# ═══════════════════════════════════════════
st.markdown("---")
st.subheader("🧬 Founder Archetypes")

archetypes = {
    "Solo Technical": lambda c: c["num_founders"] == 1 and c["has_tech"],
    "Solo Non-Tech": lambda c: c["num_founders"] == 1 and not c["has_tech"],
    "Duo with Tech": lambda c: c["num_founders"] == 2 and c["has_tech"],
    "Duo no Tech": lambda c: c["num_founders"] == 2 and not c["has_tech"],
    "Team 3+ with Tech": lambda c: c["num_founders"] >= 3 and c["has_tech"],
    "Team 3+ no Tech": lambda c: c["num_founders"] >= 3 and not c["has_tech"],
}

arch_data = []
for label, filt in archetypes.items():
    matches = [c for c in company_stats if filt(c)]
    if matches:
        rate = sum(c["is_success"] for c in matches) / len(matches) * 100
        arch_data.append({"Archetype": label, "Success Rate": rate, "Count": len(matches)})

if arch_data:
    fig = px.bar(
        arch_data, x="Archetype", y="Success Rate",
        color="Success Rate", color_continuous_scale="RdYlGn",
        range_color=[60, 100],
        text=[f"{d['Success Rate']:.1f}%\n({d['Count']})" for d in arch_data],
    )
    fig.update_layout(height=450, margin=dict(t=20, b=20), yaxis_range=[0, 100],
                      yaxis_title="Success Rate %")
    fig.update_coloraxes(showscale=False)
    st.plotly_chart(fig, use_container_width=True)

# ═══════════════════════════════════════════
# ROW 3: Leadership + Top Titles
# ═══════════════════════════════════════════
st.markdown("---")
col3, col4 = st.columns(2)

with col3:
    st.subheader("Leadership Structure")
    leadership = {
        "CEO + CTO": lambda c: c["has_ceo"] and c["has_cto"],
        "CEO only": lambda c: c["has_ceo"] and not c["has_cto"],
        "CTO only": lambda c: not c["has_ceo"] and c["has_cto"],
        "Neither": lambda c: not c["has_ceo"] and not c["has_cto"],
    }
    lead_data = []
    for label, filt in leadership.items():
        matches = [c for c in company_stats if filt(c)]
        if matches:
            rate = sum(c["is_success"] for c in matches) / len(matches) * 100
            lead_data.append({"Structure": label, "Success Rate": rate, "Count": len(matches)})

    fig = px.bar(lead_data, x="Structure", y="Success Rate",
                 color="Success Rate", color_continuous_scale="RdYlGn", range_color=[70, 90],
                 text=[f"{d['Success Rate']:.1f}%" for d in lead_data])
    fig.update_layout(height=400, yaxis_range=[0, 100], margin=dict(t=20))
    fig.update_coloraxes(showscale=False)
    st.plotly_chart(fig, use_container_width=True)

with col4:
    st.subheader("Most Common Titles")
    title_counts = Counter(f["title"] for f in all_founders if f["title"])
    top_titles = dict(title_counts.most_common(12))
    fig = px.bar(
        x=list(top_titles.values()), y=list(top_titles.keys()),
        orientation="h", color_discrete_sequence=["#9b59b6"],
    )
    fig.update_layout(height=400, xaxis_title="Count", yaxis_title="",
                      margin=dict(t=20, b=20))
    st.plotly_chart(fig, use_container_width=True)

# ═══════════════════════════════════════════
# ROW 4: Industry × Founders
# ═══════════════════════════════════════════
st.markdown("---")
st.subheader("Founders by Industry")

ind_f = {}
for cs in company_stats:
    ind = cs["industry"]
    if ind not in ind_f:
        ind_f[ind] = {"total_f": 0, "count": 0, "tech": 0}
    ind_f[ind]["total_f"] += cs["num_founders"]
    ind_f[ind]["count"] += 1
    ind_f[ind]["tech"] += 1 if cs["has_tech"] else 0

ind_table = []
for ind, s in sorted(ind_f.items(), key=lambda x: -x[1]["count"]):
    if s["count"] >= 10:
        ind_table.append({
            "Industry": ind,
            "Companies": s["count"],
            "Avg Founders": round(s["total_f"] / s["count"], 1),
            "% with Tech Founder": f"{s['tech']/s['count']*100:.0f}%",
        })

st.dataframe(ind_table, use_container_width=True)