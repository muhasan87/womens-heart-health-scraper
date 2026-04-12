import json
from pathlib import Path

from common import (
    # build_record,
    # classify_topic,
    clean_paragraph_list,
    extract_author_generic,
    extract_publish_time_generic,
    extract_summary_from_paragraphs,
    extract_title_generic,
    get_soup,
    #save_json,
    now_iso
)

LISTING_URL = "https://www.abc.net.au/news/health"

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR = BASE_DIR / "data" / "json"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def collect_article_links() -> list[str]:
    soup = get_soup(LISTING_URL)
    links = []

    for a_tag in soup.find_all("a", href=True):
        href = a_tag["href"]

        if href.startswith("/news/"):
            href = f"https://www.abc.net.au{href}"

        if not href.startswith("https://www.abc.net.au/news/"):
            continue

        if "#" in href:
            continue

        if "/news/20" not in href:
            continue

        if href not in links:
            links.append(href)

    return links


def extract_content_and_summary(soup, title: str) -> tuple[str, str]:
    junk_phrases = [
        "find any issues using dark mode",
        "please let us know",
        "do you have a story to share",
        "email",
        "read more",
        "skip to",
        "listen",
        "posted",
        "share this article",
        "loading",
    ]

    paragraphs = [p.get_text(" ", strip=True) for p in soup.find_all("p")]
    cleaned = clean_paragraph_list(paragraphs, junk_phrases=junk_phrases, min_length=40)

    content = "\n".join(cleaned[:15]) if cleaned else None
    summary = extract_summary_from_paragraphs(cleaned, title)

    return content, summary

def is_heart_related(title: str, content: str) -> bool:
    text = f"{title} {content}".lower()
    keywords = ["heart", "cardio", "cardiovascular", "stroke", "blood pressure"]
    return any(k in text for k in keywords)


def build_article_record(article_url: str, item_id: str) -> dict:
    soup = get_soup(article_url)

    #is_heart = is_heart_health_related(title or "", content or "")
    title = extract_title_generic(soup)
    author = extract_author_generic(soup)
    publish_time = extract_publish_time_generic(soup)
    content, summary = extract_content_and_summary(soup, title or "")
    source_class = "factual"

    record = {
        "id": item_id,
        "source": "ABC News",
        "source_category": "news",
        "source_type": "media",
        "source_classification": source_class,
        "url": article_url,
        "title": title,
        "content": content,
        "summary": summary,
        "author": author or None,
        "author_type": "individual" if author else None,
        "publish_time": publish_time or None,
        "scrape_time": now_iso(),
        "tags": [], #need to be improved later
        "hashtags": [],
        "mentions": [],
        "engagement": {
            "likes": None, 
            "comments": None, 
            "shares": None, 
        },
        "media_type": "text",
        "content_type": "article",
        "language": "en",
    }

    return record



def save_json(record: dict, filename: str) -> None:
    output_path = OUTPUT_DIR / filename
    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(record, file, indent=2, ensure_ascii=False)


def main() -> None:
    links = collect_article_links()
    print(f"Found {len(links)} possible article links")

    if not links:
        print("No article links found.")
        return

    print("\nFirst 10 candidate links:")
    for i, link in enumerate(links[:10], start=1):
        print(f"{i}. {link}")

    matched_article = None

    for index, link in enumerate(links[:20], start=1):
        print(f"\nChecking article {index}: {link}")

        try:
            article = build_article_record(link, f"abc_{index:03d}")
        except Exception as error:
            print(f"Error reading article: {error}")
            continue

        print("Title:", article["title"])

        if is_heart_related(article["title"] or "", article["content"] or ""):
            matched_article = article
            break

    if matched_article:
        save_json(matched_article, "abc_heart_sample.json")
        print("\nSaved article to data/json/abc_heart_sample.json")
        print("Title:", matched_article["title"])
        print("URL:", matched_article["url"])
        #print("Topic:", matched_article["topic"])
    else:
        print("\nNo women heart health articles found in first 20 ABC links.")


if __name__ == "__main__":
    main()