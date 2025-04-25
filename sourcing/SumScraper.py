import requests
from bs4 import BeautifulSoup
import re

class SumScraper:
    def __init__(self):
        self.wiki_base_url = "https://en.wikipedia.org/w/api.php"
        self.wikidata_base_url = "https://www.wikidata.org/w/api.php"

    def get_wikipedia_summary(self, movie_title, director_name=None, imdb_id=None):
        """
        Fetches all relevant information about a movie from Wikipedia, including plot, synopsis, themes, and analysis.

        Args:
            movie_title (str): The title of the movie.
            director_name (str, optional): The director's name to refine Wikipedia search.
            imdb_id (str, optional): The IMDb ID of the movie.

        Returns:
            dict: A dictionary containing relevant sections from the Wikipedia page.
        """
        # Step 1: Get Wikipedia page title from Wikidata using IMDb ID (if available)
        page_title = None
        if imdb_id:
            page_title = self.get_wikipedia_page_from_wikidata(imdb_id)

        # Step 2: If Wikidata fails, search Wikipedia by title + director
        if not page_title:
            page_title = self.search_wikipedia_page(movie_title, director_name)

        if not page_title:
            return {"error": f"No Wikipedia page found for '{movie_title}'"}

        # Step 3: Fetch the table of contents (sections)
        sections = self.get_wikipedia_sections(page_title)
        if not sections:
            return {"error": f"No sections found for '{page_title}'"}

        # Step 4: Filter and fetch relevant sections
        relevant_sections = self.filter_relevant_sections(sections)
        if not relevant_sections:
            return {"error": f"No relevant content found for '{page_title}'"}

        details = self.fetch_section_content(page_title, relevant_sections)
        return details if details else {"error": f"No detailed content retrieved for '{page_title}'"}

    def get_wikipedia_page_from_wikidata(self, imdb_id):
        """Fetches the Wikipedia page title from Wikidata using the IMDb ID."""
        params = {
            "action": "wbgetentities",
            "format": "json",
            "props": "sitelinks",
            "sites": "enwiki",
            "ids": f"P345:{imdb_id}"  # P345 is the IMDb ID property in Wikidata
        }
        response = requests.get(self.wikidata_base_url, params=params)
        if response.status_code == 200:
            data = response.json()
            entities = data.get("entities", {})
            for entity in entities.values():
                site_links = entity.get("sitelinks", {})
                if "enwiki" in site_links:
                    return site_links["enwiki"]["title"]
        return None

    def search_wikipedia_page(self, movie_title, director_name):
        """Searches Wikipedia for the movie title."""
        search_query = f"{movie_title} {director_name}" if director_name else movie_title
        search_params = {
            "action": "query",
            "list": "search",
            "srsearch": search_query,
            "format": "json"
        }
        response = requests.get(self.wiki_base_url, params=search_params)
        if response.status_code == 200:
            results = response.json().get("query", {}).get("search", [])
            return results[0]["title"] if results else None
        return None

    def get_wikipedia_sections(self, page_title):
        """Fetches the sections of a Wikipedia page."""
        content_params = {
            "action": "parse",
            "page": page_title,
            "prop": "sections",
            "format": "json"
        }
        response = requests.get(self.wiki_base_url, params=content_params)
        if response.status_code == 200:
            return response.json().get("parse", {}).get("sections", [])
        return None

    def filter_relevant_sections(self, sections):
        """Filters sections based on relevant keywords."""
        keywords = ["plot", "synopsis", "theme", "analysis", "story", "overview"]
        return [s for s in sections if any(kw in s["line"].lower() for kw in keywords)]

    def fetch_section_content(self, page_title, sections):
        """Fetches the content of relevant sections."""
        details = {}
        for section in sections:
            section_id = section["index"]
            section_title = section["line"]

            section_params = {
                "action": "parse",
                "page": page_title,
                "section": section_id,
                "prop": "text",
                "format": "json"
            }
            response = requests.get(self.wiki_base_url, params=section_params)
            if response.status_code == 200:
                section_html = response.json().get("parse", {}).get("text", {}).get("*", "")
                details[section_title] = self.strip_html_tags(section_html)
        return details

    def strip_html_tags(self, html_content):
        """Cleans HTML content and removes unwanted artifacts."""
        soup = BeautifulSoup(html_content, "html.parser")

        # Remove footnotes and references
        for sup in soup.find_all("sup", class_="reference"):
            sup.decompose()

        # Extract plain text and clean up
        text = soup.get_text(separator="\n")
        text = re.sub(r"\[\nedit\n\]", "", text)  # Remove "[edit]"
        text = re.sub(r"\n+", "\n", text)  # Replace multiple newlines with a single newline
        text = re.split(r"\^\s*\n", text, maxsplit=1)[0]  # Split at the first caret and remove everything after it
        text = re.sub(r"\n+", "\n", text)  # Replace multiple newlines with a single newline
        text = text.strip()  # Remove leading and trailing whitespace

        return text