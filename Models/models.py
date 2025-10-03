from datetime import date
from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, Literal, List 


class InputModel(BaseModel):
    company_name: str = Field(..., description="Company Name")
    company_website: Optional[str] = Field(None, description="Company Website")


class LongDescription(BaseModel):
    founders: Optional[str]
    technologies: Optional[str]
    applications: Optional[str]
    products: Optional[str]
    customer_engagements: Optional[str]


class HQLocation(BaseModel):
    country: Optional[str]
    state_or_province: Optional[str]
    city: Optional[str]


class FundingInfo(BaseModel):
    last_round: Optional[str]
    amount: Optional[str]
    date: Optional[date]
    valuation: Optional[str]


class ResponseModel(BaseModel):
    reasoning_for_uniqueness_or_impact: str
    uniqueness_score: int = Field(..., ge=1, le=10)
    confidence_uniqueness: Literal["High", "Medium", "Low"]
    effectiveness_score: int = Field(..., ge=1, le=10)
    confidence_effectiveness: Literal["High", "Medium", "Low"]
    brief_description: str
    long_description: LongDescription
    hq_location: HQLocation
    funding_info: FundingInfo
    core_technology: List[str] = Field(..., min_items=1, max_items=5)
    applications: List[str] = Field(..., min_items=1, max_items=5)
    development_stage: Literal["Lab", "Prototype", "PoC", "Customer Trial", "Production"]

class GoogleResponseModel(BaseModel):
    company_name: str
    in_scope: str
    uniqueness_score: int
    uniqueness_why: str
    effectiveness_score: int
    effectiveness_why: str
    market_diff_score: int
    combined_score: int
    confidence: str
    brief_description: str
    wow_one_liner: str
    founders: str
    technologies: str 
    applications: str
    products: str
    customer_engagements: str
    hq_location: str
    current_funding_information: str
    core_technology_used: str
    known_development_stage: str
    action: str
