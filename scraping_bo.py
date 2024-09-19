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

def extract_last_bo_link(website : str ="https://www.enseignementsup-recherche.gouv.fr/fr/bulletin-officiel") -> list[str] :
    """Scrape a specific website to extract links for the last available BO

    Args:
        website (str, optional): link where we can find the official bulletin for schools. Defaults to "https://www.enseignementsup-recherche.gouv.fr/fr/bulletin-officiel".

    Returns:
        List[str]: list of website link to the different last BO
    """
    chrome_driver_path = "chromedriver-win64/chromedriver.exe"
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    driver = webdriver.Chrome(service=Service(chrome_driver_path),options=options)
    print("Launching chrome browser....")
    link_to_last_BO = list()
    try: 
        driver.get(website)
        print("Page loaded...")
        # identify the title where the last BO are
        html_content = driver.page_source
        soup = BeautifulSoup(html_content,"html.parser")
        all_links = soup.find_all("a")
        # in the filtered link we will have links to the 3 lastest BO
        link_to_last_BO = list()
        for link in all_links:
            if link.get('href') and "https://www.enseignementsup-recherche.gouv.fr/fr/bo" in link['href'] :
                link_to_last_BO.append(link["href"])         
    finally:
        driver.quit()
    return link_to_last_BO

def extract_article_links(link_to_last_BO:list[str]) -> list[str]:
    """Extract the website link to the articles from every link in a BO link list

    Args:
        link_to_last_BO (list[str]): list of website link to a BO

    Returns:
        list[str]: list of website link to the articles that we find in each BO
    """
    chrome_driver_path = "chromedriver-win64/chromedriver.exe"
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    driver = webdriver.Chrome(service=Service(chrome_driver_path),options=options)
    print("Launching chrome browser....")
    link_to_article = list()
    try:
        for link in link_to_last_BO:
            print(link)
            driver.get(link)
            html_content = driver.page_source
            soup  = BeautifulSoup(html_content,"html.parser")
            all_links = soup.find_all("a")
            for link in all_links:
                if link.get("href") and contains_any(link["href"],["MEN","CTNR","ESRR"]):
                    link_to_article.append(link["href"])
    finally:
        driver.quit()
    return link_to_article 

def scrape_article(article_link:list[str]) -> str:
    """Scrape all the informations in all article website indicated in the list

    Args:
        article_link (list[str]): list of website link for the article to scrap

    Returns:
        str: contain a join of all the source page for each article 
    """
    htmls = list()
    chrome_driver_path = "chromedriver-win64/chromedriver.exe"
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    driver = webdriver.Chrome(service=Service(chrome_driver_path),options=options)
    print("Launching chrome browser....")
    try:
        for article in [f"https://www.enseignementsup-recherche.gouv.fr{article_website}" for article_website in article_link]:
            driver.get(article)
            print("Article loaded....")
            print(article)
            html = driver.page_source
            htmls.append(html)
    finally:
        driver.quit()
    return "".join(htmls)
    
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
        
def split_dom_content(dom_content:str,max_lenght=6000) -> list[str]:
    """Split the cleaned content into a list of maximum max_lenght string

    Args:
        dom_content (str): cleaned body content of the articles
        max_lenght (int, optional): lenght to split the string content. Defaults to 6000.

    Returns:
        list[str]: list of all the split cleaned content
    """
    return [
        dom_content[i: i+max_lenght] for i in range(0,len(dom_content))
    ]
    
    