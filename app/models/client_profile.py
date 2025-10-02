from datetime import date, timedelta
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, List
class ClientProfile(BaseModel):
    risk_tolerance: int = Field(ge=1, le=10, description="Risk tolerance on scale 1-10 (1=very conservative, 10=very aggressive)")
    investment_goals: str = Field(description="Client's investment objectives and goals")
    cash_flow: int = Field(gt=0, description="Available investment capital (must be positive)")
    start_date: date = Field(description="Investment start date")
    end_date: date = Field(description="Investment end date", default = date.today().replace(year=date.today().year + 30) )
    
### Output Format
class ClientSummary(BaseModel):
    model_config = ConfigDict(extra='forbid')
    recommended_portfolio_type: str = Field(description="Recommended portfolio type")
    expected_yearly_returns: float = Field(description="Expected yearly returns")
    risk_level: str = Field(description="Risk level")
    initial_portfolio_allocation: str = Field(description="Initial portfolio allocation")
    monthly_contribution: float = Field(description="Monthly contribution")


    
