-- Guardian Editorial Output Analysis
-- Run one query at a time in DB Browser for SQLite.

-- 1. Confirm that the database contains articles.
SELECT COUNT(*) AS total_articles
FROM articles;

-- 2. Confirm the date range and availability of word counts.
SELECT
    MIN(publication_date) AS first_date,
    MAX(publication_date) AS last_date,
    COUNT(word_count) AS articles_with_word_count,
    COUNT(*) - COUNT(word_count) AS articles_without_word_count
FROM articles;

-- Practice questions to complete:

-- 3. How many articles were published in each section?
SELECT
    section_name,
    COUNT(*) AS article_count
FROM articles
GROUP BY section_name
ORDER BY article_count DESC;

-- 4. On which days of the week were the most articles published?
SELECT
    publication_day,
    COUNT(*) AS article_count
FROM articles
GROUP BY publication_day
ORDER BY article_count DESC;

-- 5. What was the average article word count in each section?
SELECT
    section_name,
    ROUND(AVG(word_count), 0) AS average_word_count
FROM articles
GROUP BY section_name
ORDER BY average_word_count DESC;

-- 6a. Which raw byline values appeared most frequently?
-- This is a data-quality check: bylines may include roles, multiple authors,
-- trailing spaces or collective labels.
SELECT
    byline,
    COUNT(*) AS article_count
FROM articles
WHERE byline IS NOT NULL
  AND TRIM(byline) <> ''
GROUP BY byline
ORDER BY article_count DESC
LIMIT 10;

-- 6b. Which normalized contributor tags appeared on the most articles?
SELECT
    tags.tag_name AS contributor,
    COUNT(DISTINCT article_tags.article_id) AS article_count
FROM tags
INNER JOIN article_tags
    ON tags.tag_id = article_tags.tag_id
WHERE tags.tag_type = 'contributor'
GROUP BY tags.tag_id, tags.tag_name
ORDER BY article_count DESC, contributor ASC
LIMIT 10;


-- 7. Which keyword tags appeared most frequently?
SELECT
    tags.tag_name AS keyword,
    COUNT(DISTINCT article_tags.article_id) AS article_count
FROM tags
INNER JOIN article_tags
    ON tags.tag_id = article_tags.tag_id
WHERE tags.tag_type = 'keyword'
GROUP BY tags.tag_id, tags.tag_name
ORDER BY article_count DESC, keyword ASC
LIMIT 15;

-- 8. How did publishing volume vary by time of day (UTC)?
SELECT
    CASE
        WHEN publication_hour BETWEEN 0 AND 5 THEN 'Night'
        WHEN publication_hour BETWEEN 6 AND 11 THEN 'Morning'
        WHEN publication_hour BETWEEN 12 AND 17 THEN 'Afternoon'
        WHEN publication_hour BETWEEN 18 AND 23 THEN 'Evening'
        ELSE 'Unknown'
    END AS time_of_day,
    COUNT(*) AS article_count
FROM articles
GROUP BY time_of_day
ORDER BY article_count DESC;


-- 9. Which sections had an average word count above the overall average?
SELECT
    section_name,
    ROUND(AVG(word_count), 0) AS average_word_count
FROM articles
GROUP BY section_name
HAVING AVG(word_count) > (
    SELECT AVG(word_count)
    FROM articles
)
ORDER BY average_word_count DESC;
