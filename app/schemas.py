# from pydantic import BaseModel
# from typing import Optional, Dict, List, Any

# from sqlmodel import JSON, Field, SQLModel

# class ClientBase(SQLModel):
#     name: str = Field(index=True)
#     age: int
#     risk_tolerance: str  # low, medium, high
#     investment_goals: str  # retirement, wealth, education
#     investment_history: Optional[Dict[str, Any]] = Field(default={}, sa_type=JSON)
#     portfolio: Optional[Dict[str, Any]] = Field(default={}, sa_type=JSON)
#     investment_horizon: str  # short-term, medium-term, long-term
#     investor_type: str  # conservative, moderate, aggressive
#     total_assets: float
#     preferred_investment_types: Optional[List[str]] = Field(default=[], sa_type=JSON)
#     constraints: Optional[Dict[str, Any]] = Field(default={}, sa_type=JSON)

# class ClientCreate(SQLModel):
#     name: str = Field(index=True)
#     age: int
#     risk_tolerance: str  # low, medium, high
#     investment_goals: str  # retirement, wealth, education
#     investment_history: Optional[Dict[str, Any]] = Field(default={}, sa_type=JSON)
#     portfolio: Optional[Dict[str, Any]] = Field(default={}, sa_type=JSON)
#     investment_horizon: str  # short-term, medium-term, long-term
#     investor_type: str  # conservative, moderate, aggressive
#     total_assets: float
#     preferred_investment_types: Optional[List[str]] = Field(default=[], sa_type=JSON)
#     constraints: Optional[Dict[str, Any]] = Field(default={}, sa_type=JSON)

# class Client(ClientBase):
#     # id: int

#     class Config:
#         from_attributes = True

# class InvestmentRecommendation(BaseModel):
#     client_id: int
#     recommendations: List[Dict[str, Any]]
#     reasoning: str
#     risk_assessment: str
#     confidence_score: float