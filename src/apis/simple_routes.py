from typing import Any

from fastapi import APIRouter, UploadFile, Depends, File
from fastapi.responses import JSONResponse

from models.chat import ChatRequest
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
        client.ask_with_document(question=request.question, document=documents)
    except Exception as exception:
        return JSONResponse(status_code=500, content={"message": f"{exception}"})


@router.post("/simple/ask")
def ask(request: ChatRequest) -> Any:
    try:
        client = SimpleLLMClient.get()
        return client.ask(question=request.question)
    except Exception as exception:
        return JSONResponse(status_code=500, content={"message": f"{exception}"})
