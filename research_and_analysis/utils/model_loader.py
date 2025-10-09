import os
import sys
import json
import asyncio
from dotenv import load_dotenv
from research_and_analysis.utils.config_loader import load_config
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_groq import ChatGroq
from research_and_analysis.logger import GLOBAL_LOGGER as log
from research_and_analysis.exception.custom_exception import ResearchAnalysisException

load_dotenv()


class ApiKeyManager:
    def __init__(self):
        self.api_keys = {
            "OPENAI_API_KEY": os.getenv('OPENAI_API_KEY'),
            "GROQ_API_KEY": os.getenv("GROQ_API_KEY"),
            "GOOGLE_API_KEY": os.getenv("GOOGLE_API_KEY")
        }

        for key, val in self.api_keys.items():
            if val:
                # log.info(f"{key} loaded from environment")
                pass
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
        
    def load_llm(self):
        """
        Load and return the configured LLM model.
        """
        llm_block = self.config["llm"]
        provider_key = os.getenv("LLM_PROVIDER", "openai")

        if provider_key not in llm_block:
            log.error("LLM provider not found in config", provider=provider_key)
            raise ValueError(f"LLM provider '{provider_key}' not found in config")

        llm_config = llm_block[provider_key]
        provider = llm_config.get("provider")
        model_name = llm_config.get("model_name")
        temperature = llm_config.get("temperature", 0.2)
        max_tokens = llm_config.get("max_output_tokens", 2048)

        log.info("Loaded LLM", provider=provider, model=model_name)

        if provider == "google":
            return ChatGoogleGenerativeAI(
                model=model_name,
                google_api_key=self.api_key_mgr.get("GOOGLE_API_KEY"),
                temperature=temperature,
                max_output_tokens=max_tokens
            )

        elif provider == "groq":
            return ChatGroq(
                model=model_name,
                api_key=self.api_key_mgr.get("GROQ_API_KEY"), #type: ignore
                temperature=temperature,
            )

        elif provider == "openai":
            return ChatOpenAI(
                model=model_name,
                api_key=self.api_key_mgr.get("OPENAI_API_KEY"),
                temperature=temperature
            )

        else:
            log.error("Unsupported LLM provider", provider=provider)
            raise ValueError(f"Unsupported LLM provider: {provider}")


if __name__=='__main__':
    loader = ModelLoader()

    embedding = loader.load_embedding()
    print(f"embedding model laoded: {embedding}")

    result = embedding.embed_query("Hello, how re you?")
    print(f"embedding result: {len(result)}")

    llm = loader.load_llm()
    print(f"LLM loaded: {llm}")

    query = "Hi, how are you?"
    result = llm.invoke(query)
    print(f"Q: {query}\nA: {result.content}")
