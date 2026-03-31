import re
from urllib.parse import urljoin, urlparse, parse_qs, unquote
import aiohttp
import asyncio
import random
from bs4 import BeautifulSoup
import requests
import nltk



class PolicyCrawler:
    def __init__(self, reopuri, depth=1, concurrency=5):
        self.reopuri = reopuri
        self.reopuri = self._normalize_url(self.reopuri)
        self.repo_html = requests.get(reopuri).content
        self.repo_links = {}
        self.policy_links ={}
        self.visited = {self.reopuri} # initial set
        self.sem = asyncio.Semaphore(concurrency)
        self.depth = depth

        self.stemmer = nltk.stem.SnowballStemmer('english')

        self.policy_terms = [
            'act',
            'agreement',
            'charter',
            'code',
            'condition',
            'constitution',
            'contract',
            'declaration',
            'directive',
            'guide',
            'guideline',
            'licence',
            'license',
            'manual',
            'note',
            'notice',
            'plan',
            'policy',
            'principle',
            'regulation',
            'rule',
            'statement',
            'statute',
            'strategy',
            'term'
        ]
        #some additional terms typically used to indicate terms, policies etc
        self.policy_terms.extend([
            'information',
            'intellectual',
            'legal',
            'liability',
            'moderation',
            'permission',
            'personal',
            'privacy',
            'prohibited',
            'property',
            'restriction',
            'right',
            'security',
            'share',
            'tos',
            'tracking',
            'transparency',
            'use',
        ]
        )
        self.policy_stems = [self.stemmer.stem(t) for t in self.policy_terms]
        #self.set_repo_links()

    def _normalize_url(self,  link: str, filter_query = True):
        """
        Safely completes a relative URL against a base page URL and removes e.g. trailing slashes
        """
        normalized_url = None
        if not link or not isinstance(link, str):
            return None  # skip empty hrefs
        # ignore javascript links or mailto links
        link = link.strip()
        if link.lower().startswith(("javascript:", "mailto:")):
            return None
        # Handle fragment-only links (e.g., "#section") by joining with base page URL
        normalized_url = urljoin(self.reopuri, link)
        # ignore links that result in an empty or malformed URL
        # in case filter_query is set to true also skip links which contain query params
        parsed = urlparse(normalized_url)
        normalized = parsed._replace(
            fragment="",
            query=""
        )
        # normalize URL
        normalized_url = normalized.geturl().rstrip("/")
        params = parse_qs(parsed.query,keep_blank_values=True)
        if filter_query and 'q' in params or 'query' in params:
            return None
        if not parsed.scheme or not parsed.netloc:
            return None
        return normalized_url


    def _url_to_string(self, url: str):
        # returns a string which consists of word-like entities extracted from a URL
        url = unquote(url)
        url = re.sub(r"[^A-Za-z]+", " ", url)
        url = re.sub(r'([A-Z])', r' \1', url)
        url = re.sub(r"\b\w{1,3}\b", " ", url)
        url = re.sub(r'\s+', r' ', url)
        url = url.replace('https ', '').replace('http ', '')
        return url.lower()

    def _contains_policy_term(self, string: str):
        for word in string.split():
            if self.stemmer.stem(word) in self.policy_stems:
                return True
        return False


    async def crawl(self):
        visited = set()
        async with aiohttp.ClientSession(
            headers={"User-Agent": "PolicyCrawler/1.0"}
        ) as session:
            await self._crawl_page(
                session,
                self.reopuri,
                self.repo_html,
                self.depth
            )


    async def _crawl_page(self, session, url, html, level):
        print(url)
        soup = BeautifulSoup(html, "html.parser")
        tasks = []
        for a_href in soup.find_all("a", href=True):
            link_url = self._normalize_url(a_href["href"])
            link_text = a_href.text.strip()
            if not link_url:
                continue
            if link_url in self.visited:
                continue
            self.visited.add(link_url)
            self.repo_links[link_url] = link_text
            # check if other policy like links exist in policy like web pages
            is_policy_like = (
                    self._contains_policy_term(self._url_to_string(link_url)) or
                    self._contains_policy_term(link_text.lower())
            )

            if is_policy_like:
                self.policy_links[link_url] = {'link_text': link_text, 'page_content': html}

            if level > 0 and is_policy_like:
                tasks.append(
                    self._fetch_and_crawl(
                        session,
                        link_url,
                        level - 1
                    )
                )
        if tasks:
            await asyncio.gather(*tasks)

    async def _fetch_and_crawl(self, session, url, level):
        async with self.sem:
            await asyncio.sleep(random.uniform(0.3, 1.2))
            try:
                async with session.get(url, timeout=10) as response:
                    if response.status != 200:
                        return
                    if "text/html" not in response.headers.get("content-type", ""):
                        return
                    html = await response.text()
            except Exception:
                return

        await self._crawl_page(session, url, html, level)

crawler = PolicyCrawler("https://ssh.datastations.nl/", depth=2)

asyncio.run(crawler.crawl())

print([v.get("link_text") for l,v in crawler.policy_links.items()])