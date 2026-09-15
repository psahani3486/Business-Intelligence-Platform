import logging
from fastapi import APIRouter, HTTPException
from backend.api.schemas import NLQRequest, NLQResponse
from backend.llm.agent import ask_question

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/ask", response_model=NLQResponse)
def ask_nlq(request: NLQRequest):
    """Ask a natural language question and get SQL + data + AI analysis."""
    if not request.question or not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")
        
    logger.info(f"Processing NLQ question: '{request.question}'")
    try:
        result = ask_question(request.question)
    except Exception as e:
        logger.error(f"Error during NLQ agent processing: {e}", exc_info=True)
        return NLQResponse(
            question=request.question,
            error=f"Processing error: {str(e)}",
            data=[],
            analysis={
                "summary": "An error occurred while processing the request.",
                "insights": [str(e)],
                "recommended_chart": "table"
            }
        )
    
    return NLQResponse(
        question=result.get("question", request.question),
        sql=result.get("sql"),
        data=result.get("data"),
        analysis=result.get("analysis"),
        error=result.get("error")
    )
