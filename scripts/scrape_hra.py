import json
from datetime import datetime
from pathlib import Path

import requests
from bs4 import BeautifulSoup


ARTICLE_URL = "https://heartresearch.com.au/heart-disease/women-and-heart-disease/"
BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "data" / "json"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def get_soup(url: str) -> BeautifulSoup:
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/124.0.0.0 Safari/537.36"
        )
    }
    response = requests.get(url, headers=headers, timeout=20)
    response.raise_for_status()
    return BeautifulSoup(response.text, "lxml")


def clean_paragraphs(paragraphs: list[str]) -> list[str]:
    junk_phrases = [
        "read more",
        "subscribe",
        "newsletter",
        "donate",
        "share this",
        "facebook",
        "instagram",
        "twitter",
        "linkedin",
        "click here",
        "tax deductible",
        "abn",
        "monthly donation",
        "one-off gift",
    ]

    cleaned = []

    for p in paragraphs:
        text = p.strip()

        if len(text) < 40:
            continue

        lower_text = text.lower()

        if any(junk in lower_text for junk in junk_phrases):
            continue

        cleaned.append(text)

    return cleaned


def extract_title(soup: BeautifulSoup) -> str:
    selectors = ["h1", "title", "h2"]

    for selector in selectors:
        tag = soup.select_one(selector)
        if tag:
            text = tag.get_text(" ", strip=True)
            if text:
                text = text.replace(" – Heart Research Australia", "").strip()
                return text

    return ""


def extract_author(soup: BeautifulSoup) -> str:
    for tag in soup.find_all(["span", "p", "a"]):
        text = tag.get_text(" ", strip=True)
        if text.lower().startswith("by "):
            return text[3:].strip()
    return ""


def extract_publish_time(soup: BeautifulSoup) -> str:
    time_tag = soup.find("time")
    if time_tag:
        return time_tag.get("datetime", "") or time_tag.get_text(strip=True)
    return ""


def extract_content(soup: BeautifulSoup) -> tuple[str, str]:
    paragraph_tags = soup.find_all("p")
    raw_paragraphs = [p.get_text(" ", strip=True) for p in paragraph_tags]
    cleaned_paragraphs = clean_paragraphs(raw_paragraphs)

    content = "\n".join(cleaned_paragraphs[:15])
    summary = cleaned_paragraphs[0] if cleaned_paragraphs else ""

    return content, summary


def build_record(article_url: str, item_id: str) -> dict:
    soup = get_soup(article_url)

    title = extract_title(soup)
    author = extract_author(soup)
    publish_time = extract_publish_time(soup)
    content, summary = extract_content(soup)

    record = {
        "id": item_id,
        "source": "Heart Research Australia",
        "platform": "news",
        "source_type": "institution",
        "url": article_url,
        "title": title,
        "content": content,
        "summary": summary,
        "author": author,
        "author_type": "organisation" if not author else "journalist",
        "publish_time": publish_time,
        "scrape_time": datetime.now().isoformat(),
        "tags": [],
        "hashtags": [],
        "mentions": [],
        "engagement": {"likes": None, "comments": None, "shares": None, "views": None},
        "media_type": "text",
        "media_url": "",
        "topic": "women_heart_health",
        "content_type": "article",
        "language": "en",
    }

    return record


def save_json(record: dict, filename: str) -> None:
    output_path = OUTPUT_DIR / filename
    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(record, file, indent=2, ensure_ascii=False)


def main() -> None:
    record = build_record(ARTICLE_URL, "heart_res_aus_samp")
    save_json(record, "heart_res_aus_samp.json")

    print("Saved article to data/json/hra_001.json")
    print("Title:", record["title"])
    print("URL:", record["url"])
    print("Summary:", record["summary"][:150])


if __name__ == "__main__":
    main()
