
import json
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

FEEDS = [
    "https://feeds.bbci.co.uk/news/rss.xml",
    "https://rss.nytimes.com/services/xml/rss/nyt/World.xml",
]

def get_text(element, name):
    child = element.find(name)
    return (child.text or "").strip() if child is not None else ""

def main():
    articles = []
    seen = set()

    for url in FEEDS:
        try:
            request = urllib.request.Request(
                url,
                headers={"User-Agent": "NewsWebsiteBot/1.0"}
            )
            with urllib.request.urlopen(request, timeout=20) as response:
                root = ET.fromstring(response.read())

            for item in root.findall(".//item"):
                title = get_text(item, "title")
                link = get_text(item, "link")
                description = get_text(item, "description")
                pub_date = get_text(item, "pubDate")

                if not title or not link or link in seen:
                    continue

                seen.add(link)
                articles.append({
                    "title": title,
                    "link": link,
                    "description": description,
                    "published": pub_date,
                    "source": url.split("/")[2],
                })

        except Exception as error:
            print(f"Could not read {url}: {error}")

    if not articles:
        raise RuntimeError(
            "No news was collected. Existing news.json was not overwritten."
        )

    articles.sort(
        key=lambda item: item["published"],
        reverse=True
    )

    output = {
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "articles": articles[:50],
    }

    Path("news.json").write_text(
        json.dumps(output, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(f"Saved {len(output['articles'])} news articles.")

if __name__ == "__main__":
    main()
