import os

from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import DocumentAnalysisFeature
from azure.core.credentials import AzureKeyCredential
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import AzureOpenAI, AzureChatOpenAI
from langchain_core.prompts import PromptTemplate
from singleton import Singleton
from utils import parse_extraction_service_result


class SimpleLLMClient(metaclass=Singleton):
    __version__ = "0.0.1"

    @classmethod
    def get(cls):
        if cls not in cls._instances:
            raise AttributeError("Singleton class not created. Please, instantiate the first object and then retrieve "
                                 "it through `get()` method")
        return cls._instances[cls]

    def __init__(self, api_version, deploy_name):
        self.api_version = api_version
        self.llm = AzureChatOpenAI(deployment_name=deploy_name, temperature=0.3, max_tokens=1024)

    def ask(self, question):
        # Run the LLM
        return self.llm.invoke(question).content

    def ask_with_chain(self, question):
        prompt = PromptTemplate.from_template(
            "You are world class sci-fi writer."
            "you should give a inspirational and sort response for the next question:\n" 
            "'{question}'.\n"
            "You should give a response that is relevant to the question. Do not give unnecessary information.\n")

        output = StrOutputParser()
        chain = prompt | self.llm | output
        return chain.invoke({"question": question})

    def ask_with_document(self, question: str, document: dict):
        prompt = PromptTemplate.from_template(
            "You are business assistant and you have this context from a document:\n"
            "###Documnet start###\n"
            "{context}\n"
            "###Documnet end###\n"
            "You are asked to answer the next question: '{question}'.\n"
            "You should give a response that is relevant to the question. Do not give unnecessary information.\n"
        )
        output = StrOutputParser()
        chain = prompt | self.llm | output
        return chain.invoke({"question": question, "context": document})


class FileExtractor(metaclass=Singleton):
    @classmethod
    def get(cls):
        if cls not in cls._instances:
            raise AttributeError("Singleton class not created. Please, instantiate the first object and then retrieve "
                                 "it through `get()` method")
        return cls._instances[cls]

    def __init__(self, document_intelligence_endpoint, document_intelligence_api_key, document_intelligence_locale="en-US"):
        self._document_intelligence_client = DocumentIntelligenceClient(
            endpoint=document_intelligence_endpoint, credential=AzureKeyCredential(document_intelligence_api_key))
        self._document_intelligence_locale = document_intelligence_locale

    def extract_from_document(self, stream):
        document = self._document_intelligence_client.begin_analyze_document(
            model_id="prebuilt-invoice", analyze_request=stream, locale=self._document_intelligence_locale,
            features=[DocumentAnalysisFeature.KEY_VALUE_PAIRS],
            content_type="application/octet-stream").result()
        content = parse_extraction_service_result(document)
        return content


if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv()
    # Get the Azure Credential
    client = SimpleLLMClient(
        api_version=os.environ["OPENAI_API_VERSION"],
        deploy_name=os.environ["OPENAI_GPT_DEPLOYMENT_NAME"])
    print(client.ask("What AI can do for me"))
    print("######")
    print(client.ask_with_chain("What AI can do for me?"))



