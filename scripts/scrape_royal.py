"""
scrape_royalwomens.py
Scrapes news and health information from The Royal Women's Hospital (Melbourne).
URL: https://www.thewomens.org.au/news (paginated) +
     https://www.thewomens.org.au/health-information
"""

import matplotlib.pyplot as plt
from datetime import datetime

from common import (
    classify_topic,
    clean_paragraph_list,
    extract_author_generic,
    extract_publish_time_generic,
    extract_summary_from_paragraphs,
    extract_title_generic,
    get_soup,
    save_json,
    now_iso,
    CHART_DIR,
)

LISTING_URL = "https://www.thewomens.org.au/news"
HEALTH_INFO_URL = "https://www.thewomens.org.au/health-information"
BASE_DOMAIN = "https://www.thewomens.org.au"
MAX_PAGES = 10
MAX_ARTICLES = 200


def build_page_url(page: int) -> str:
    if page == 1:
        return f"{LISTING_URL}/page/"
    offset = (page - 1) * 6
    return f"{LISTING_URL}/page/P{offset}"


def collect_article_links() -> list[str]:
    links = []

    for page in range(1, MAX_PAGES + 1):
        page_url = build_page_url(page)
        print(f"Scanning news page {page}: {page_url}")

        try:
            soup = get_soup(page_url)
        except Exception as error:
            print(f"Error fetching page {page}: {error}")
            break

        found_on_page = 0

        for a_tag in soup.find_all("a", href=True):
            href = a_tag["href"]

            if href.startswith("/"):
                href = f"{BASE_DOMAIN}{href}"

            if not href.startswith(BASE_DOMAIN):
                continue

            if "#" in href:
                continue

            # Exclude known listing/pagination pages
            if href in [LISTING_URL, HEALTH_INFO_URL]:
                continue
            if "/news/page/" in href:
                continue

            path = href.replace(BASE_DOMAIN, "").rstrip("/")
            parts = [p for p in path.split("/") if p]

            is_news = (
                len(parts) >= 2
                and parts[0] == "news"
                and parts[1] not in ("page",)
            )
            is_health_info = (
                len(parts) >= 2
                and parts[0] == "health-information"
            )

            if not (is_news or is_health_info):
                continue

            if href not in links:
                links.append(href)
                found_on_page += 1

        print(f"  Found {found_on_page} links on page {page}")

        if found_on_page == 0:
            print("No new links found — stopping pagination.")
            break

    print(f"\nScanning health info: {HEALTH_INFO_URL}")
    try:
        soup = get_soup(HEALTH_INFO_URL)
        found_health = 0

        for a_tag in soup.find_all("a", href=True):
            href = a_tag["href"]

            if href.startswith("/"):
                href = f"{BASE_DOMAIN}{href}"

            if not href.startswith(f"{BASE_DOMAIN}/health-information/"):
                continue

            if "#" in href or href == HEALTH_INFO_URL:
                continue

            # Must have a slug after /health-information/
            path = href.replace(BASE_DOMAIN, "").rstrip("/")
            parts = [p for p in path.split("/") if p]
            if len(parts) < 2:
                continue

            if href not in links:
                links.append(href)
                found_health += 1

        print(f"  Found {found_health} health information links")

    except Exception as error:
        print(f"Error fetching health info page: {error}")

    return links


def extract_content_and_summary(soup, title: str) -> tuple[str, str]:
    junk_phrases = [
        "read more",
        "subscribe",
        "newsletter",
        "donate",
        "share this",
        "click here",
        "follow us",
        "sign up",
        "contact us",
        "make an appointment",
        "find a service",
        "privacy policy",
        "back to top",
        "this page was",
        "last updated",
        "print this page",
    ]

    paragraphs = [p.get_text(" ", strip=True) for p in soup.find_all("p")]
    cleaned = clean_paragraph_list(paragraphs, junk_phrases=junk_phrases, min_length=40)

    content = "\n".join(cleaned[:15]) if cleaned else ""
    summary = extract_summary_from_paragraphs(cleaned, title)

    return content, summary


def build_article_record(article_url: str, item_id: str) -> dict:
    soup = get_soup(article_url)

    title = extract_title_generic(
        soup,
        [
            " | The Royal Women's Hospital",
            " - The Royal Women's Hospital",
            " – The Royal Women's Hospital",
        ],
    )
    author = extract_author_generic(soup)
    publish_time = extract_publish_time_generic(soup)
    content, summary = extract_content_and_summary(soup, title or "")

    content_type = "article" if "/news/" in article_url else "guide"

    return {
        "id": item_id,
        "source": "Royal Women's Hospital",
        "source_category": "institutional",
        "source_type": "hospital",
        "source_classification": "factual",
        "url": article_url,
        "title": title,
        "content": content,
        "summary": summary,
        "author": author or None,
        "author_type": "organisation" if author else None,
        "publish_time": publish_time or None,
        "scrape_time": now_iso(),
        "tags": [],
        "hashtags": [],
        "mentions": [],
        "engagement": {
            "likes": None,
            "comments": None,
            "shares": None,
        },
        "media_type": "text",
        "content_type": content_type,
        "language": "en",
    }


def main() -> None:
    links = collect_article_links()
    print(f"\nFound {len(links)} possible article links.")

    if not links:
        print("No article links found.")
        return

    records = []
    general_count = 0
    heart_count = 0
    women_heart_count = 0

    for index, link in enumerate(links[:MAX_ARTICLES], start=1):
        print(f"\nChecking article {index}: {link}")

        try:
            article = build_article_record(link, f"rwh_{index:03d}")
        except Exception as error:
            print(f"Error reading article: {error}")
            continue

        print("Title:", article["title"])

        topic = classify_topic(article["title"] or "", article["content"] or "")

        if topic == "general_health":
            general_count += 1
        elif topic == "heart_health":
            heart_count += 1
        elif topic == "women_heart_health":
            women_heart_count += 1
            records.append(article)

    if records:
        save_json(records, "royalwomens.json")
        print(f"\nSaved {len(records)} articles to royalwomens.json")
    else:
        print("\nNo women's heart health articles found.")

    print("\nScraping Summary:")
    print(f"Total examined: {general_count + heart_count + women_heart_count}")
    print(f"General health: {general_count}")
    print(f"Heart health: {heart_count}")
    print(f"Women's heart health: {women_heart_count}")

    labels = ["general_health", "heart_health", "women_heart_health"]
    values = [general_count, heart_count, women_heart_count]

    plt.figure()
    plt.bar(labels, values)
    plt.title("Royal Women's Hospital Article Summary")
    plt.xlabel("Category")
    plt.ylabel("Number of Articles")
    plt.xticks(rotation=20)
    plt.tight_layout()

    timestamp = datetime.now().strftime("%Y%m%d_%H%M")
    chart_path = CHART_DIR / f"royalwomens_summary_{timestamp}.png"
    plt.savefig(chart_path)
    plt.close()
    print(f"Chart saved to: {chart_path}")


if __name__ == "__main__":
    main()