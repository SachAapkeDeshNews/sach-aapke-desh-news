
import json
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

FEEDS = [
    "https://feeds.bbci.co.uk/news/rss.xml",
    "https://rss.nytimes.com/services/xml/rss/nyt/World.xml",
]

def read_text(item, tag):
    node = item.find(tag)
    return (node.text or "").strip() if node is not None else ""

def main():
    articles = []
    seen_links = set()

    for feed_url in FEEDS:
        try:
            request = urllib.request.Request(
                feed_url,
                headers={"User-Agent": "SachAapkeDeshNews/1.0"},
            )
            with urllib.request.urlopen(request, timeout=25) as response:
                root = ET.fromstring(response.read())

            for item in root.findall(".//item"):
                title = read_text(item, "title")
                link = read_text(item, "link")

                if not title or not link or link in seen_links:
                    continue

                seen_links.add(link)
                articles.append({
                    "title": title,
                    "link": link,
                    "description": read_text(item, "description"),
                    "published": read_text(item, "pubDate"),
                    "source": feed_url.split("/")[2],
                })

        except Exception as error:
            print(f"Feed failed: {feed_url}: {error}")

    if not articles:
        raise RuntimeError("No news collected; news.json was not changed.")

    articles.sort(
        key=lambda article: article["published"],
        reverse=True,
    )

    output = {
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "articles": articles[:50],
    }

    Path("news.json").write_text(
        json.dumps(output, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(f"Successfully saved {len(output['articles'])} articles.")

if __name__ == "__main__":
    main()
