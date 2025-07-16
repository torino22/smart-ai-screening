from pydantic import BaseModel
from typing import Optional, Any

class ExtractedEntities(BaseModel):
    name: Optional[str] = None
    skills: Optional[str] = None
    yoe: Optional[str] = None
    previous_role: Optional[str] = None
    desired_role: Optional[str] = None
    previous_ctc: Optional[str] = None
    expected_ctc: Optional[str] = None

    education: Optional[str] = None
    certifications: Optional[str] = None
    notice_period: Optional[str] = None
    location: Optional[str] = None
    current_company: Optional[str] = None
    projects: Optional[str] = None
    preferred_location: Optional[str] = None
    availability: Optional[str] = None

    other_info: Optional[str] = None


class GenericServiceResponse(BaseModel):
    success: bool = True
    result: Optional[Any] = None
    message: Optional[str] = None
    error: Optional[str] = None
    path: Optional[str] = None

    model_config = {
        "exclude_none": True
    }

