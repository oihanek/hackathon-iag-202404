from typing import Any

from fastapi import APIRouter, UploadFile, Depends, File
from fastapi.responses import JSONResponse

from models.chat import ChatRequest, ChatResponse
from simple import SimpleLLMClient, FileExtractor

router = APIRouter()


@router.get("/simple/version")
def simple_version() -> JSONResponse:
    simple = SimpleLLMClient.get()
    return JSONResponse(status_code=200, content=simple.__version__)


@router.post("/simple/ask_with_document")
def ingest_document(request: ChatRequest = Depends(), document: UploadFile = File()) -> Any:
    try:
        client = SimpleLLMClient.get()
        file_ingest = FileExtractor.get()
        documents = file_ingest.extract_from_document(document.file.read())
        print(documents)
        return client.ask_with_document(question=request.question, document=documents)
    except Exception as exception:
        return JSONResponse(status_code=500, content={"message": f"{exception}"})


@router.post("/simple/ask")
def ask(request: ChatRequest = Depends()) -> Any:
    try:
        client = SimpleLLMClient.get()
        response = client.ask(question=request.question)
        return ChatResponse(question=request.question, answer=response)
    except Exception as exception:
        return JSONResponse(status_code=500, content={"message": f"{exception}"})
