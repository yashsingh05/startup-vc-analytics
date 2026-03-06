# 🚀 US Startup & VC Analytics Platform

An end-to-end data intelligence platform analyzing **5,690+ Y Combinator startups** with data collected from **5 raw sources** — zero pre-made datasets. Features 4 ML models, interactive dashboards, and a startup success prediction tool.

🔗 **[Live Demo on Streamlit Cloud](#)** | 📊 **[Portfolio](https://yashsingh05.github.io/yashsingh.github.io/)** | 💼 **[LinkedIn](https://www.linkedin.com/in/yashsingh02)**

---

## 📌 Project Highlights

| Metric | Value |
|--------|-------|
| Companies Analyzed | 5,690+ |
| Raw Data Sources | 5 (SEC EDGAR, YC, ProductHunt, GitHub, News APIs) |
| Founders Scraped | 13,000+ from individual YC company pages |
| Features Engineered | 63 per company |
| ML Models Built | 4 (Success Classifier, Sector Clustering, Founder Analysis, Traction Predictor) |
| Best Model F1 Score | 0.88 (XGBoost Success Classifier) |
| Cross-Source Matches | 619 companies matched across 2+ sources |
| Deployment | Streamlit Cloud |

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    DATA COLLECTION LAYER                     │
├──────────┬──────────┬───────────┬───────────┬──────────────┤
│ SEC EDGAR│ YC Dir.  │ProductHunt│ GitHub API│ News APIs    │
│  700 co. │5,690 co. │ 1,740     │ 168 orgs  │ 435 articles │
└────┬─────┴────┬─────┴─────┬─────┴─────┬─────┴──────┬───────┘
     │          │           │           │            │
     ▼          ▼           ▼           ▼            ▼
┌─────────────────────────────────────────────────────────────┐
│         DATA CLEANING + ENTITY RESOLUTION (fuzzy matching)   │
│         63 engineered features per company                   │
└──────────────────────────┬──────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                      4 ML MODELS                             │
│  ┌──────────────┐ ┌──────────────┐ ┌────────────────────┐   │
│  │Success       │ │Hot Sector    │ │Founder Background  │   │
│  │Classifier    │ │Identifier    │ │Analyzer            │   │
│  │(XGBoost)     │ │(K-Means)     │ │(Random Forest)     │   │
│  │F1: 0.88      │ │3 Clusters    │ │5,621 companies     │   │
│  └──────────────┘ └──────────────┘ └────────────────────┘   │
│  ┌──────────────────────────────────────────────────────┐   │
│  │Traction Predictor (Gradient Boosting) — Acc: 91.4%   │   │
│  └──────────────────────────────────────────────────────┘   │
└──────────────────────────┬──────────────────────────────────┘
                           ▼
┌─────────────────────────────────────────────────────────────┐
│              STREAMLIT APP (6 Interactive Pages)              │
│  Home │ Ecosystem │ Sectors │ Founders │ Scorer │ Explorer   │
└─────────────────────────────────────────────────────────────┘
```

---

## 📊 Key Findings

### Startup Success Patterns
- **B2B startups** have the highest success rate (85.3%) compared to Consumer (64.7%)
- **Healthcare and Fintech** sectors outperform with 86%+ success rates
- Companies with **GitHub presence** show significantly higher visibility and traction
- **YC batch size** has been growing rapidly — Winter 2022 had 399 companies

### Founder Insights
- **Duo teams with a technical co-founder** have the optimal success profile
- Companies with a **CEO + CTO combination** show higher success rates
- **LinkedIn presence** among founders correlates with company success

### Technology Trends
- **TypeScript** is the #1 language across YC startup repos (261 repos)
- **Python** is #2 (222 repos), followed by JavaScript, Go, and Rust
- **Ollama** leads with 177K+ GitHub stars among YC companies

---

## 🛠️ Tech Stack

| Layer | Tools |
|-------|-------|
| **Data Collection** | Python, Requests, BeautifulSoup, Selenium |
| **APIs Used** | SEC EDGAR, YC Directory, ProductHunt GraphQL, GitHub REST, NewsAPI |
| **Data Processing** | pandas, numpy, fuzzywuzzy (entity resolution) |
| **ML Modeling** | scikit-learn, XGBoost, SHAP |
| **Visualization** | Plotly, Streamlit |
| **Deployment** | Streamlit Cloud |

---

## 📁 Project Structure

```
startup_vc_analytics/
├── Home.py                          # Streamlit main page
├── pages/
│   ├── 1_Ecosystem.py               # Ecosystem dashboard
│   ├── 2_Sectors.py                 # Sector analysis + clustering
│   ├── 3_Founders.py                # Founder insights
│   ├── 4_Startup_Scorer.py          # ML prediction tool
│   └── 5_Data_Explorer.py           # Search & browse companies
├── data/
│   ├── raw/                         # Raw data from 5 sources
│   │   ├── sec_edgar/               # SEC filings
│   │   ├── yc_directory/            # YC companies + founders
│   │   ├── producthunt/             # PH launches
│   │   ├── github/                  # GitHub org data
│   │   └── news/                    # News articles
│   ├── processed/                   # Cleaned master dataset
│   │   ├── master_companies.json    # 5,690 companies, 63 features
│   │   └── master_companies.csv     # Power BI compatible
│   └── models/                      # Trained ML models
├── notebooks/                       # Jupyter exploration notebooks
├── requirements.txt                 # Python dependencies
└── README.md
```

---

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- pip

### Installation

```bash
git clone https://github.com/yashsingh05/startup-vc-analytics.git
cd startup-vc-analytics
pip install -r requirements.txt
```

### Run the App
```bash
streamlit run Home.py
```

### Data Collection (Optional — to regenerate data)
Open the Jupyter notebooks in `notebooks/` and run them in order:
1. `01_sec_edgar_scraper.ipynb`
2. `02_yc_scraper.ipynb`
3. `03_producthunt_scraper.ipynb`
4. `04_github_scraper.ipynb`
5. `05_news_scraper.ipynb`
6. `06_data_cleaning.ipynb`
7. `07_ml_models.ipynb`

---

## 📈 ML Model Results

### Model 1: Startup Success Classifier
- **Algorithm:** XGBoost
- **F1 Score:** 0.881
- **AUC-ROC:** 0.865
- **Top Features:** company_age_years, team_size, visibility_score, batch_year

### Model 2: Hot Sector Identifier
- **Algorithm:** K-Means Clustering (K=3)
- **Clusters:** Rising/Hot, Stable, Declining
- **Sectors Analyzed:** 9 industries

### Model 3: Founder Background Analyzer
- **Companies Analyzed:** 5,621 with founder data
- **Founders Scraped:** 13,000+ from YC company pages
- **Key Finding:** Technical co-founders increase success rate

### Model 4: Traction Predictor
- **Algorithm:** Gradient Boosting Classifier
- **Accuracy:** 91.4%
- **Categories:** Low / Medium / High traction

---

## 🎯 Interview Talking Points

1. **"How did you get the data?"** — Built custom scrapers for 5 different sources: SEC EDGAR API, YC company pages (5,690 HTML pages scraped for founder data), ProductHunt GraphQL API, GitHub REST API, and NewsAPI + TechCrunch RSS.

2. **"What was the hardest part?"** — Entity resolution: matching the same company across 5 different data sources with different naming conventions. Built a fuzzy matching pipeline using normalized names and fuzzywuzzy.

3. **"Why this project?"** — Wanted to demonstrate the full data lifecycle: from messy, unstructured raw data to actionable ML predictions and interactive dashboards.

4. **"What would you improve?"** — Add real-time data refresh with Airflow, incorporate LinkedIn data for deeper founder analysis, and build an automated alert system for emerging hot sectors.

---

## 👤 Author

**Yash Singh Thakur**
- MS in Information Systems, Syracuse University (May 2026)
- 📧 ysingh02@syr.edu
- 🔗 [LinkedIn](https://www.linkedin.com/in/yashsingh02)
- 💻 [GitHub](https://github.com/yashsingh05)
- 🌐 [Portfolio](https://yashsingh05.github.io/yashsingh.github.io/)

---

## 📜 License


This project is for educational and portfolio purposes. Data collected from public APIs and publicly available sources.
