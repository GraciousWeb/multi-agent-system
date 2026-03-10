from pydantic import BaseModel, Field
from typing import List, Optional, Literal


Market = Literal["US", "UK", "EU", "NG", "GLOBAL"]
EventCategory = Literal["FUNDING_ROUND", "REGULATORY_UPDATE", "PARTNERSHIP", "M_AND_A"]

class FintechEvent(BaseModel):
    category: EventCategory
    company_name: str
    summary: str
    impact_score: int = Field(ge=1, le=10, description="How much this moves the market")
    funding_amount: Optional[str] = None
    regulatory_deadline: Optional[str] = None
    source_url: str

class IntelligenceBrief(BaseModel):
    headline: str
    top_stories: List[FintechEvent]
    regulatory_radar: List[str] = Field(description="Upcoming laws to watch")
    skeptic_notes: List[str] = Field(description="Verified red flags found during audit")
    confidence_score: float

class CritiqueOutput(BaseModel):
    quality_score: int = Field(ge=1, le=10, description="Research quality score")
    should_loop: bool = Field(description="Whether more scouting is needed")
    follow_up_queries: List[str] = Field(default_factory=list, description="More specific queries to run")
    skeptic_notes: List[str] = Field(default_factory=list, description="Issues/red flags discovered during audit")
