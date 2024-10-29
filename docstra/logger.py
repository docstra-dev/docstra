import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("docstra")
logger.setLevel(logging.INFO)
logger = logging.getLogger(__name__)
logging.getLogger("chromadb").setLevel(logging.WARNING)
logging.getLogger("langchain").setLevel(logging.WARNING)
logging.getLogger("langchain_openai").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)
