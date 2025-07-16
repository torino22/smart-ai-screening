import os

from fastapi import APIRouter, Depends
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.db.setup import get_db
from app.pydantics.schemas import GenericServiceResponse
from app.services.file_io import FileTranscriptService
from app.services.llm_service import LLMService
from app.services.sql import SqlService
from app.services.vector import VectorService

chat_router = APIRouter(tags=["Chat"])

def get_vector_service():
    return VectorService()

def get_sql_service():
    return SqlService()

def get_llm_service():
    return LLMService()

def get_file_service():
    return FileTranscriptService()


@chat_router.post("/faq")
async def get_faq(
          session_id: str,
          sql_service: SqlService = Depends(get_sql_service),
          db: Session = Depends(get_db)
          ):
    try:
        response = sql_service.get_faqs(db, session_id)
        return response.model_dump(exclude_none=True)

    except Exception as e:
        return GenericServiceResponse(
               success=False,
               error=str(e)
               ).model_dump(exclude_none=True)


@chat_router.post("/chat")
async def chat(
        session_id: str,
        query: str,
        vector_service: VectorService = Depends(get_vector_service),
        llm_service: LLMService = Depends(get_llm_service),
        file_service: FileTranscriptService = Depends(get_file_service)
):
    try:
        response = vector_service.semantic_search(session_id, query)
        if not response.success:
            return response.model_dump(exclude_none=True)
        top_k_match = response.result

        llm_response = await llm_service.chat(query, top_k_match)
        if not llm_response.success:
            return llm_response.model_dump(exclude_none=True)
        response_text = llm_response.result

        file_response = await file_service.text_to_audio(response_text)
        if not file_response.success:
            return file_response.model_dump(exclude_none=True)
        audio_file_path: str = file_response.path

        # Return the audio file as streaming response
        if os.path.exists(audio_file_path):
            return FileResponse(
                path=audio_file_path,
                media_type="audio/mpeg",
                filename=os.path.basename(audio_file_path),
                headers={"Content-Disposition": f"attachment; filename={os.path.basename(audio_file_path)}"}
            )
        else:
            return GenericServiceResponse(
                success=False,
                error="Audio file generation failed"
            ).model_dump(exclude_none=True)



        # YET TO BE RETURNED AS VOICE (text to voice flow integration need to be done)

        # return llm_response.model_dump(exclude_none=True)



    except Exception as e:
        return GenericServiceResponse(
            success=False,
            error=str(e)
        ).model_dump(exclude_none=True)





