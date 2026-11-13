import re
import urllib.parse
from bs4 import BeautifulSoup
import httpx

EMAIL_REGEX = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")

class LeadScraper:
    def __init__(self):
        self.headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            )
        }

    def search_businesses(self, niche: str, location: str, max_results: int = 15) -> list:
        """Searches DuckDuckGo HTML for business listings and websites in that niche & location."""
        query = f"{niche} in {location}"
        encoded_query = urllib.parse.quote_plus(query)
        url = f"https://html.duckduckgo.com/html/?q={encoded_query}"

        leads = []
        try:
            with httpx.Client(headers=self.headers, timeout=12.0, follow_redirects=True) as client:
                res = client.get(url)
                soup = BeautifulSoup(res.text, "html.parser")

                results = soup.select(".result")
                for r in results[:max_results]:
                    title_elem = r.select_one(".result__title a")
                    snippet_elem = r.select_one(".result__snippet")
                    url_elem = r.select_one(".result__url")

                    if not title_elem:
                        continue

                    title = title_elem.get_text(strip=True)
                    snippet = snippet_elem.get_text(strip=True) if snippet_elem else ""
                    raw_href = title_elem.get("href", "")

                    # Extract actual target url from DuckDuckGo redirect
                    target_url = ""
                    if "uddg=" in raw_href:
                        parsed = urllib.parse.parse_qs(urllib.parse.urlparse(raw_href).query)
                        if "uddg" in parsed:
                            target_url = parsed["uddg"][0]
                    elif raw_href.startswith("http"):
                        target_url = raw_href

                    # Filter out major directories / social hubs to focus on real target businesses
                    skipped_domains = ["yelp.com", "tripadvisor.com", "wikipedia.org", "yellowpages.com", "facebook.com", "instagram.com", "linkedin.com"]
                    if any(d in target_url.lower() for d in skipped_domains):
                        continue

                    leads.append({
                        "name": title.split("-")[0].split("|")[0].strip(),
                        "company": title.split("-")[0].split("|")[0].strip(),
                        "website": target_url,
                        "email": "",
                        "phone": "",
                        "status": "New",
                        "notes": f"Niche: {niche} | Loc: {location} | Info: {snippet[:120]}"
                    })
        except Exception as e:
            print(f"Error searching DuckDuckGo: {e}")

        return leads

    def deep_crawl_emails(self, website_url: str) -> str:
        """Visits website homepage and /contact or /about page to extract public business email."""
        if not website_url or not website_url.startswith("http"):
            return ""

        found_emails = set()
        pages_to_check = [website_url]
        clean_base = website_url.rstrip("/")
        pages_to_check.extend([f"{clean_base}/contact", f"{clean_base}/about-us", f"{clean_base}/about"])

        try:
            with httpx.Client(headers=self.headers, timeout=8.0, follow_redirects=True, verify=False) as client:
                for p in pages_to_check[:3]:
                    try:
                        r = client.get(p)
                        if r.status_code == 200:
                            # 1. Search mailto: links
                            soup = BeautifulSoup(r.text, "html.parser")
                            for a in soup.find_all("a", href=True):
                                if a["href"].startswith("mailto:"):
                                    em = a["href"].replace("mailto:", "").split("?")[0].strip()
                                    if "@" in em and not any(skip in em.lower() for skip in [".png", ".jpg", "example.com", "sentry.io", "wixpress.com"]):
                                        found_emails.add(em)

                            # 2. Regex scan full text
                            matches = EMAIL_REGEX.findall(r.text)
                            for m in matches:
                                if not any(skip in m.lower() for skip in [".png", ".jpg", ".webp", "example.com", "wixpress.com", "schema.org"]):
                                    found_emails.add(m)
                            
                            if found_emails:
                                break
                    except Exception:
                        continue
        except Exception:
            pass

        return list(found_emails)[0] if found_emails else ""

    def scrape_and_enrich(self, niche: str, location: str, max_leads: int = 10) -> list:
        """Full pipeline: searches businesses and crawls their sites for emails."""
        raw_leads = self.search_businesses(niche, location, max_results=max_leads * 2)
        enriched = []
        for l in raw_leads:
            if len(enriched) >= max_leads:
                break
            site = l.get("website")
            if site:
                email_found = self.deep_crawl_emails(site)
                if email_found:
                    l["email"] = email_found
            enriched.append(l)

        return enriched
