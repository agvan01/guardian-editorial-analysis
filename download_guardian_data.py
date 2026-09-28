#!/usr/bin/env python3
"""Download Guardian article metadata and build a local SQLite database.

The API key is requested securely at runtime and is never written to disk.
Only article metadata is downloaded; article body text is not requested.
"""

from __future__ import annotations

import csv
import getpass
import json
import sqlite3
import sys
import time
from datetime import datetime
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import unquote, urlencode, urlparse
from urllib.request import Request, urlopen


API_URL = "https://content.guardianapis.com/search"
FROM_DATE = "2026-08-30"
TO_DATE = "2026-09-26"
SECTIONS = ("business", "technology", "world", "politics", "culture")
PAGE_SIZE = 200
REQUEST_DELAY_SECONDS = 1.05

PROJECT_DIR = Path(__file__).resolve().parent
DATA_DIR = PROJECT_DIR / "data"
DATABASE_PATH = DATA_DIR / "guardian_editorial_analysis.sqlite"


SCHEMA = """
PRAGMA foreign_keys = ON;

CREATE TABLE articles (
    article_id TEXT PRIMARY KEY,
    content_type TEXT,
    section_id TEXT,
    section_name TEXT,
    publication_datetime TEXT,
    publication_date TEXT,
    publication_day TEXT,
    publication_hour INTEGER,
    title TEXT NOT NULL,
    byline TEXT,
    word_count INTEGER,
    web_url TEXT,
    api_url TEXT
);

CREATE TABLE tags (
    tag_id TEXT PRIMARY KEY,
    tag_name TEXT NOT NULL,
    tag_type TEXT,
    web_url TEXT
);

CREATE TABLE article_tags (
    article_id TEXT NOT NULL,
    tag_id TEXT NOT NULL,
    PRIMARY KEY (article_id, tag_id),
    FOREIGN KEY (article_id) REFERENCES articles(article_id),
    FOREIGN KEY (tag_id) REFERENCES tags(tag_id)
);

CREATE INDEX idx_articles_section ON articles(section_id);
CREATE INDEX idx_articles_date ON articles(publication_date);
CREATE INDEX idx_article_tags_tag ON article_tags(tag_id);
"""


def request_json(params: dict[str, str | int]) -> dict:
    url = f"{API_URL}?{urlencode(params)}"
    request = Request(url, headers={"User-Agent": "Guardian-SQL-Portfolio-Project/1.0"})

    for attempt in range(1, 4):
        try:
            with urlopen(request, timeout=45) as response:
                return json.load(response)
        except HTTPError as exc:
            if exc.code == 429 and attempt < 3:
                wait_seconds = int(exc.headers.get("Retry-After", "5"))
                print(f"Rate limit reached. Waiting {wait_seconds} seconds...")
                time.sleep(wait_seconds)
                continue
            raise RuntimeError(f"Guardian API returned HTTP {exc.code}: {exc.reason}") from exc
        except URLError as exc:
            if attempt < 3:
                print("Network problem. Retrying in 5 seconds...")
                time.sleep(5)
                continue
            raise RuntimeError(f"Could not connect to the Guardian API: {exc.reason}") from exc

    raise RuntimeError("The Guardian API request failed after three attempts.")


def parse_publication_date(value: str | None) -> tuple[str | None, str | None, int | None]:
    if not value:
        return None, None, None

    try:
        published = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return value[:10] or None, None, None

    day_names = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday")
    return published.date().isoformat(), day_names[published.weekday()], published.hour


def parse_word_count(value: object) -> int | None:
    try:
        return int(str(value))
    except (TypeError, ValueError):
        return None


def extract_api_key(value: str) -> str:
    """Accept either a bare API key or a Guardian test URL containing one."""
    value = value.strip()
    if not value:
        return ""

    if value.startswith(("http://", "https://")):
        # Split manually instead of using parse_qs: API keys may contain a
        # literal '+' character, which parse_qs would incorrectly turn into a
        # space before the next request is built.
        for part in urlparse(value).query.split("&"):
            name, separator, raw_value = part.partition("=")
            if separator and name in {"api-key", "api_key"}:
                return unquote(raw_value).strip()
        return ""

    return value


def insert_result(connection: sqlite3.Connection, result: dict) -> None:
    fields = result.get("fields") or {}
    published_datetime = result.get("webPublicationDate")
    publication_date, publication_day, publication_hour = parse_publication_date(published_datetime)

    connection.execute(
        """
        INSERT OR REPLACE INTO articles (
            article_id, content_type, section_id, section_name,
            publication_datetime, publication_date, publication_day,
            publication_hour, title, byline, word_count, web_url, api_url
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            result.get("id"),
            result.get("type"),
            result.get("sectionId"),
            result.get("sectionName"),
            published_datetime,
            publication_date,
            publication_day,
            publication_hour,
            result.get("webTitle") or fields.get("headline") or "Untitled",
            fields.get("byline"),
            parse_word_count(fields.get("wordcount")),
            result.get("webUrl"),
            result.get("apiUrl"),
        ),
    )

    for tag in result.get("tags") or []:
        tag_id = tag.get("id")
        if not tag_id:
            continue

        connection.execute(
            """
            INSERT INTO tags (tag_id, tag_name, tag_type, web_url)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(tag_id) DO UPDATE SET
                tag_name = excluded.tag_name,
                tag_type = excluded.tag_type,
                web_url = excluded.web_url
            """,
            (tag_id, tag.get("webTitle") or tag_id, tag.get("type"), tag.get("webUrl")),
        )
        connection.execute(
            "INSERT OR IGNORE INTO article_tags (article_id, tag_id) VALUES (?, ?)",
            (result.get("id"), tag_id),
        )


def download_section(connection: sqlite3.Connection, api_key: str, section: str) -> int:
    page = 1
    pages = 1
    downloaded = 0

    while page <= pages:
        params: dict[str, str | int] = {
            "api-key": api_key,
            "section": section,
            "from-date": FROM_DATE,
            "to-date": TO_DATE,
            "order-by": "oldest",
            "page-size": PAGE_SIZE,
            "page": page,
            "show-fields": "headline,byline,wordcount,short-url",
            "show-tags": "keyword,contributor",
        }

        payload = request_json(params)
        response = payload.get("response") or {}
        if response.get("status") != "ok":
            raise RuntimeError(f"Unexpected Guardian API response for section '{section}'.")

        pages = int(response.get("pages") or 1)
        results = response.get("results") or []
        for result in results:
            insert_result(connection, result)

        connection.commit()
        downloaded += len(results)
        print(f"  {section}: page {page}/{pages} ({downloaded} articles)")
        page += 1

        if page <= pages:
            time.sleep(REQUEST_DELAY_SECONDS)

    return downloaded


def export_table(connection: sqlite3.Connection, table_name: str) -> None:
    destination = DATA_DIR / f"{table_name}.csv"
    cursor = connection.execute(f'SELECT * FROM "{table_name}"')
    columns = [description[0] for description in cursor.description]

    with destination.open("w", encoding="utf-8", newline="") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow(columns)
        writer.writerows(cursor)


def prepare_database() -> sqlite3.Connection:
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    if DATABASE_PATH.exists():
        answer = input(
            f"A database already exists at {DATABASE_PATH}. Replace it? [y/N]: "
        ).strip().lower()
        if answer not in {"y", "yes"}:
            print("Nothing was changed.")
            sys.exit(0)
        DATABASE_PATH.unlink()

    connection = sqlite3.connect(DATABASE_PATH)
    connection.executescript(SCHEMA)
    return connection


def main() -> None:
    print("Guardian Editorial Output Analysis")
    print(f"Period: {FROM_DATE} to {TO_DATE}")
    print(f"Sections: {', '.join(SECTIONS)}")
    print("The API key will not be displayed or saved.\n")

    entered_value = getpass.getpass(
        "Paste your Guardian API key or the full Guardian test URL and press Enter: "
    )
    api_key = extract_api_key(entered_value)
    if not api_key:
        print("No API key was entered.")
        sys.exit(1)

    connection = prepare_database()
    try:
        for section in SECTIONS:
            print(f"Downloading {section}...")
            download_section(connection, api_key, section)

        for table_name in ("articles", "tags", "article_tags"):
            export_table(connection, table_name)

        article_count = connection.execute("SELECT COUNT(*) FROM articles").fetchone()[0]
        tag_count = connection.execute("SELECT COUNT(*) FROM tags").fetchone()[0]
    except Exception:
        connection.close()
        raise
    else:
        connection.close()

    print("\nDownload complete.")
    print(f"Articles: {article_count}")
    print(f"Tags: {tag_count}")
    print(f"Database: {DATABASE_PATH}")
    print("Open this .sqlite file in DB Browser for SQLite.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nDownload cancelled.")
        sys.exit(1)
    except Exception as exc:
        print(f"\nError: {exc}", file=sys.stderr)
        sys.exit(1)
