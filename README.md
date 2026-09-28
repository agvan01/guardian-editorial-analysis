# Guardian Editorial Output Analysis

A SQL portfolio project analysing publication metadata from The Guardian. The analysis explores editorial output by section, weekday, publication time, contributor, article length and topic.

The project contains 1,098 content items published across five sections during a four-week period. It examines publishing activity rather than audience engagement, as the public Guardian Content API does not provide page views, reading time or subscription data.

## Dataset

- Period: 30 August 2026 to 26 September 2026
- Sections: Business, Technology, World news, Politics and Culture
- Source: Guardian Open Platform Content API
- Records: 1,098 content items and 1,557 tags
- Content collected: publication metadata only; article body text was not requested

## Research questions

1. How did publication volume vary by section?
2. Which days and times had the highest publishing activity?
3. How did average article length differ between sections?
4. Which contributors and topics appeared most frequently?
5. Which sections had an average article length above the overall average?

## SQL methods used

- Filtering and sorting
- `COUNT` and `AVG`
- `GROUP BY` and `HAVING`
- `INNER JOIN`
- `CASE` expressions
- Subqueries
- Distinct counts
- Data-quality checks

## Key findings

- World news had the highest publication volume, with 488 of 1,098 content items.
- Wednesday was the busiest publishing day, with 205 items during the four-week period.
- Politics had the highest average article length at approximately 1,356 words.
- Politics was the only section above the overall average article length of approximately 1,120 words.
- The afternoon was the busiest publishing period, accounting for 513 items, or approximately 46.7% of the dataset.
- Contributor tags produced more consistent author-level results than the free-text byline field, which sometimes included job titles and other variations.
- AI was one of the most frequent specific subject tags, appearing on 112 content items.

## Visualisations

### Publication volume by section

![Guardian articles published by section](charts/articles-by-section.svg)

### Publication volume by day of the week

![Guardian articles published by day of the week](charts/articles-by-weekday.svg)

### Average article length by section

![Average Guardian article length by section](charts/average-word-count-by-section.svg)

The dashed line in the final chart represents the overall average article length across the five selected sections.

## Database structure

The SQLite database contains three tables:

- `articles`: one row per Guardian content item
- `tags`: one row per keyword or contributor tag
- `article_tags`: a linking table connecting articles with their tags

## Reproduce the analysis

### Requirements

- Python 3
- A free Guardian Open Platform Developer key
- DB Browser for SQLite, or another SQLite client

### Create the database

1. Register for a non-commercial Developer key at [The Guardian Open Platform](https://open-platform.theguardian.com/access/).
2. Download or clone this repository.
3. Open a terminal in the project folder.
4. Run:

```bash
python3 download_guardian_data.py
```

5. Paste the API key when requested. The key is hidden while being entered and is not stored.
6. Wait for the download to finish.

The script creates:

- `data/guardian_editorial_analysis.sqlite`
- `data/articles.csv`
- `data/tags.csv`
- `data/article_tags.csv`

### Run the SQL analysis

1. Open `data/guardian_editorial_analysis.sqlite` in DB Browser for SQLite.
2. Select **Execute SQL**.
3. Run the queries contained in `sql/analysis_queries.sql`.

### Recreate the charts

Run:

```bash
python3 create_charts.py
```

The script reads the results directly from the SQLite database and recreates the SVG files in the `charts` folder.

## Project structure

```text
guardian-editorial-analysis/
├── charts/                     # Data visualisations
├── results/
│   └── findings.md             # Detailed findings and interpretation
├── sql/
│   └── analysis_queries.sql    # SQL analysis
├── create_charts.py            # Recreates the visualisations
├── download_guardian_data.py   # Downloads and prepares the API data
└── README.md
```

## Limitations

This dataset measures editorial output rather than article performance. It does not include page views, unique visitors, reading time, scroll depth, subscriptions or other engagement metrics.

Keyword and contributor counts can overlap because one article may contain multiple tags or contributors. The findings should therefore be interpreted as patterns in Guardian publishing activity during the selected period.
