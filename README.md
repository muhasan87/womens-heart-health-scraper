# Women's Heart Health Data Scraper

## Capstone Overview

This project is a modular Python scraping and analysis pipeline for collecting, normalising, classifying, and visualising women's heart health content across news, medical, institutional, and community sources.

The system was built to answer a practical data question: how often do public health sources discuss women's heart health, what themes appear most often, and how does that coverage differ across factual medical sources, hospitals, media outlets, and community discussion platforms?

The pipeline combines source-specific web scrapers with a shared processing layer that outputs consistent JSON records, source-level statistics, and chart-ready analytics.

## Headline Results

Current stat-backed dataset:

| Metric | Value |
|---|---:|
| Active/stat-backed sources | 9 |
| Total records examined | 1,509 |
| Women's heart health records identified | 121 |
| Heart health records identified | 330 |
| General health records identified | 1,058 |
| Keyword/tag categories tracked | 14 |
| Sentiment classes tracked | 3 |
| Source classification types | 3 |

Topic distribution:

| Topic | Count |
|---|---:|
| General health | 1,058 |
| Heart health | 330 |
| Women's heart health | 121 |

Sentiment distribution:

| Sentiment | Count |
|---|---:|
| Positive | 420 |
| Neutral | 650 |
| Negative | 439 |

Source classification:

| Classification | Count |
|---|---:|
| Factual | 1,258 |
| Opinion/anecdotal | 182 |
| Mixed | 69 |

## Data Sources

| Source | Records Examined | Women's Heart Health Records | Source Category |
|---|---:|---:|---|
| ABC News | 257 | 4 | News/media |
| HealthUnlocked | 298 | 3 | Community/forum |
| Heart Research Australia | 45 | 4 | Organisation/research |
| Heart Foundation | 118 | 16 | Institutional/organisation |
| Jean Hailes | 285 | 47 | Women's health organisation |
| Medical News Today | 236 | 31 | Medical news/media |
| Reddit r/WomensHealth | 122 | 4 | Community/forum |
| Royal Women's Hospital | 79 | 6 | Hospital/institutional |
| Women's Health Magazine | 69 | 6 | Media/magazine |

## What The Scrapers Do

The project uses a separate scraper for each website because every source has different page structure, pagination, metadata, and content layout. All scrapers write into the same JSON/statistics format.

| Script | Purpose |
|---|---|
| `scripts/common.py` | Shared helper module for requests, BeautifulSoup parsing, text cleaning, metadata extraction, topic classification, keyword tagging, sentiment analysis, stats updates, and JSON saving. |
| `scripts/scrape_abc_loadmore.py` | Scrapes ABC News health content using Selenium to trigger "load more" behaviour and collect article links. |
| `scripts/scrape_abc.py` | Earlier ABC News scraper focused on ABC's heart disease topic page. |
| `scripts/scrape_mnt.py` | Scrapes Medical News Today across cardiovascular health, women's health, and heart disease sections. |
| `scripts/scrape_hra.py` | Scrapes Heart Research Australia heart hub and research project pages. |
| `scripts/scrape_hf.py` | Scrapes Heart Foundation media releases/news pages using Selenium pagination. |
| `scripts/scrape_jh.py` | Scrapes Jean Hailes news and stories, separating factual articles from anecdotal story content. |
| `scripts/scrape_royal.py` | Scrapes Royal Women's Hospital news and health information pages. |
| `scripts/scrape_whm.py` | Scrapes Women's Health Magazine health articles using Selenium "See More" loading. |
| `scripts/scrape_reddit.py` | Scrapes old Reddit r/WomensHealth posts and classifies user-generated health discussions. |
| `scripts/scrape_unlocked.py` | Scrapes HealthUnlocked communities including heart failure, atrial fibrillation, women's health, menopause/perimenopause, and cholesterol support forums. |
| `scripts/scrape_ig_wha.py` | Experimental Instagram scraper for Women's Heart Alliance using Instaloader. |
| `scripts/scrape_hb.py` | Experimental HealthBoards forum scraper for heart disorder discussion threads. |
| `scripts/analysis.py` | Aggregates saved source stats and generates cross-source charts and insights. |

## Unified Output Schema

Each scraper builds records with a shared structure so content can be compared across sources:

```json
{
  "id": "source_001",
  "source": "Source Name",
  "source_category": "news | website | forum | institutional | social_media",
  "source_type": "media | organisation | hospital | community",
  "source_classification": "factual | opinion/anecdotal | mixed",
  "url": "https://example.com/article",
  "title": "Record title",
  "content": "Cleaned article or post text",
  "summary": "Short extracted summary",
  "author": "Author or organisation",
  "author_type": "individual | organisation",
  "publish_time": "ISO-like timestamp where available",
  "scrape_time": "UTC scrape timestamp",
  "tags": ["heart_disease", "menopause"],
  "hashtags": [],
  "engagement": {
    "likes": null,
    "comments": null,
    "shares": null
  },
  "media_type": "text",
  "content_type": "article | post | guide | media_release",
  "language": "en"
}
```

## Metrics Saved

Each stat-backed scraper saves a source-level stats file in `data/json/stats/`. The metrics include:

- `total_examined`
- topic counts: `general_health`, `heart_health`, `women_heart_health`
- keyword/tag counts
- sentiment counts: `positive`, `neutral`, `negative`
- source classification counts: `factual`, `opinion/anecdotal`, `mixed`
- heart health subset counts and tag/sentiment breakdowns
- women's heart health subset counts and tag/sentiment breakdowns
- date range where publish dates are available
- section-level breakdowns for multi-section sources

## Classification And Analysis

The shared analysis logic in `common.py` applies lightweight rule-based NLP:

- Topic classification detects heart health and women-specific health terminology.
- Keyword tagging tracks recurring clinical, lifestyle, and gender-specific themes.
- Sentiment analysis estimates positive, neutral, or negative framing using weighted keyword rules and simple negation handling.
- Source classification separates factual, anecdotal, and mixed content types.

Tracked keyword tags include:

| Tag | Meaning |
|---|---|
| `female_risk_factors` | Women, female, maternal, sex-specific risk language |
| `heart_disease` | Heart disease and cardiovascular disease references |
| `cardiovascular` | Cardiac, coronary, artery, atherosclerosis language |
| `heart_attack` | Heart attack and myocardial infarction references |
| `hypertension` | Blood pressure and hypertension references |
| `cholesterol` | Cholesterol, LDL, HDL references |
| `stroke` | Stroke references |
| `arrhythmia` | Arrhythmia, palpitations, tachycardia, atrial fibrillation |
| `chest_pain` | Chest pain, shortness of breath, fatigue, dizziness |
| `menopause` | Menopause and perimenopause references |
| `pregnancy` | Pregnancy, preeclampsia, gestational, postpartum |
| `mental_health` | Stress, anxiety, depression, emotional burden |
| `diet` | Diet, nutrition, obesity |
| `exercise` | Exercise, physical activity, fitness |

Top overall tags in the current dataset:

| Tag | Count |
|---|---:|
| `female_risk_factors` | 562 |
| `mental_health` | 308 |
| `heart_disease` | 223 |
| `cardiovascular` | 215 |
| `menopause` | 203 |
| `diet` | 194 |
| `pregnancy` | 170 |
| `exercise` | 170 |
| `heart_attack` | 143 |
| `hypertension` | 133 |

Top tags within women's heart health records:

| Tag | Count |
|---|---:|
| `female_risk_factors` | 113 |
| `heart_disease` | 77 |
| `cardiovascular` | 55 |
| `hypertension` | 46 |
| `mental_health` | 44 |
| `menopause` | 42 |
| `stroke` | 40 |
| `heart_attack` | 38 |
| `pregnancy` | 33 |
| `diet` | 33 |

## Visual Analytics

The analysis pipeline generates charts in `data/charts/` for recruiter/demo review.

### Topic And Source Coverage

![Topic distribution](data/charts/topic_distribution.png)

![Source distribution](data/charts/source_distribution.png)

![Source topic percentage](data/charts/source_topic_percent.png)

![Coverage funnel](data/charts/coverage_funnel.png)

### Sentiment And Classification

![Sentiment distribution](data/charts/sentiment_distribution.png)

![Sentiment by source](data/charts/sentiment_by_source.png)

![Source classification](data/charts/source_classification.png)

### Women's Heart Health Insights

![Women's heart health tags](data/charts/women_tags.png)

![Women's heart health sentiment](data/charts/women_sentiment_distribution.png)

![Women's tag heatmap](data/charts/women_tag_heatmap.png)

![Women's sentiment tag heatmap](data/charts/women_sentiment_tag_heatmap.png)

### Comparative Analysis

![Heart vs women's heart health tags](data/charts/heart_vs_women_tags.png)

![Heart vs women's heart health sentiment](data/charts/heart_vs_women_sentiment.png)

![Cardiovascular ratio](data/charts/whh_cardiovascular_ratio.png)

## Project Structure

```text
.
├── README.md
├── requirements.txt
├── scripts/
│   ├── common.py
│   ├── analysis.py
│   ├── scrape_abc_loadmore.py
│   ├── scrape_hf.py
│   ├── scrape_hra.py
│   ├── scrape_jh.py
│   ├── scrape_mnt.py
│   ├── scrape_reddit.py
│   ├── scrape_royal.py
│   ├── scrape_unlocked.py
│   └── scrape_whm.py
└── data/
    ├── json/
    │   ├── *.json
    │   └── stats/
    │       └── *stats.json
    └── charts/
        └── *.png
```

## How To Run

Install dependencies:

```bash
pip install -r requirements.txt
```

Run an individual scraper:

```bash
python scripts/scrape_mnt.py
```

Run the aggregate analysis and regenerate charts:

```bash
python scripts/analysis.py
```

Notes:

- Selenium-based scrapers require Chrome/Chromedriver support.
- Some sources change their HTML over time, so selectors may need maintenance.
- Instagram scraping requires a valid Instaloader session and is treated as experimental in this repo.

##  Summary

This capstone demonstrates end-to-end data engineering and analysis work: source discovery, web scraping, browser automation, content cleaning, schema design, rule-based NLP, structured JSON outputs, cross-source statistics, and visual reporting. The project is intentionally modular so new health sources can be added without changing the shared processing and analytics layer.

Potential resume wording:

- Built a modular Python scraping and analysis pipeline that examined 1,509 health records across 9 news, medical, institutional, and community sources.
- Designed a unified JSON schema for heterogeneous article, guide, forum, and media content, enabling cross-source comparison.
- Implemented source-specific scrapers using Requests, BeautifulSoup, Selenium, and Instaloader to handle static pages, pagination, load-more interactions, and forum/social content.
- Developed rule-based topic classification, keyword tagging, and sentiment analysis to identify 121 women's heart health records and quantify themes across sources.
- Generated visual analytics for source coverage, topic distribution, sentiment, source classification, keyword trends, and women's heart health subset comparisons.
