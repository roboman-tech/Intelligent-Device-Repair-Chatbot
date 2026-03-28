from fastapi import APIRouter

from backend.models.chat_models import RetrieveRequest, RetrieveResponse
from backend.rag.retriever import retrieve

router = APIRouter(prefix="/retrieve", tags=["retrieve"])


@router.post("", response_model=RetrieveResponse)
def retrieve_endpoint(req: RetrieveRequest) -> RetrieveResponse:
    chunks = retrieve(
        req.query,
        top_k=req.top_k,
        device_type=req.device_type,
        issue=req.issue,
    )
    if not chunks:
        chunks = retrieve(req.query, top_k=req.top_k, device_type=None, issue=None)
    return RetrieveResponse(chunks=chunks)
