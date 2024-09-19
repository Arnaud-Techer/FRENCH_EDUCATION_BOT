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
from llama_index.core.tools import QueryEngineTool,ToolMetadata
from llama_index.core import Settings
from llama_index.llms.ollama import Ollama
from llama_index.core.agent import ReActAgent
from register_prompt import register_prompt_engine
from scraping_bo import *
embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")
llm = Ollama(model='llama3',request_timeout=360.)

Settings.embed_model = embed_model
Settings.llm = llm

context = """But : Le principal objectif de cet agent est d'assister l'utilisateur dans son apprentissage pour le concours de CPE.
Il fournit des informations precises sur le fonctionnement de l ecole ainsi que sur les principes fondamentaux de son fonctionnement."""

try:
    storage_context = StorageContext.from_defaults(
        persist_dir="./storage/fiches"
    )
    fiche_index = load_index_from_storage(storage_context)
    
    index_loaded = True
except:
    index_loaded = False

if not index_loaded:
    fiche_docs = SimpleDirectoryReader("data/").load_data()
    # build the index
    fiche_index =VectorStoreIndex.from_documents(fiche_docs,
                                                 show_progress=True)
    # persist index
    fiche_index.storage_context.persist(persist_dir="./storage/fiches")
    
    
# 
fiche_engine = fiche_index.as_query_engine()

def create_document_from_dom_content(dom_contents : str) -> list[Document]:
    """Create a list of Document for the indexation in llama_index

    Args:
        dom_contents (list[str]): list containing the split of the dom content

    Returns:
        list[Document]: list of Document that can be indexing by llama_index to be use in the RAG
    """
    # documents = list()
    # for i,dom_content in enumerate(dom_contents):
    #     documents.append(Document(id=f"doc{i}",text=dom_content))
    # return documents
    return [Document(id='bulletin-officiel',text=dom_contents)]

try:
    storage_context_bo = StorageContext.from_defaults(
        persist_dir="./storage/bo"
    )
    summary_index = load_index_from_storage(storage_context_bo)
    
    index_loaded_bo = True
except:
    index_loaded_bo = False
 
if not index_loaded_bo:
    link_to_bo = extract_last_bo_link()
    article_link = extract_article_links(link_to_bo)
    html_content = scrape_article(article_link)
    body_content = extract_body_content(html_content)
    cleaned_body_content = clean_body_content(body_content)
    # dom_content = split_dom_content(cleaned_body_content)
    documents = create_document_from_dom_content(cleaned_body_content)
    summary_index = DocumentSummaryIndex.from_documents(documents,llm=llm,show_progress=True)
    summary_index.storage_context.persist("./storage/bo")

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
agent = ReActAgent.from_tools(tools=tools,llm=llm,verbose=True,context=context)