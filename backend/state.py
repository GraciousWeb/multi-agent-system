from pydantic import BaseModel, Field
from typing import Annotated, List, Literal, Optional
from operator import add

from schema import IntelligenceBrief, Market, FintechEvent

class AgentState(BaseModel):
    query: str
    target_market: Market
    raw_research_notes: Annotated[List[str], add]
    follow_up_queries: List[str]
    iteration_count: int
    is_satisfactory: bool
    skeptic_notes: Annotated[List[str], add]
    verified_events: Annotated[List[FintechEvent], add]
    attempted_queries: List[str] = Field(default_factory=list)
    human_verdict: Optional[Literal["approve", "reject", "comment"]] = None
    human_feedback: Optional[str] = None
    final_brief: Optional[IntelligenceBrief]

