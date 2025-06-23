#LLM MODEL USE FOR THE AI AGENT
HUGGINGFACE_MODEL_NAME = "BAAI/bge-small-en-v1.5"
OLLAMA_MODEL_NAME = 'llama3.1:8b'

# FOLDER NAMES FOR THE STORAGE OF THE DATA 
DATA_FOLDER_NAME = "./data"
FICHES_STORAGE_FOLDER_NAME = "./storage/fiches"
BO_STORAGE_FOLDER_NAME = "./storage/bo"

# DESCRIPTION OF THE CONTEXT FOR THE AI AGENT
context = """But : Le principal objectif de cet agent est d'assister l'utilisateur dans son apprentissage pour le concours de CPE.
Il fournit des informations precises sur le fonctionnement de l ecole ainsi que sur les principes fondamentaux de son fonctionnement."""

# PATH TO THE CHROME DRIVER NEEDED TO DO THE WEB SCRAPING.
CHROME_DRIVER_PATH = "chromedriver-win64/chromedriver.exe"