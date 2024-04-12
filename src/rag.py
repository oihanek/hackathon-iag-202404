import logging
from typing import BinaryIO

from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.ai.documentintelligence.models import DocumentAnalysisFeature
from azure.core.credentials import AzureKeyCredential
from langchain.chains.conversational_retrieval.base import ConversationalRetrievalChain
from langchain_community.vectorstores.chroma import Chroma
from langchain_openai import AzureOpenAIEmbeddings, AzureChatOpenAI
from langchain_text_splitters import RecursiveCharacterTextSplitter

from models.chat import ChatResponse
from singleton import Singleton


class RetrievalAugmentedGeneration(metaclass=Singleton):
    MAJOR_VERSION = 0
    MINOR_VERSION = 0
    PATCH_VERSION = 0

    def __init__(self,
                 document_intelligence_endpoint: str,
                 document_intelligence_api_key: str,
                 document_intelligence_locale: str,
                 openai_gpt_deployment_name: str,
                 openai_gpt_model_name: str,
                 openai_embedding_deployment_name: str):
        self._document_intelligence_endpoint = document_intelligence_endpoint
        self._document_intelligence_api_key = document_intelligence_api_key
        self._document_intelligence_locale = document_intelligence_locale
        self._openai_gpt_deployment_name = openai_gpt_deployment_name
        self._openai_gpt_model_name = openai_gpt_model_name
        self._openai_embedding_deployment_name = openai_embedding_deployment_name

        self._document_intelligence_client = DocumentIntelligenceClient(
            endpoint=document_intelligence_endpoint, credential=AzureKeyCredential(document_intelligence_api_key))
        self._llm = AzureChatOpenAI(
            temperature=0.0, azure_deployment=self._openai_gpt_deployment_name,
            model_name=self._openai_gpt_model_name, max_tokens=4096, request_timeout=600)
        self._embeddings = AzureOpenAIEmbeddings(deployment=self._openai_embedding_deployment_name)
        self._vector_store = Chroma(persist_directory="./chroma_db", embedding_function=self._embeddings)
        self._rag = ConversationalRetrievalChain.from_llm(
            llm=self._llm, retriever=self._vector_store.as_retriever(search_kwargs={"k": 10}),
            chain_type="stuff", return_source_documents=True, verbose=False)
        self.logger = logging.getLogger(name=self.__class__.__name__)
        self.logger.info(f"Version: {self.version()}")

    @classmethod
    def get(cls):
        if cls not in cls._instances:
            raise AttributeError("Singleton class not created. Please, instantiate the first object and then retrieve "
                                 "it through `get()` method")
        return cls._instances[cls]

    def ingest_document(self, stream: BinaryIO, model_id: str):
        document = self._document_intelligence_client.begin_analyze_document(
            model_id=model_id, analyze_request=stream, locale=self._document_intelligence_locale,
            features=[DocumentAnalysisFeature.KEY_VALUE_PAIRS],
            content_type="application/octet-stream").result()

        text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
        documents = text_splitter.create_documents([document.content])
        self._vector_store.add_documents(documents)

    def ask_to_documents(self, question: str) -> ChatResponse:
        try:
            response = self._rag.invoke({"question": question, 'chat_history': []})
            return ChatResponse(question=response["question"], answer=response["answer"])
        except Exception as exception:
            self.logger.error(exception)
            raise exception

    def version(self) -> str:
        return f"{self.MAJOR_VERSION}.{self.MINOR_VERSION}.{self.PATCH_VERSION}"
