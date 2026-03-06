import streamlit as st
import json
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
from collections import Counter

st.set_page_config(page_title="Ecosystem Overview", page_icon="📊", layout="wide")

PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data" / "processed"

@st.cache_data
def load_data():
    with open(DATA_DIR / "master_companies.json", encoding="utf-8") as f:
        return json.load(f)

companies = load_data()

st.title("📊 Startup Ecosystem Overview")
st.markdown("---")

# ═══════════════════════════════════════════
# ROW 1: Status Distribution + Industry
# ═══════════════════════════════════════════
col1, col2 = st.columns(2)

with col1:
    st.subheader("Company Status Distribution")
    status_counts = Counter(c.get("status", "Unknown") for c in companies)
    fig = px.pie(
        names=list(status_counts.keys()),
        values=list(status_counts.values()),
        color_discrete_sequence=px.colors.qualitative.Set2,
        hole=0.4,
    )
    fig.update_traces(textposition="inside", textinfo="percent+label+value")
    fig.update_layout(height=400, margin=dict(t=20, b=20, l=20, r=20))
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Top Industries")
    ind_counts = Counter(c.get("industry", "Unknown") for c in companies if c.get("industry"))
    top_ind = dict(ind_counts.most_common(10))
    fig = px.bar(
        x=list(top_ind.values()),
        y=list(top_ind.keys()),
        orientation="h",
        color=list(top_ind.values()),
        color_continuous_scale="Viridis",
    )
    fig.update_layout(height=400, margin=dict(t=20, b=20), showlegend=False,
                      xaxis_title="Number of Companies", yaxis_title="")
    fig.update_coloraxes(showscale=False)
    st.plotly_chart(fig, use_container_width=True)

# ═══════════════════════════════════════════
# ROW 2: Batch Trends Over Time
# ═══════════════════════════════════════════
st.markdown("---")
st.subheader("📈 YC Batch Size Over Time")

batch_counts = Counter(c.get("batch", "") for c in companies if c.get("batch"))
# Sort by year
sorted_batches = sorted(batch_counts.items(), key=lambda x: x[0])
batch_names = [b[0] for b in sorted_batches]
batch_values = [b[1] for b in sorted_batches]

fig = px.bar(
    x=batch_names, y=batch_values,
    color=batch_values,
    color_continuous_scale="Blues",
)
fig.update_layout(
    height=400,
    xaxis_title="Batch", yaxis_title="Companies",
    xaxis_tickangle=-45,
    margin=dict(t=20, b=80),
    showlegend=False,
)
fig.update_coloraxes(showscale=False)
st.plotly_chart(fig, use_container_width=True)

# ═══════════════════════════════════════════
# ROW 3: Success Rate by Batch Year
# ═══════════════════════════════════════════
st.markdown("---")
col3, col4 = st.columns(2)

with col3:
    st.subheader("Success Rate by Batch Year")
    year_stats = {}
    for c in companies:
        yr = c.get("batch_year_int", 0)
        if yr > 0:
            if yr not in year_stats:
                year_stats[yr] = {"total": 0, "success": 0}
            year_stats[yr]["total"] += 1
            year_stats[yr]["success"] += c.get("is_success", 0)

    years = sorted(year_stats.keys())
    rates = [year_stats[y]["success"] / year_stats[y]["total"] * 100 for y in years]
    totals = [year_stats[y]["total"] for y in years]

    fig = go.Figure()
    fig.add_trace(go.Bar(x=years, y=totals, name="Total Companies", opacity=0.3, yaxis="y"))
    fig.add_trace(go.Scatter(x=years, y=rates, name="Success Rate %", yaxis="y2",
                             line=dict(color="red", width=3), mode="lines+markers"))
    fig.update_layout(
        height=400,
        yaxis=dict(title="Companies", side="left"),
        yaxis2=dict(title="Success Rate %", side="right", overlaying="y", range=[0, 100]),
        legend=dict(x=0.01, y=0.99),
        margin=dict(t=20, b=20),
    )
    st.plotly_chart(fig, use_container_width=True)

with col4:
    st.subheader("Team Size Distribution")
    team_sizes = [c.get("team_size", 0) for c in companies if c.get("team_size", 0) > 0]
    # Cap at 200 for visualization
    team_sizes_capped = [min(t, 200) for t in team_sizes]
    fig = px.histogram(
        x=team_sizes_capped,
        nbins=50,
        color_discrete_sequence=["#636EFA"],
    )
    fig.update_layout(
        height=400,
        xaxis_title="Team Size (capped at 200)",
        yaxis_title="Number of Companies",
        margin=dict(t=20, b=20),
    )
    st.plotly_chart(fig, use_container_width=True)

# ═══════════════════════════════════════════
# ROW 4: Cross-Source Analysis
# ═══════════════════════════════════════════
st.markdown("---")
st.subheader("🔗 Cross-Source Data Coverage")

source_labels = ["YC Only", "2 Sources", "3 Sources", "4 Sources", "5 Sources"]
source_counts_list = [
    sum(1 for c in companies if c.get("num_sources", 1) == 1),
    sum(1 for c in companies if c.get("num_sources", 1) == 2),
    sum(1 for c in companies if c.get("num_sources", 1) == 3),
    sum(1 for c in companies if c.get("num_sources", 1) == 4),
    sum(1 for c in companies if c.get("num_sources", 1) == 5),
]

col5, col6 = st.columns(2)

with col5:
    fig = px.bar(
        x=source_labels, y=source_counts_list,
        color=source_counts_list,
        color_continuous_scale="Oranges",
    )
    fig.update_layout(height=350, xaxis_title="Data Sources", yaxis_title="Companies",
                      margin=dict(t=20), showlegend=False)
    fig.update_coloraxes(showscale=False)
    st.plotly_chart(fig, use_container_width=True)

with col6:
    # Source breakdown
    sources = {
        "GitHub": sum(1 for c in companies if c.get("has_github")),
        "ProductHunt": sum(1 for c in companies if c.get("has_producthunt")),
        "SEC EDGAR": sum(1 for c in companies if c.get("has_sec_filing")),
        "News": sum(1 for c in companies if c.get("has_news_mention")),
    }
    fig = px.bar(
        x=list(sources.keys()), y=list(sources.values()),
        color=list(sources.keys()),
        color_discrete_sequence=px.colors.qualitative.Bold,
    )
    fig.update_layout(height=350, xaxis_title="Source", yaxis_title="Companies Matched",
                      margin=dict(t=20), showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

# ═══════════════════════════════════════════
# ROW 5: Top Companies Table
# ═══════════════════════════════════════════
st.markdown("---")
st.subheader("⭐ Top Companies by Visibility Score")

top = sorted(companies, key=lambda x: x.get("visibility_score", 0), reverse=True)[:20]
table_data = []
for c in top:
    table_data.append({
        "Company": c.get("name", ""),
        "Status": c.get("status", ""),
        "Industry": c.get("industry", ""),
        "Batch": c.get("batch", ""),
        "Team Size": c.get("team_size", 0),
        "GitHub Stars": f"{c.get('total_github_stars', 0):,}",
        "PH Votes": c.get("ph_votes", 0),
        "Visibility": round(c.get("visibility_score", 0), 1),
    })

st.dataframe(table_data, use_container_width=True, height=500)