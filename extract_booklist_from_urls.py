# Utility script to parse booklist and generate a list / spreadsheet with following info extrated
# - Title
# - Author
# - ISBN
# https://sites.google.com/shs.org/shslssummerreading2025/b-k

import pandas as pd
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, parse_qs

# ======= STEP 1: Scape booklist google-site to parse book urls =======
# Scraping strategy
# Since each book has a image for the cover, and the link to the book isn't following standard hyperlink structure (by scraping <a> tags),
# we use following way to scrape the nested hyperlink url to each book's detailed page
# Instead of only scraping <a> tags, we’ll:
# 1. Find all <img> tags in your HTML.
# 2. For each <img>, trace its parent chain up to the ancestor that’s a clickable link (<a href="...">).
# 3. Extract both the src (image URL) and the href (detail page URL).
# 4. Use the detail URLs to scrape title / author / ISBN, as before.

# Reload the HTML file
file_path = "SHS LS Summer Reading 2025 - B & K.html"   # Put the saved html page to the same folder as script
with open(file_path, "r", encoding="utf-8") as f:
    soup = BeautifulSoup(f, "html.parser")

# Enhanced scraping: trace <img> to clickable ancestors <a>
results = []
base_url = "https://sites.google.com/shs.org/shslssummerreading2025/b-k"

for img in soup.find_all('img'):
    img_src = img.get('src')
    parent = img.parent
    link = None

    while parent and parent.name != 'body':
        if parent.name == 'a' and parent.get('href'):
            link = parent['href']
            break
        parent = parent.parent

    if img_src and link:
        full_link = urljoin(base_url, link)
        results.append({
            "Cover Image": img_src,
            "Book Detail URL": full_link
        })

df_links = pd.DataFrame(results)

# Decode the Google redirect URLs to get the real book links
df_links["Clean URL"] = df_links["Book Detail URL"].apply(
    lambda x: parse_qs(urlparse(x).query).get("q", [""])[0]
)

# Keep only unique cleaned URLs
df_cleaned = df_links[["Clean URL"]].drop_duplicates().rename(columns={"Clean URL": "Book Detail URL"})

print(df_cleaned)
# Save to CSV for external use
df_cleaned.to_csv("cleaned_book_urls.csv", index=False)
print("Saved to cleaned_book_urls.csv")


# ======= STEP 2: Paste your book detail URLs here =======
book_urls = df_cleaned["Book Detail URL"].dropna().unique().tolist()

# ======= STEP 3: Function to extract metadata =======

def extract_book_info_enhanced(url):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 " +
                        "(KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
        }

        resp = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(resp.text, "html.parser")

        # 1. Meta tags (OG and itemprop)
        title = soup.find("meta", property="og:title")
        title = title["content"] if title else ""
        author = soup.find("meta", attrs={"name": "author"})
        author = author["content"] if author else ""

        # 2. Visible title/author if meta missing
        if not title:
            h1 = soup.find("h1")
            title = h1.get_text(strip=True) if h1 else ""
        if not author:
            # common selectors: byline, .author, span[itemprop='author']
            author_el = soup.select_one(".author, span[itemprop='author'], .byline")
            author = author_el.get_text(strip=True) if author_el else ""

        # 3. ISBN from page text
        isbn_match = re.search(r"\b97[89][\d\-]{10,}\b", resp.text)
        isbn = isbn_match.group(0) if isbn_match else ""

        print(f"Extracting book: {title}\n")
        return {"Title": title, "Author": author, "ISBN": isbn, "Source URL": url}
    except Exception:
        return {"Title": "-ERROR-", "Author": "", "ISBN": "", "Source URL": url}


# ======= STEP 3: Process and export =======
book_info = [extract_book_info_enhanced(url) for url in book_urls]
df = pd.DataFrame(book_info)

# Save to CSV
df.to_csv("summer_reading_books.csv", index=False)
print("Saved to summer_reading_books.csv")
