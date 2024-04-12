import os

from dotenv import load_dotenv
from fastapi import FastAPI

import services
from rag import RetrievalAugmentedGeneration

load_dotenv()

app = FastAPI()

app.include_router(services.router)

RetrievalAugmentedGeneration(document_intelligence_endpoint=os.environ['AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT'],
                             document_intelligence_api_key=os.environ['AZURE_DOCUMENT_INTELLIGENCE_API_KEY'],
                             document_intelligence_locale=os.environ['AZURE_DOCUMENT_INTELLIGENCE_LOCALE'],
                             openai_gpt_deployment_name=os.environ['OPENAI_GPT_DEPLOYMENT_NAME'],
                             openai_gpt_model_name=os.environ['OPENAI_GPT_MODEL_NAME'],
                             openai_embedding_deployment_name=os.environ['OPENAI_EMBEDDING_DEPLOYMENT_NAME'])
