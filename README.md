# PharmaSentinel
### Real-Time Drug Safety Signal Detection via Social Media and CDSCO Label Cross-Referencing

> **Theme 6 — Real-Time Social Listening for Patient Experience & Safety Signals**

---

## The Problem

India's pharmacovigilance system depends on doctors and hospitals filing reports manually to CDSCO. That process is slow, underreported, and completely misses what patients are saying online.

A few months back we came across a Reddit thread where dozens of people were complaining about the same side effect from a common antibiotic. When we checked the drug's official label — that side effect was not mentioned anywhere.

**PharmaSentinel** is built to catch exactly these gaps, automatically.

---

## What It Does

### 1. Listens to Social Media
Crawls Twitter/X, Reddit, Quora, and health forums continuously. Users configure projects for specific drugs and set monitoring frequency (real-time / daily / weekly).

### 2. Checks Against CDSCO Labels
Every detected side effect is cross-referenced with the CDSCO-approved drug label:
- **Listed** → logged as LOW priority
- **Not listed** → HIGH priority signal raised immediately

### 3. Scores Signals and Generates Reports
Uses **PRR (Proportional Reporting Ratio)** — the same statistical method real pharmacovigilance systems use — to score each signal. When a signal crosses the threshold, an auto-generated pharmacovigilance report in CDSCO format is ready for review and submission.

---

## Dashboard Features

| Feature | Description |
|---|---|
| Project Management | One dashboard for all drug monitoring projects |
| Signal Timeline | When signals first appeared and how they grew |
| CDSCO Label Comparison | Reported side effects vs what the label says |
| PRR Scoring | Statistical confidence score for every signal |
| Source Posts | Anonymized social media posts behind each signal |
| PII Detection | Personal information removed before storage |
| Report Export | CDSCO-format pharmacovigilance reports |

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python, FastAPI, SQLAlchemy, SQLite |
| NLP Pipeline | Custom rule-based ADR extraction, first-person filter, PII anonymization |
| Signal Scoring | PRR (Proportional Reporting Ratio) with chi-squared test |
| Social Crawling | Reddit API (PRAW), twitterapi.io, mock data for demo |
| Frontend | HTML, Tailwind CSS, Chart.js |
| Drug Database | CDSCO-labeled data for 10 major Indian drugs |

---

## Project Structure

```
pharmasentinel/
├── backend/
│   ├── main.py                  # FastAPI app — all API routes
│   ├── models.py                # Database models (Project, Post, Signal, Report)
│   ├── database.py              # SQLite setup
│   ├── config.py                # Environment config
│   ├── crawlers/
│   │   ├── reddit_crawler.py    # Reddit PRAW integration
│   │   └── mock_generator.py    # Realistic demo data generator
│   ├── nlp/
│   │   └── adr_extractor.py    # ADR extraction + PII anonymization
│   ├── signals/
│   │   ├── prr_calculator.py   # PRR signal scoring
│   │   └── label_comparator.py # CDSCO label cross-reference
│   ├── reports/
│   │   └── generator.py        # CDSCO-format report generator
│   └── data/
│       ├── cdsco_labels.json   # Drug label database (10 drugs)
│       └── adr_terms.json      # ADR symptom ontology
├── frontend/
│   └── index.html              # Single-page dashboard
├── requirements.txt
├── start.sh                    # One-click startup script
└── .env.example
```

---

## Demo — What the Judges Will See

**Signal detected:** Azithromycin → Tinnitus
- 3 independent patient reports on Reddit
- PRR = 71.4 (threshold: 2.0)
- **NOT listed on CDSCO-approved label**
- Priority: HIGH
- Auto-generated pharmacovigilance report ready for CDSCO submission

---

## Setup & Run

### Requirements
- Python 3.9+

### Install and Start

```bash
git clone https://github.com/gunnu1106/pharmasentinel.git
cd pharmasentinel
./start.sh
```

Open: **http://localhost:8000/frontend/index.html**

### Optional — Add Real Reddit Data

```bash
cp .env.example backend/.env
# Add your Reddit API credentials to backend/.env
```

Get Reddit credentials at: https://www.reddit.com/prefs/apps

### API Docs
Auto-generated docs at: **http://localhost:8000/docs**

---

## How PRR Works

Proportional Reporting Ratio is the standard signal detection method in pharmacovigilance:

```
PRR = (reports of drug+ADR / all reports for drug)
      ÷
      (reports of ADR in background / all background reports)
```

**Signal criteria (WHO standard):**
- PRR ≥ 2.0
- Chi-squared ≥ 4.0
- At least 3 independent reports

---

## Who We Are

**Gunjan and Huda Khan** — MCA students at MIET Meerut.

We've been working on NLP and data projects for the past year. The problem felt genuine to us — real patients are reporting real side effects that regulators don't know about yet. The approach felt doable. So we built it.
