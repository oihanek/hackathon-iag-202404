import os

from dotenv import load_dotenv
from fastapi import FastAPI

from apis import rag_routes, simple_routes
from rag import RetrievalAugmentedGeneration
from simple import SimpleLLMClient, FileExtractor

load_dotenv()

app = FastAPI()

app.include_router(rag_routes.router)
app.include_router(simple_routes.router)

RetrievalAugmentedGeneration(document_intelligence_endpoint=os.environ['AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT'],
                             document_intelligence_api_key=os.environ['AZURE_DOCUMENT_INTELLIGENCE_API_KEY'],
                             document_intelligence_locale=os.environ['AZURE_DOCUMENT_INTELLIGENCE_LOCALE'],
                             openai_gpt_deployment_name=os.environ['OPENAI_GPT_DEPLOYMENT_NAME'],
                             openai_gpt_model_name=os.environ['OPENAI_GPT_MODEL_NAME'],
                             openai_embedding_deployment_name=os.environ['OPENAI_EMBEDDING_DEPLOYMENT_NAME'])

SimpleLLMClient(
    api_version=os.environ["OPENAI_API_VERSION"],
    deploy_name=os.environ["OPENAI_GPT_DEPLOYMENT_NAME"])

FileExtractor(
    document_intelligence_endpoint=os.environ['AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT'],
    document_intelligence_api_key=os.environ['AZURE_DOCUMENT_INTELLIGENCE_API_KEY'],
    document_intelligence_locale=os.environ['AZURE_DOCUMENT_INTELLIGENCE_LOCALE'])


def debug():
    import uvicorn
    app = FastAPI()
    app.include_router(rag_routes.router)
    app.include_router(simple_routes.router)
    uvicorn.run(app, host="127.0.0.1", port=8000)


if __name__ == "__main__":
    debug()
