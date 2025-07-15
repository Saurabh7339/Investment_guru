from typing import Optional, Dict, List, Any
from sqlmodel import SQLModel, Field, JSON

# Base model for shared fields
class ClientBase(SQLModel):
    name: str = Field(index=True)
    age: int
    risk_tolerance: str
    investment_goals: str
    investment_history: Dict[str, Any] = Field(default={}, sa_type=JSON)
    portfolio: Dict[str, Any] = Field(default={}, sa_type=JSON)
    investment_horizon: str
    investor_type: str
    total_assets: float
    preferred_investment_types: List[str] = Field(default=[], sa_type=JSON)
    constraints: Dict[str, Any] = Field(default={}, sa_type=JSON)

# Database model
class Client(ClientBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

# Create schema (for POST requests)
class ClientCreate(ClientBase):
    pass

# Read schema (for responses)
class ClientRead(ClientBase):
    id: int

class InvestmentRecommendation(SQLModel):
    client_id: int
    recommendations: List[Dict[str, Any]]
    reasoning: str
    risk_assessment: str
    confidence_score: float