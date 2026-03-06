import streamlit as st
import json
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
from collections import Counter

st.set_page_config(page_title="Sector Analysis", page_icon="🔥", layout="wide")

PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data" / "processed"
MODELS_DIR = PROJECT_ROOT / "data" / "models"

@st.cache_data
def load_data():
    with open(DATA_DIR / "master_companies.json", encoding="utf-8") as f:
        return json.load(f)

@st.cache_data
def load_clusters():
    path = MODELS_DIR / "model2_sector_clusters.json"
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return {}

companies = load_data()
cluster_data = load_clusters()

st.title("🔥 Sector & Industry Analysis")
st.markdown("---")

# ─── Build sector stats ───
sector_stats = {}
for c in companies:
    ind = c.get("industry", "") or "Unknown"
    if ind not in sector_stats:
        sector_stats[ind] = {
            "total": 0, "active": 0, "inactive": 0, "acquired": 0, "public": 0,
            "hiring": 0, "github": 0, "stars": 0, "ph": 0, "ph_votes": 0,
            "recent": 0, "team_sizes": [], "ages": [], "ai_count": 0,
        }
    s = sector_stats[ind]
    s["total"] += 1
    s["active"] += c.get("is_active", 0)
    s["inactive"] += c.get("is_dead", 0)
    s["acquired"] += c.get("is_acquired", 0)
    s["public"] += c.get("is_public", 0)
    s["hiring"] += 1 if c.get("is_hiring") else 0
    s["github"] += 1 if c.get("has_github") else 0
    s["stars"] += c.get("total_github_stars", 0) or 0
    s["ph"] += 1 if c.get("has_producthunt") else 0
    s["ph_votes"] += c.get("ph_votes", 0) or 0
    s["recent"] += c.get("is_recent_batch", 0)
    s["ai_count"] += c.get("is_ai", 0)
    ts = c.get("team_size", 0) or 0
    if ts > 0:
        s["team_sizes"].append(ts)
    age = c.get("company_age_years", 0) or 0
    if age > 0:
        s["ages"].append(age)

# ═══════════════════════════════════════════
# ROW 1: Sector Comparison
# ═══════════════════════════════════════════
st.subheader("📊 Sector Performance Comparison")

sectors_for_chart = {k: v for k, v in sector_stats.items() if v["total"] >= 10}

sector_names = list(sectors_for_chart.keys())
success_rates = [(s["active"] + s["acquired"] + s["public"]) / s["total"] * 100
                 for s in sectors_for_chart.values()]
failure_rates = [s["inactive"] / s["total"] * 100 for s in sectors_for_chart.values()]
totals = [s["total"] for s in sectors_for_chart.values()]

fig = go.Figure()
fig.add_trace(go.Bar(name="Success %", x=sector_names, y=success_rates,
                     marker_color="#2ecc71", text=[f"{r:.0f}%" for r in success_rates],
                     textposition="auto"))
fig.add_trace(go.Bar(name="Failure %", x=sector_names, y=failure_rates,
                     marker_color="#e74c3c", text=[f"{r:.0f}%" for r in failure_rates],
                     textposition="auto"))
fig.update_layout(barmode="group", height=450, yaxis_title="Percentage",
                  margin=dict(t=20, b=20), legend=dict(x=0.01, y=0.99))
st.plotly_chart(fig, use_container_width=True)

# ═══════════════════════════════════════════
# ROW 2: Cluster Results
# ═══════════════════════════════════════════
st.markdown("---")
st.subheader("🎯 Sector Classification (ML Clustering)")

cluster_profiles = cluster_data.get("cluster_profiles", {})
if cluster_profiles:
    cols = st.columns(len(cluster_profiles))
    colors = {"RISING/HOT": "🔥", "STABLE": "✅", "DECLINING": "📉"}

    for i, (label, profile) in enumerate(cluster_profiles.items()):
        with cols[i]:
            emoji = colors.get(label, "📊")
            st.markdown(f"### {emoji} {label}")
            sectors = profile.get("sectors", [])
            st.markdown(f"**Sectors:** {', '.join(sectors)}")
            means = profile.get("means", {})
            st.metric("Success Rate", f"{means.get('Success Rate %', 0):.1f}%")
            st.metric("Hiring Rate", f"{means.get('Hiring Rate %', 0):.1f}%")
            st.metric("Recent Batch %", f"{means.get('Recent Batch %', 0):.1f}%")
            st.metric("Avg Visibility", f"{means.get('Avg Visibility', 0):.1f}")
else:
    st.info("Cluster data not available. Run Model 2 in Jupyter first.")

# ═══════════════════════════════════════════
# ROW 3: Radar Chart
# ═══════════════════════════════════════════
st.markdown("---")
st.subheader("🕸️ Sector Radar Comparison")

selected_sectors = st.multiselect(
    "Select sectors to compare:",
    options=sorted(sectors_for_chart.keys()),
    default=sorted(sectors_for_chart.keys())[:3],
)

if selected_sectors:
    categories = ["Success Rate", "Hiring Rate", "GitHub Adoption", "PH Presence", "Recent %", "Avg Team"]
    fig = go.Figure()

    for sector in selected_sectors:
        s = sectors_for_chart[sector]
        total = s["total"]
        avg_team = sum(s["team_sizes"]) / len(s["team_sizes"]) if s["team_sizes"] else 0
        values = [
            (s["active"] + s["acquired"] + s["public"]) / total * 100,
            s["hiring"] / total * 100,
            s["github"] / total * 100,
            s["ph"] / total * 100,
            s["recent"] / total * 100,
            min(avg_team, 100),  # cap for viz
        ]
        fig.add_trace(go.Scatterpolar(r=values, theta=categories, fill="toself", name=sector))

    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        height=500, margin=dict(t=40, b=40),
    )
    st.plotly_chart(fig, use_container_width=True)

# ═══════════════════════════════════════════
# ROW 4: Detailed Sector Table
# ═══════════════════════════════════════════
st.markdown("---")
st.subheader("📋 Detailed Sector Metrics")

table = []
for name, s in sorted(sector_stats.items(), key=lambda x: -x[1]["total"]):
    if s["total"] < 5:
        continue
    total = s["total"]
    avg_team = sum(s["team_sizes"]) / len(s["team_sizes"]) if s["team_sizes"] else 0
    table.append({
        "Industry": name,
        "Companies": total,
        "Success Rate": f"{(s['active']+s['acquired']+s['public'])/total*100:.1f}%",
        "Failure Rate": f"{s['inactive']/total*100:.1f}%",
        "Hiring": s["hiring"],
        "Avg Team Size": f"{avg_team:.0f}",
        "GitHub Orgs": s["github"],
        "Total Stars": f"{s['stars']:,}",
        "PH Products": s["ph"],
        "AI Companies": s["ai_count"],
        "Recent (2023+)": s["recent"],
    })

st.dataframe(table, use_container_width=True)

# ═══════════════════════════════════════════
# ROW 5: Sector Trends — Treemap
# ═══════════════════════════════════════════
st.markdown("---")
st.subheader("🗺️ Sector Treemap")

treemap_data = []
for name, s in sector_stats.items():
    if s["total"] >= 10:
        treemap_data.append({
            "sector": name,
            "count": s["total"],
            "success_rate": (s["active"] + s["acquired"] + s["public"]) / s["total"] * 100,
        })

if treemap_data:
    fig = px.treemap(
        treemap_data,
        path=["sector"],
        values="count",
        color="success_rate",
        color_continuous_scale="RdYlGn",
        range_color=[60, 100],
    )
    fig.update_layout(height=500, margin=dict(t=20, b=20))
    st.plotly_chart(fig, use_container_width=True)