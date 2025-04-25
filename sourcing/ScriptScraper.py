from urllib.parse import urljoin
import pymupdf
import requests
from bs4 import BeautifulSoup
from io import BytesIO
from PyPDF2 import PdfReader 



class ScriptScraper:
    def __init__(self):
        self.dailyscript_base_url = "https://www.dailyscript.com/movie.html"
        self.dailyscript_second_url ="https://www.dailyscript.com/movie_n-z.html"
        self.dailyscript_site_url = "https://www.dailyscript.com/"
        self.sfy_base_url = "https://sfy.ru/scripts"
        self.sfy_site_url = "https://sfy.ru"
    
    def pdf_to_text(self, pdf_path):
        text = ""
        try:
            pdf_document = pymupdf.open(pdf_path)
            for page_num in range(pdf_document.page_count):
                page = pdf_document[page_num]
                text += page.get_text()
            pdf_document.close()
        except Exception as e:
            print(f"An error occurred: {e}")
        return text

    def sfy_get(self, title, imdb_id):
        """
        Fetches the script text from sfy.ru for the given movie title and IMDb ID.
        
        Args:
            title (str): The movie title to search for (e.g., "Ace Ventura: Pet Detective").
            imdb_id (str): The IMDb ID of the movie (e.g., "tt0109040").
        
        Returns:
            str: The script text if found, or None if not found.
        """
        try:
            # Step 1: Fetch the main scripts page
            response = requests.get(self.sfy_base_url)
            if response.status_code != 200:
                return f"Failed to fetch SFY scripts page. Status code: {response.status_code}"

            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Step 2: Search for the movie title
            movie_link = None
            links = soup.find_all('a', href=True)
            for link in links:
                if title.lower() in link.text.lower():
                    movie_link = urljoin(self.sfy_site_url, link['href'])
                    break
            
            if not movie_link:
                return None  # Movie title not found
            # Step 3: Navigate to the movie's page
            movie_page_url = f"{movie_link}"
            movie_response = requests.get(movie_page_url)
            if movie_response.status_code != 200:
                return f"Failed to fetch the movie page at {movie_page_url}. Status code: {movie_response.status_code}"

            movie_soup = BeautifulSoup(movie_response.content, 'html.parser')

            # Step 4: Verify IMDb ID on the movie page
            imdb_link = movie_soup.find('a', href=True, text="More info about this movie on IMDb.com")
            if not imdb_link or imdb_id not in imdb_link['href']:
                return None  # IMDb ID does not match

            # Step 5: Check for a PDF link
            pdf_link = movie_soup.find('a', href=lambda href: href and href.lower().endswith('.pdf'))
            if pdf_link:
                pdf_url = pdf_link['href']
                if not pdf_url.startswith("http"):
                    pdf_url = urljoin(self.sfy_site_url, pdf_url)
                
                # Check if the PDF actually exists
                pdf_response = requests.head(pdf_url)
                if pdf_response.status_code == 404:
                    return None 

                return self.fetch_pdf_script(pdf_url)

            # Step 6: Extract the script after "FOR EDUCATIONAL PURPOSES ONLY"
            script_text = movie_soup.get_text(separator="\n")
            split_text = script_text.split("FOR EDUCATIONAL PURPOSES ONLY")
            if len(split_text) > 1:
                return split_text[1].strip()  # Return the script content after the marker

            return None  # If no script is found
        except Exception as e:
            return f"An error occurred: {str(e)}"

    def dailyscript_get(self, imdb_id):
        """
        Fetches the script text from Daily Script for the given IMDb ID.
        
        Args:
            imdb_id (str): The IMDb ID of the movie (e.g., "tt0298203").
            
        Returns:
            str: The script text if found, or an error message if not found.
        """
        try:
            # Fetch the main page with the list of scripts
            for url in [self.dailyscript_base_url, self.dailyscript_second_url]:
                response = requests.get(url)
                if response.status_code != 200:
                    return f"Failed to fetch Daily Script page. Status code: {response.status_code}"
                
                soup = BeautifulSoup(response.content, 'html.parser')
                rows = soup.find_all('a')  # Assuming links are in <a> tags
                
                # Search for the script using the IMDb ID
                for link in rows:
                    href = link.get('href')
                    if href and 'imdb.com/' in href:
                        # Extract IMDb ID from 'title/ttXXXXXXX' or similar formats
                        if 'imdb.com/title/' in href:
                            imdb_id_part = href.split('imdb.com/title/tt')[-1]
                        elif 'imdb.com/Title?' in href:
                            imdb_id_part = href.split('imdb.com/Title?')[-1]
                        else:
                            continue  # Skip unrelated links
                        
                        # Extract the valid IMDb ID (ttXXXXXXX) from the part before any extra data
                        extracted_id = imdb_id_part.split('/')[0].split('?')[0]  # Split by '/' or '?'
                                        
                        # Check if the extracted IMDb ID matches the target
                        if extracted_id == imdb_id:
                            # Find the script link (previous <a> tag)
                            parent = link.find_parent()
                            all_links = parent.find_all('a', href=True)
                            for sibling_link in all_links:
                                if sibling_link != link:
                                    script_link = sibling_link.get('href')
                                    if script_link:
                                        # Add the base URL and fetch the script
                                        full_script_url = self.dailyscript_site_url + script_link
                                        if script_link.lower().endswith('.pdf'):  # Convert to lowercase for case-insensitive check
                                            return self.fetch_pdf_script(full_script_url)
                                        else:  # Assume it's an HTML script
                                            return self.fetch_html_script(full_script_url)
            return None
        except Exception as e:
            return f"An error occurred: {str(e)}"
        

    def fetch_html_script(self, script_url):
        """
        Fetches the script text from an HTML script URL.
        
        Args:
            script_url (str): The full URL to the HTML script.
            
        Returns:
            str: The content of the script as plain text.
        """
        try:
            response = requests.get(script_url)
            if response.status_code != 200:
                return f"Failed to fetch script from {script_url}. Status code: {response.status_code}"
            
            # Parse the script page
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Extract all text from the body (you may need to adjust this based on the page structure)
            script_content = soup.get_text(separator="\n")
            return script_content.strip()
        except Exception as e:
            return f"An error occurred while fetching the HTML script: {str(e)}"

    def fetch_pdf_script(self, script_url):
        """
        Fetches the script text from a PDF script URL.
        
        Args:
            script_url (str): The full URL to the PDF script.
            
        Returns:
            str: The extracted text from the PDF.
        """
        try:
            response = requests.get(script_url)
            if response.status_code != 200:
                return f"Failed to fetch PDF script from {script_url}. Status code: {response.status_code}"
            
            # Read the PDF content
            pdf_content = BytesIO(response.content)
            pdf_reader = PdfReader(pdf_content)
            
            # Extract text from each page
            script_text = ""
            for page in pdf_reader.pages:
                script_text += page.extract_text()
            
            return script_text.strip()
        except Exception as e:
            return f"An error occurred while fetching the PDF script: {str(e)}"


