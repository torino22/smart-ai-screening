import json
from datetime import datetime, timezone

from requests import session
from sqlalchemy.orm import Session

from app.db.models import Candidate, Entity, Log
from app.pydantics.schemas import ExtractedEntities, GenericServiceResponse


class SqlService:

    @staticmethod
    def create_candidate(
        db: Session,
        session_id: str
        ) -> GenericServiceResponse:

        candidate = db.query(Candidate).filter(Candidate.session_id == session_id).first()

        if candidate:
            return GenericServiceResponse(
                   success=False,
                   message="Duplicate entry! Candidate already attended the interview."
                   )

        candidate = Candidate(
                    session_id=session_id,
                    created_at=datetime.now(timezone.utc),
                    updated_at=datetime.now(timezone.utc),
                    entities_entry=0
                    )
        db.add(candidate)
        db.commit()
        db.refresh(candidate)
        return GenericServiceResponse(
               result=candidate
               )

    @staticmethod
    def store_entities(
        db: Session,
        session_id: str,
        extracted_entities: ExtractedEntities
        ) -> GenericServiceResponse:
        try:
            candidate = db.query(Candidate).filter(Candidate.session_id == session_id).first()
            entity = Entity(
                     candidate_id=candidate.id,
                     name=extracted_entities.name,
                     skills=extracted_entities.skills,
                     yoe=extracted_entities.yoe,
                     previous_role=extracted_entities.previous_role,
                     desired_role=extracted_entities.desired_role,
                     previous_ctc=extracted_entities.previous_ctc,
                     expected_ctc=extracted_entities.expected_ctc,
                     education=extracted_entities.education,
                     certifications=extracted_entities.certifications,
                     notice_period=extracted_entities.notice_period,
                     location=extracted_entities.location,
                     current_company=extracted_entities.current_company,
                     projects=extracted_entities.projects,
                     preferred_location=extracted_entities.preferred_location,
                     other_info=extracted_entities.other_info
                     )
            db.add(entity)

            # Update entity count and timestamp in candidate
            candidate.entities_entry += 1
            candidate.updated_at = datetime.now(timezone.utc)
            db.commit()

            db.refresh(candidate)
            db.refresh(entity)

            return GenericServiceResponse(
                   message="New candidate entity stored successfully"
                   )
        except Exception as e:
            return GenericServiceResponse(
                success=False,
                error=str(e)
            )


    def store_transcript(self,
        db: session,
        session_id: str,
        file_data: GenericServiceResponse
        ):
        try:
            candidate_status = self.create_candidate(db, session_id)
            if not candidate_status.success:
                return candidate_status

            candidate = candidate_status.result
            transcript = file_data.result

            log = Log(
                candidate_id=candidate.id,
                file_path=file_data.path,
                transcription=transcript,
            )

            db.add(log)
            db.commit()
            db.refresh(log)

            return GenericServiceResponse(
                message="Transcript stored successfully",
            )

        except Exception as e:
            return GenericServiceResponse(
                success=False,
                error=str(e)
            )

    def store_faq_log(self,
        db: session,
        session_id: str,
        faqs: list
        ):
        try:
            candidate =  db.query(Candidate).filter(Candidate.session_id == session_id).first()
            faq_json = json.dumps(faqs)

            log = Log(
                  candidate_id=candidate.id,
                  faq=faq_json
                  )

            db.add(log)
            db.commit()
            db.refresh(log)

            return GenericServiceResponse(
                   message="Transcript ingested and Logs stored successfully",
                   )

        except Exception as e:
            return GenericServiceResponse(
                   success=False,
                   error=str(e)
                   )

    def get_faqs(
        self,
        db: Session,
        session_id: str
        ) -> GenericServiceResponse:
        try:
            candidate = db.query(Candidate).filter(Candidate.session_id == session_id).first()

            if not candidate:
                return GenericServiceResponse(
                    success=False,
                    message=f"No candidate found with session_id: {session_id}"
                )

            log = db.query(Log).filter(Log.candidate_id == candidate.id).order_by(Log.id.desc()).first()

            if not log or not log.faq:
                return GenericServiceResponse(
                    success=False,
                    message=f"No FAQ log found for session_id: {session_id}"
                )

            # Convert JSON string back to list of strings
            faqs = json.loads(log.faq)

            return GenericServiceResponse(
                result=faqs,
                message="FAQs fetched successfully"
            )

        except Exception as e:
            return GenericServiceResponse(
                success=False,
                error=str(e)
            )

