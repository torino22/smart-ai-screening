from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Form
from sqlalchemy.orm import Session
from app.db.setup import get_db
from app.pydantics.schemas import GenericServiceResponse, ExtractedEntities
from app.services.file_io import FileTranscriptService
from app.services.ner import NERService
from app.services.sql import SqlService
from app.services.vector import VectorService
from app.templates.generic_faq import FAQ_QUESTIONS


file_router = APIRouter(tags=["File IO"])

def get_file_service():
    return FileTranscriptService()

def get_vector_service():
    return VectorService()

def get_sql_service():
    return SqlService()

def get_ner_service():
    return NERService()


@file_router.post("/media")
async def upload_media(
        session_id: str = Form(...),
        file: UploadFile = File(...),
        service: FileTranscriptService = Depends(get_file_service),
        vector_service: VectorService = Depends(get_vector_service),
        ner_service: NERService = Depends(get_ner_service),
        sql_service: SqlService = Depends(get_sql_service),
        db: Session = Depends(get_db)
):
    try:
        response = service.transcribe_and_save(file)
        if not response.success:
            return response.model_dump(exclude_none=True)
        transcript = response.result

        sql_response = sql_service.store_transcript(db, session_id=session_id, file_data=response)
        if not sql_response.success:
            return sql_response.model_dump(exclude_none=True)

        # Yet to store integrate the extracted entities flow here
        ner_response = ner_service.run_ner(transcript)
        if not ner_response.success:
            return ner_response.model_dump(exclude_none=True)
        entities = ner_response.result
        sql_service.store_entities(db, session_id=session_id, extracted_entities=entities)

        vector_response = vector_service.chunk_text(transcript)
        if not vector_response.success:
            return vector_response.model_dump(exclude_none=True)
        raw_chunks = vector_response.result

        embed_store_response = vector_service.embed_and_store(session_id, raw_chunks)
        if not embed_store_response.success:
            return vector_response.model_dump(exclude_none=True)

        sql_service.store_faq_log(db, session_id=session_id, faqs=FAQ_QUESTIONS)

        return embed_store_response.model_dump(exclude_none=True)

    except Exception as e:
        return GenericServiceResponse(
               success=False,
               error=str(e)
               )


@file_router.get("/health")
async def health_check():
    """
    Health check endpoint to verify if the service is running
    """
    return {"status": "ok"}
