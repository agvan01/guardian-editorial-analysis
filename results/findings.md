# Guardian Editorial Output Analysis: Findings

## Scope

- Period: 30 August 2026 to 26 September 2026
- Sections: Business, Technology, World news, Politics and Culture
- Dataset: 1,098 Guardian content items and 1,557 tags
- Important limitation: the dataset measures publishing activity, not reader engagement or article performance

## 1. Publication volume by section

| Section | Articles |
|---|---:|
| World news | 488 |
| Politics | 221 |
| Business | 205 |
| Technology | 126 |
| Culture | 58 |

World news had the highest publication volume among the five selected sections during the four-week period, accounting for 488 of 1,098 content items. Culture had the lowest volume, with 58 items. These figures describe editorial output only and do not indicate readership or engagement.

## 2. Publication volume by day of the week

| Day | Articles |
|---|---:|
| Wednesday | 205 |
| Thursday | 179 |
| Tuesday | 177 |
| Friday | 157 |
| Monday | 154 |
| Sunday | 121 |
| Saturday | 105 |

Wednesday had the highest publication volume, with 205 content items, while Saturday had the lowest, with 105. The dataset covers exactly four complete weeks, so every weekday occurs the same number of times and the comparison is not distorted by an uneven date range. These results measure publishing volume rather than reader demand or engagement.

## 3. Average article length by section

| Section | Average word count |
|---|---:|
| Politics | 1,356 |
| Business | 1,097 |
| World news | 1,095 |
| Culture | 1,002 |
| Technology | 890 |

Politics had the highest average article length, at approximately 1,356 words, while Technology had the lowest, at approximately 890 words. Word-count data was available for all 1,098 content items, so no articles were excluded from these averages because of missing values. Article length alone does not indicate quality or reader engagement.

## 4. Raw byline frequency and data-quality issue

| Raw byline | Articles |
|---|---:|
| Julia Kollewe | 19 |
| Guardian staff and agencies | 19 |
| John Crace | 16 |
| Rowena Mason Whitehall editor | 15 |
| Graeme Wearden | 14 |
| Andrew Sparrow | 14 |
| Peter Walker Senior political correspondent | 13 |
| Robert Booth UK technology editor | 12 |
| Patrick Wintour Diplomatic editor | 11 |
| Jessica Elgot Deputy political editor | 11 |

The raw `byline` field is not a fully standardised author identifier: some values contain job titles, some articles use collective labels, and other records contain multiple authors or small spacing variations. Grouping only by `byline` can therefore split the same contributor across several groups. Contributor tags will be used for a cleaner author-level comparison.

## 5. Most frequent normalised contributors

| Contributor | Articles |
|---|---:|
| Heather Stewart | 31 |
| Patrick Wintour | 29 |
| Peter Walker | 28 |
| Julia Kollewe | 27 |
| Lisa O’Carroll | 25 |
| Dan Milmo | 24 |
| Jessica Elgot | 23 |
| Jennifer Rankin | 21 |
| Robert Booth | 20 |
| Rowena Mason | 20 |

Contributor tags consolidate byline variations into standardised author identities. For example, Heather Stewart appeared in 31 tagged articles, while the most frequent individual raw Heather Stewart byline variant appeared only eight times. The difference demonstrates why stable identifiers are preferable to free-text names when grouping records. Contributor counts may include jointly authored articles, so they should not be interpreted as 31 exclusively authored pieces.

## 6. Most frequent keyword tags

| Keyword | Articles |
|---|---:|
| World news | 431 |
| UK news | 416 |
| Politics | 283 |
| Business | 245 |
| Europe | 235 |
| US news | 159 |
| Technology | 150 |
| AI (artificial intelligence) | 112 |
| Labour | 89 |
| Middle East and north Africa | 88 |
| Reform UK | 84 |
| Russia | 83 |
| Culture | 81 |
| Economics | 80 |
| Andy Burnham | 78 |

Broad editorial classifications such as World news, UK news and Politics were the most frequent keyword tags. Among more specific subjects, AI appeared on 112 articles, followed by Labour, Middle East and north Africa, Reform UK, Russia and Economics. Keyword counts overlap because a single article can carry multiple tags; they should not be added together or interpreted as shares of total output without further calculation. The counts describe editorial coverage, not reader interest.

## 7. Publication volume by time of day

| Time band (UTC) | Articles |
|---|---:|
| Afternoon (12:00–17:59) | 513 |
| Morning (06:00–11:59) | 245 |
| Night (00:00–05:59) | 205 |
| Evening (18:00–23:59) | 135 |

The afternoon was the busiest publication period, with 513 of 1,098 content items (approximately 46.7%), while the evening had the lowest volume, with 135 items (approximately 12.3%). Publication timestamps supplied by the API are recorded in UTC; during this late-August-to-September period, UK local time was one hour ahead. These patterns describe when content was published, not when readers consumed it.

## 8. Sections above the overall average article length

| Section | Average word count |
|---|---:|
| Politics | 1,356 |

The overall average article length across all five sections was approximately 1,120 words. Politics was the only section above this benchmark, with an average of approximately 1,356 words. This comparison uses a subquery to calculate the overall benchmark and a `HAVING` clause to filter the grouped section results.
