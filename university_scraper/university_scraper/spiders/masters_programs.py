import scrapy
import spacy

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

class MastersProgramsSpider(scrapy.Spider):
    name = "masters_programs"
    
    # Start URLs (modify this to include relevant university URLs)
    start_urls = [
        'https://www.lmu.de/en/study/all-degrees-and-programs/international-degree-programs/',  # Example URL, replace with actual university URLs
    ]

    # Define the depth limit for scraping
    custom_settings = {
        'DEPTH_LIMIT': 2,  # Set to 2 levels deep
        'DOWNLOAD_DELAY': 2,  # Add 2 second delay between requests
        'RANDOMIZE_DOWNLOAD_DELAY': True,  # Randomize the delay
        'CONCURRENT_REQUESTS': 1,  # Limit concurrent requests
        'RETRY_TIMES': 3,  # Retry failed requests up to 3 times
        'RETRY_HTTP_CODES': [500, 502, 503, 504, 408, 429]  # Retry on these HTTP codes
    }

    def parse(self, response):
        # Ensure the response is valid
        if response.status != 200:
            self.logger.warning(f"Failed to load {response.url} - Status: {response.status}")
            return

        # Extract all links on the page
        links = response.css("a::attr(href)").getall()
        for link in links:
            # Join the link with the base URL if it is a relative path
            full_link = response.urljoin(link)

            # Use the NLP function to check if the link is relevant
            if self.is_relevant_link(full_link):
                # Display message in the terminal
                self.logger.info(f"Scraping relevant link: {full_link}")
                
                # Recursively parse the relevant page
                yield scrapy.Request(url=full_link, callback=self.parse_masters_page)
            else:
                self.logger.info(f"Skipping irrelevant link: {full_link}")

    def parse_masters_page(self, response):
        # Extract and process relevant content from a Master's program page
        program_title = response.css("h1::text").get()  # Adjust selectors as needed
        program_description = response.css("p::text").getall()
        
        yield {
            "url": response.url,
            "title": program_title,
            "description": " ".join(program_description),
        }

        # Follow additional links on the Master's page to achieve depth level 2
        links = response.css("a::attr(href)").getall()
        for link in links:
            full_link = response.urljoin(link)
            if self.is_relevant_link(full_link):
                self.logger.info(f"Scraping additional relevant link at depth 2: {full_link}")
                yield scrapy.Request(url=full_link, callback=self.parse_masters_page)
            else:
                self.logger.info(f"Skipping irrelevant link at depth 2: {full_link}")

    def is_relevant_link(self, link):
        """
        Checks if a link is related to Master's programs using NLP and skips those containing 'undergraduate'.
        """
        keywords = ["master", "graduate", "postgraduate", "m.s.", "m.sc.", "ms"]
        exclude_keywords = ["undergraduate"]

        doc = nlp(link)
        
        # Check if the link contains any excluded keywords
        if any(exclude in link.lower() for exclude in exclude_keywords):
            return False

        # Check for keyword matches
        for token in doc:
            if any(keyword in token.text.lower() for keyword in keywords):
                return True
        return False
