import os
import glob
import logging

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from langchain_openai import AzureOpenAIEmbeddings
from langchain_community.vectorstores import AzureSearch

from dotenv import load_dotenv
load_dotenv(override=True)


logging.basicConfig(
    level = logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

logger = logging.getLogger("indexer")

def index_docs():
    '''
    Reads the pdf , chunks them , upload them to Azure AI search.
    '''

    #paths and data folder

    current_dir = os.path.dirname(os.path.abspath(__file__))

    data_folder = os.path.join(current_dir, "../../backend/data")

    #check on env variables

    logger.info("=" * 60)
    logger.info("--- Env Configuration check")
    logger.info(f"AZURE_OPENAI_ENDPOINT :  {os.getenv('AZURE_OPENAI_ENDPOINT')}")
    logger.info(f"AZURE_OPENAI_API_VERSION :  {os.getenv('AZURE_OPENAI_API_VERSION')}")
    logger.info(f"AZURE_OPENAI_EMBEDDING_DEPLOYMET :  {os.getenv('AZURE_OPENAI_EMBEDDING_DEPLOYMET', 'text-embedding-3-small-sunrise')}")
    logger.info(f"AZURE_SEARCH_ENDPOINT :  {os.getenv('AZURE_SEARCH_ENDPOINT')}")
    logger.info(f"AZURE_SEARCH_API_KEY :  {os.getenv('AZURE_SEARCH_API_KEY')}")
    logger.info(f"AZURE_SEARCH_INDEX_NAME :  {os.getenv('AZURE_SEARCH_INDEX_NAME')}")

    logger.info("=" * 60)

    required_vars=[
        'AZURE_OPENAI_ENDPOINT',
        'AZURE_OPENDAI_API_KEY',
        'AZURE_SEARCH_ENDPOINT',
        'AZURE_SEARCH_API_KEY',
        'AZURE_SEARCH_INDEX_NAME'
    ]

    missing_vars = [var for var in required_vars if not os.getenv(var)]

    if missing_vars:
        logger.error(f"Missing env variables : {missing_vars}")
        logger.error("Please check your .env file")
        return 

    #initialize the Embedding model
    try :
        logger.info("initializing the Embedding model.")
        embeddings = AzureOpenAIEmbeddings(
            azure_deployment=os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT",'text-embedding-3-small-sunrise' ),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            api_version=os.getenv("AZURE_OPENAI_API_VERSION", "2024-02-01")
        )

        logger.info("Embedding model initialized.")
    except Exception as e:
        logger.error(f"Failed to initialize embeddings {e}")
        logger.error(f"Please verify your Azure OPENAI deplouent name and endpoint.")
        return
    

    #initialize the Azure Search Knowledge base
    try :
        index_name = "compliance-rules"
        logger.info("initializing the  Knowldege base.")
        vector_store = AzureSearch(
            azure_search_endpoint=os.getenv("AZURE_SEARCH_ENDPOINT"),
            azure_search_key=os.getenv("AZURE_SEARCH_API_KEY"),
            index_name= os.getenv('AZURE_SEARCH_INDEX_NAME', "compliance-rules"),
            embedding_function=embeddings.embed_query,
        )
    
        logger.info(f"Azure Search initialized for index name : {index_name}")
    except Exception as e:
        logger.error(f"Failed to initialize Azure Search {e}")
        logger.error(f"Please verify your Azure Search index name and endpoint.")
        return


    #finidng pdf files

    pdf_files = glob.glob(os.path.join(data_folder, "*.pdf"))

    if not pdf_files:
        logger.warning(f"No pdf file found in : {data_folder}")
    logger.info(f"Found {len(pdf_files)} PDFs to process : {[os.path.basename(f) for f in pdf_files]}")


    all_splits = []

    #chunking

    for pdf_path in pdf_files:
        try:
            logger.info(f"--- Loading : {os.path.basename(pdf_path)}")
            loader = PyPDFLoader(pdf_path)
            raw_docs = loader.load()

            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size = 1000,
                chunk_overlap = 200
            )    

            splits = text_splitter.split_documents(raw_docs)

            for split in splits:
                split.metadata["source"] = os.path.basename(pdf_path)

            all_splits.extend(splits)

            logger.info(f"Splitted into {len(splits)} chunks.")
        except Exception as e:
            logger.error(f"Failed to process {pdf_path} : {e}")

        if all_splits:
            logger.info(f"Uploading {len(all_splits)} chunks to azure search index {index_name}")

            try:
                vector_store.add_documents(documents = all_splits)
                logger.info('=' * 60)
                logger.info("Knowlwedge Base is Complete.... and ready...")
                logger.info(f"Total chunks : {len(all_splits)}")
            except Exception as e:
                logger.error(f"Fauled to upload the documenrs ro azure, please check the configurations and try again.")
        else:
            logger.warning("Nop documents are processed.")


if __file__ == "__main__":
    index_docs()