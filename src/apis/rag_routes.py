from typing import Any

from fastapi import APIRouter, UploadFile, Depends
from fastapi.responses import JSONResponse

from models.chat import ChatRequest
from rag import RetrievalAugmentedGeneration

router = APIRouter()


@router.get("/rag_version")
def rag_version() -> JSONResponse:
    rag = RetrievalAugmentedGeneration.get()
    return JSONResponse(status_code=200, content=rag.version())


@router.post("/ingest_document")
def ingest_document(document: UploadFile, model_id: str) -> Any:
    try:
        rag = RetrievalAugmentedGeneration.get()
        rag.ingest_document(stream=document.file.read(), model_id=model_id)
    except Exception as exception:
        return JSONResponse(status_code=500, content={"message": f"{exception}"})


@router.post("/chat")
def chat(request: ChatRequest = Depends()) -> Any:
    try:
        rag = RetrievalAugmentedGeneration.get()
        return rag.ask_to_documents(question=request.question)
    except Exception as exception:
        return JSONResponse(status_code=500, content={"message": f"{exception}"})
