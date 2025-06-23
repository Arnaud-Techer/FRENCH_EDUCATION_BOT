import os
from pathlib import Path
from llama_index.core import (StorageContext,
                              VectorStoreIndex,
                              load_index_from_storage,
                              SimpleDirectoryReader,
                              Document,
                              DocumentSummaryIndex
                              )
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from sentence_transformers import SentenceTransformer
from llama_index.core.tools import QueryEngineTool,ToolMetadata
from llama_index.core import Settings
from llama_index.llms.ollama import Ollama
from llama_index.core.agent import ReActAgent
from register_prompt import register_prompt_engine
from scraping_bo import ScrapOfficialBulletin
from constants import *

# download the hugging face model first to avoid error
# Trigger model download and cache creation
# SentenceTransformer("BAAI/bge-small-en-v1.5",cache_folder=r"C:\Users\teche\.cache\huggingface\hub")
embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5",cache_folder=r"C:\Users\teche\.cache\huggingface\hub")
llm = Ollama(model=OLLAMA_MODEL_NAME,request_timeout=360.)

Settings.embed_model = embed_model
Settings.llm = llm

def generate_fiches_storage():
    """Generate a storage for the data using LLM and Embedding function.

    Returns:
        VectorStoreIndex: Storage of the data.
    """
    fiche_docs = SimpleDirectoryReader(DATA_FOLDER_NAME).load_data()
    # build the index
    fiche_index =VectorStoreIndex.from_documents(fiche_docs,
                                                 show_progress=True)
    # persist index
    fiche_index.storage_context.persist(persist_dir=FICHES_STORAGE_FOLDER_NAME)
    return fiche_index 

def retrieve_fiches_storage_if_possible():
    """Retrieve the storage data if the storage exists. Generate the storage otherwise.

    Returns:
        VectorStoreIndex: Storage of the data.
    """
    try:
        storage_context = StorageContext.from_defaults(
            persist_dir=FICHES_STORAGE_FOLDER_NAME
        )
        fiche_index = load_index_from_storage(storage_context)
        
        index_loaded = True
    except:
        index_loaded = False

    if not index_loaded:
        fiche_index = generate_fiches_storage()
        
    return fiche_index
    
def create_document_from_clean_body_content(clean_body_content : str) -> list[Document]:
    """Create a list of Document for the indexation in llama_index

    Args:
        clean_body_content (str): string containing the body content for the articles scrap from BO website.

    Returns:
        list[Document]: list of Document that can be indexing by llama_index to be use in the RAG
    """
    return [Document(id='bulletin-officiel',text=clean_body_content)]

def generate_bo_storage():
    """Generate a storage for the Official Bulletin data retrivied using web scraping.

    Returns:
        DocumentSummaryIndex: Storage of the Official Bulletin data.
    """
    # initiate the object for web scraping the BO official website.
    scrape_bo = ScrapOfficialBulletin(chrome_driver_path=CHROME_DRIVER_PATH)
    # retrive web links to the 3 latest versions of the BO
    last_bo_links = scrape_bo.extract_website_link_last_bo()
    # extract links to the different articles inside each BO
    links_to_articles = scrape_bo.extract_article_links(last_bo_links)
    # extract the html content for all articles
    html_content = scrape_bo.scrape_article(links_to_articles)
    # filter the html content to keep the body of it
    body_content = scrape_bo.extract_body_content(html_content)
    # clean the body content to supress style and script informations
    cleaned_body_content = scrape_bo.clean_body_content(body_content)
    # create a Document from the extracted content
    documents = create_document_from_clean_body_content(cleaned_body_content)
    # generate the storage based on this Document
    summary_index = DocumentSummaryIndex.from_documents(documents,llm=llm,show_progress=False)
    summary_index.storage_context.persist(BO_STORAGE_FOLDER_NAME)
    return summary_index

def retrieve_fiches_storage_if_possible():
    """Retrieve the storage data from the BO if the storage exists. Generate the BO storage otherwise.

    Returns:
        DocumentSummaryIndex: Storage of the Official Bulletin data.
    """
    try:
        storage_context_bo = StorageContext.from_defaults(
            persist_dir=BO_STORAGE_FOLDER_NAME
        )
        summary_index = load_index_from_storage(storage_context_bo)
        
        index_loaded_bo = True
    except:
        index_loaded_bo = False
    
    if not index_loaded_bo:
        summary_index = generate_bo_storage()
    return summary_index


fiche_index = retrieve_fiches_storage_if_possible()
fiche_engine = fiche_index.as_query_engine()

summary_index = retrieve_fiches_storage_if_possible()
bo_engine = summary_index.as_query_engine()

tools = [
    register_prompt_engine,
    QueryEngineTool(
        query_engine=fiche_engine,
        metadata= ToolMetadata(
            name='fiche_revision_ecole',
            description="""Ces documents contiennent les informations importantes concernant le fonctionnement de l ecole.
            Ils sont a utiliser pour connaitre les valeurs de l ecole, savoir comment des eleves sont gerees, comment les orientes 
            dans le systeme scolaire ou encore connaitre les procedures existantes au sein de l ecole francaise.
            """
        )
    ),
    QueryEngineTool(
        query_engine=bo_engine,
        metadata=ToolMetadata(
            name="bulletin_officielle_education_nationale",
            description="""Ces documents contiennent tous les derniers articles issus des 3 derniers bulletin officiel 
            directement issus du site de l'éducation nationale. Ces bulletins officielles sont à utiliser lorsque l'utilisateur 
            demande des résumés sur les bulletins officielles et sur les actualités du métier.
            """
        )
    )
]
agent = ReActAgent.from_tools(tools=tools,llm=llm,verbose=False,context=context)