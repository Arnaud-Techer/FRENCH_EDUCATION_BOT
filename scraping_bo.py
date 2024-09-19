import selenium.webdriver as webdriver
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
import time

def contains_any(link:str,sublinks:list[str]) -> bool:
    """Check if there is any element of a list sublinks inside a str link

    Args:
        link (str): link in which we are looking for specific str
        sublinks (list[str]): list of str that we want to check in the link

    Returns:
        bool: return True if a sublink in the list is in the list and False if not
    """
    for sublink in sublinks:
        if sublink in link:
            return True
    return False


class ScrapOfficialBulletin:
    """Class that do the scraping to retrieve important data in the official bulletin.
    """
    
    WEBSITE_TO_SCRAP = "https://www.enseignementsup-recherche.gouv.fr/fr/bulletin-officiel"
    
    def __init__(self,chrome_driver_path:str):
        self.chrome_driver_path = chrome_driver_path
        self.options = webdriver.ChromeOptions()
        self.options.add_argument("--headless")
        
    def extract_website_link_last_bo(self):
        """Scrape the official french government website to extract links for the last available BO
        
        Returns:
            List[str]: list of website link to the different last BO
        """
        driver = webdriver.Chrome(service=Service(self.chrome_driver_path),options=self.options)
        print("Launching chrome browser....")
        last_bo_links = list()
        try: 
            driver.get(self.WEBSITE_TO_SCRAP)
            print("Page loaded...")
            # identify the title where the last BO are
            html_content = driver.page_source
            soup = BeautifulSoup(html_content,"html.parser")
            all_links = soup.find_all("a")
            # in the filtered link we will have links to the 3 lastest BO
            last_bo_links = list()
            for link in all_links:
                if link.get('href') and "https://www.enseignementsup-recherche.gouv.fr/fr/bo" in link['href'] :
                    last_bo_links.append(link["href"])         
        finally:
            driver.quit()
        return last_bo_links
        

    def extract_article_links(self,last_bo_links:list[str]) -> list[str]:
        """Extract the website link to the articles from every link in a BO link list

        Args:
            last_bo_links (list[str]): list of website links to BO

        Returns:
            list[str]: list of website links to the articles that we find in each BO
        """
        driver = webdriver.Chrome(service=Service(self.chrome_driver_path),options=self.options)
        print("Launching chrome browser....")
        links_to_articles = list()
        try:
            for link in last_bo_links:
                print(link)
                driver.get(link)
                html_content = driver.page_source
                soup  = BeautifulSoup(html_content,"html.parser")
                all_links = soup.find_all("a")
                for link in all_links:
                    if link.get("href") and contains_any(link["href"],["MEN","CTNR","ESRR"]):
                        links_to_articles.append(link["href"])
        finally:
            driver.quit()
        return links_to_articles 

    def scrape_article(self,links_to_articles:list[str]) -> str:
        """Scrape all the informations in all article website indicated in the list

        Args:
            links_to_articles (list[str]): list of website link for the article to scrap

        Returns:
            str: contain a join of all the source page for each article 
        """
        htmls = list()
        driver = webdriver.Chrome(service=Service(self.chrome_driver_path),options=self.options)
        print("Launching chrome browser....")
        try:
            for article in [f"https://www.enseignementsup-recherche.gouv.fr{article_website}" for article_website in links_to_articles]:
                driver.get(article)
                print("Article loaded....")
                print(article)
                html = driver.page_source
                htmls.append(html)
        finally:
            driver.quit()
        return "".join(htmls)
    
    @staticmethod
    def extract_body_content(html_content:str) -> str:
        """Extract the body content of the join of all source pages for articles

        Args:
            html_content (str): html content create with a join of all html website article

        Returns:
            str: return only the body content of the html code
        """
        soup = BeautifulSoup(html_content,"html.parser")
        body_content = soup.body
        if body_content:
            return str(body_content)
        return ""

    @staticmethod
    def clean_body_content(body_content: str) -> str:
        """Clean the body content of the articles

        Args:
            body_content (str): body content of all the articles scraped

        Returns:
            str: cleaned body content without script, style information and empty lines
        """
        soup = BeautifulSoup(body_content,"html.parser")
        for script_or_style in soup(["script","style"]):
            script_or_style.extract()
        cleaned_body_content = soup.get_text(separator="\n")
        cleaned_body_content = "\n".join(line.strip() for line in cleaned_body_content.splitlines() if line.strip()
                                        )
        return cleaned_body_content
        
    