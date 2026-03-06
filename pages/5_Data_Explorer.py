import streamlit as st
import json
import plotly.express as px
from pathlib import Path
from collections import Counter

st.set_page_config(page_title="Data Explorer", page_icon="🔍", layout="wide")

PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data" / "processed"
RAW_DIR = PROJECT_ROOT / "data" / "raw"

@st.cache_data
def load_data():
    with open(DATA_DIR / "master_companies.json", encoding="utf-8") as f:
        return json.load(f)

@st.cache_data
def load_founders():
    path = RAW_DIR / "yc_directory" / "yc_founders_data.json"
    if path.exists():
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    return {}

companies = load_data()
founders_data = load_founders()

st.title("🔍 Data Explorer")
st.markdown("*Search, filter, and browse all companies in the dataset*")
st.markdown("---")

# ═══════════════════════════════════════════
# FILTERS
# ═══════════════════════════════════════════
st.subheader("Filters")

fc1, fc2, fc3, fc4 = st.columns(4)

with fc1:
    search = st.text_input("Search company name", "")

with fc2:
    industries = sorted(set(c.get("industry", "Unknown") for c in companies if c.get("industry")))
    selected_industry = st.selectbox("Industry", ["All"] + industries)

with fc3:
    statuses = sorted(set(c.get("status", "Unknown") for c in companies))
    selected_status = st.selectbox("Status", ["All"] + statuses)

with fc4:
    batches = sorted(set(c.get("batch", "") for c in companies if c.get("batch")), reverse=True)
    selected_batch = st.selectbox("Batch", ["All"] + batches)

fc5, fc6, fc7, fc8 = st.columns(4)

with fc5:
    min_team = st.number_input("Min team size", 0, 50000, 0)

with fc6:
    has_github_filter = st.selectbox("GitHub", ["Any", "Yes", "No"])

with fc7:
    has_ph_filter = st.selectbox("ProductHunt", ["Any", "Yes", "No"])

with fc8:
    sort_by = st.selectbox("Sort by", [
        "Visibility Score", "Team Size", "GitHub Stars", "PH Votes",
        "Company Name", "Batch (newest)", "Batch (oldest)"
    ])

# ═══════════════════════════════════════════
# APPLY FILTERS
# ═══════════════════════════════════════════
filtered = companies.copy()

if search:
    filtered = [c for c in filtered if search.lower() in c.get("name", "").lower()]

if selected_industry != "All":
    filtered = [c for c in filtered if c.get("industry") == selected_industry]

if selected_status != "All":
    filtered = [c for c in filtered if c.get("status") == selected_status]

if selected_batch != "All":
    filtered = [c for c in filtered if c.get("batch") == selected_batch]

if min_team > 0:
    filtered = [c for c in filtered if (c.get("team_size") or 0) >= min_team]

if has_github_filter == "Yes":
    filtered = [c for c in filtered if c.get("has_github")]
elif has_github_filter == "No":
    filtered = [c for c in filtered if not c.get("has_github")]

if has_ph_filter == "Yes":
    filtered = [c for c in filtered if c.get("has_producthunt")]
elif has_ph_filter == "No":
    filtered = [c for c in filtered if not c.get("has_producthunt")]

# Sort
sort_map = {
    "Visibility Score": lambda c: -(c.get("visibility_score") or 0),
    "Team Size": lambda c: -(c.get("team_size") or 0),
    "GitHub Stars": lambda c: -(c.get("total_github_stars") or 0),
    "PH Votes": lambda c: -(c.get("ph_votes") or 0),
    "Company Name": lambda c: c.get("name", "").lower(),
    "Batch (newest)": lambda c: -(c.get("batch_year_int") or 0),
    "Batch (oldest)": lambda c: c.get("batch_year_int") or 9999,
}
filtered.sort(key=sort_map.get(sort_by, lambda c: 0))

st.markdown("---")
st.markdown(f"**Showing {len(filtered):,} of {len(companies):,} companies**")

# ═══════════════════════════════════════════
# FILTERED STATS
# ═══════════════════════════════════════════
if filtered:
    s1, s2, s3, s4, s5 = st.columns(5)
    active = sum(1 for c in filtered if c.get("status") == "Active")
    s1.metric("Filtered", f"{len(filtered):,}")
    s2.metric("Active", f"{active}")
    success = sum(1 for c in filtered if c.get("is_success"))
    s3.metric("Success Rate", f"{success/len(filtered)*100:.1f}%")
    avg_team = sum(c.get("team_size", 0) or 0 for c in filtered) / len(filtered)
    s4.metric("Avg Team", f"{avg_team:.0f}")
    total_stars = sum(c.get("total_github_stars", 0) or 0 for c in filtered)
    s5.metric("Total GH Stars", f"{total_stars:,}")

st.markdown("---")

# ═══════════════════════════════════════════
# QUICK CHARTS FOR FILTERED DATA
# ═══════════════════════════════════════════
if len(filtered) > 1:
    ch1, ch2 = st.columns(2)

    with ch1:
        st.subheader("Status Breakdown (Filtered)")
        status_counts = Counter(c.get("status", "Unknown") for c in filtered)
        fig = px.pie(names=list(status_counts.keys()), values=list(status_counts.values()),
                     color_discrete_sequence=px.colors.qualitative.Set2, hole=0.4)
        fig.update_layout(height=300, margin=dict(t=10, b=10, l=10, r=10))
        st.plotly_chart(fig, use_container_width=True)

    with ch2:
        st.subheader("Industry Breakdown (Filtered)")
        ind_counts = Counter(c.get("industry", "Unknown") for c in filtered if c.get("industry"))
        top_5 = dict(ind_counts.most_common(7))
        fig = px.bar(x=list(top_5.keys()), y=list(top_5.values()),
                     color_discrete_sequence=["#636EFA"])
        fig.update_layout(height=300, margin=dict(t=10, b=10), xaxis_title="", yaxis_title="Count")
        st.plotly_chart(fig, use_container_width=True)

st.markdown("---")

# ═══════════════════════════════════════════
# RESULTS TABLE
# ═══════════════════════════════════════════
st.subheader("Companies")

page_size = 25
total_pages = max(1, (len(filtered) + page_size - 1) // page_size)
page = st.number_input("Page", min_value=1, max_value=total_pages, value=1)
start_idx = (page - 1) * page_size
end_idx = start_idx + page_size

table_data = []
for c in filtered[start_idx:end_idx]:
    slug = c.get("slug", "")
    founders = founders_data.get(slug, {}).get("founders", [])
    founder_names = ", ".join(f.get("full_name", "") for f in founders[:3])
    if len(founders) > 3:
        founder_names += f" +{len(founders)-3} more"

    table_data.append({
        "Company": c.get("name", ""),
        "Status": c.get("status", ""),
        "Industry": c.get("industry", ""),
        "Batch": c.get("batch", ""),
        "Team": c.get("team_size", 0) or 0,
        "GH Stars": c.get("total_github_stars", 0) or 0,
        "PH Votes": c.get("ph_votes", 0) or 0,
        "Visibility": round(c.get("visibility_score", 0) or 0, 1),
        "Founders": founder_names,
    })

st.dataframe(table_data, use_container_width=True, height=600)
st.markdown(f"Page {page} of {total_pages}")

# ═══════════════════════════════════════════
# COMPANY DETAIL VIEW
# ═══════════════════════════════════════════
st.markdown("---")
st.subheader("🏢 Company Detail View")

company_names = [c.get("name", "") for c in filtered[:500]]
selected_company = st.selectbox("Select a company to view details", [""] + company_names)

if selected_company:
    comp = next((c for c in filtered if c.get("name") == selected_company), None)
    if comp:
        d1, d2 = st.columns(2)
        with d1:
            st.markdown(f"### {comp.get('name', '')}")
            st.markdown(f"**Status:** {comp.get('status', '')}")
            st.markdown(f"**Industry:** {comp.get('industry', '')}")
            st.markdown(f"**Batch:** {comp.get('batch', '')}")
            st.markdown(f"**Team Size:** {comp.get('team_size', 'N/A')}")
            st.markdown(f"**Stage:** {comp.get('stage', 'N/A')}")
            website = comp.get("website", "")
            if website:
                st.markdown(f"**Website:** [{website}]({website})")
            yc_url = comp.get("yc_url", "")
            if yc_url:
                st.markdown(f"**YC Profile:** [{yc_url}]({yc_url})")

        with d2:
            st.markdown("### Signals")
            st.markdown(f"**Visibility Score:** {comp.get('visibility_score', 0):.1f}")
            st.markdown(f"**GitHub Stars:** {comp.get('total_github_stars', 0):,}")
            st.markdown(f"**PH Votes:** {comp.get('ph_votes', 0)}")
            st.markdown(f"**News Mentions:** {comp.get('news_mention_count', 0)}")
            st.markdown(f"**Data Sources:** {comp.get('num_sources', 1)}")
            if comp.get("is_hiring"):
                st.markdown("**Hiring:** Yes")
            if comp.get("top_company"):
                st.markdown("**YC Top Company:** Yes")

        # One liner / description
        one_liner = comp.get("one_liner", "")
        desc = comp.get("description", "")
        if one_liner:
            st.markdown(f"**One-liner:** {one_liner}")
        if desc:
            with st.expander("Full Description"):
                st.write(desc)

        # Founders
        slug = comp.get("slug", "")
        founders = founders_data.get(slug, {}).get("founders", [])
        if founders:
            st.markdown("### Founders")
            for f in founders:
                name = f.get("full_name", "")
                title = f.get("title", "")
                li = f.get("linkedin_url", "")
                bio = f.get("founder_bio", "")
                line = f"**{name}** — {title}"
                if li:
                    line += f" | [LinkedIn]({li})"
                st.markdown(line)
                if bio:
                    st.markdown(f"_{bio[:300]}_")

# ═══════════════════════════════════════════
# DOWNLOAD
# ═══════════════════════════════════════════
st.markdown("---")
st.subheader("📥 Export Data")

if st.button("Generate CSV for filtered companies"):
    import csv
    import io

    output = io.StringIO()
    fields = ["Company", "Status", "Industry", "Batch", "Team Size",
              "GitHub Stars", "PH Votes", "Visibility Score", "Website"]
    writer = csv.DictWriter(output, fieldnames=fields)
    writer.writeheader()
    for c in filtered:
        writer.writerow({
            "Company": c.get("name", ""),
            "Status": c.get("status", ""),
            "Industry": c.get("industry", ""),
            "Batch": c.get("batch", ""),
            "Team Size": c.get("team_size", 0),
            "GitHub Stars": c.get("total_github_stars", 0),
            "PH Votes": c.get("ph_votes", 0),
            "Visibility Score": round(c.get("visibility_score", 0), 1),
            "Website": c.get("website", ""),
        })

    st.download_button(
        label="Download CSV",
        data=output.getvalue(),
        file_name="filtered_startups.csv",
        mime="text/csv",
    )