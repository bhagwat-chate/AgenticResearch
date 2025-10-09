import os
import sys
import json
import asyncio
from dotenv import load_dotenv
from utils.config_loader import load_config
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_google_genai import GoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from logger import GLOBAL_LOGGER as log
from exception.custom_exception import ResearchAnalysisException


class ApiKeyManager:
    def __init__(self):
        self.api_keys = {
            "OPENAI_API_KEY": os.getenv('OPENAI_API_KEY'),
            "GROQ_API_KEY": os.getenv("GROQ_API_KEY"),
            "GROQ_API_KEY": os.getenv("GROQ_API_KEY")
        }

        for key, val in self.api_keys.items():
            if val:
                log.info(f"{key} loaded from environment")
            else:
                log.warning(f"{key} not available in environment")
    
    def get(self, key: str):
        return self.api_keys.get(key)
    
class ModelLoader:
    def __init__(self):
        self.api_key_mgr = ApiKeyManager()
        self.config = load_config()

        log.info(f"YAML config load", config_keys=list(self.config.keys()))
        
    def load_embedding(self):
        try:
            model_name = self.config['embedding_model']['model_name']
            log.info(f"Loading embedding model", model=model_name)

            try:
                asyncio.get_running_loop()
            except RuntimeError:
                asyncio.set_event_loop(asyncio.new_event_loop())
        
            return OpenAIEmbeddings(
                model=model_name,
                api_key=self.api_key_mgr.get('OPENAI_API_KEY')
            )
        
        except Exception as e:
            log.error(f"Error loading embedding model: error: {e}")
            raise ResearchAnalysisException("Failed to load embedding model", sys)
        