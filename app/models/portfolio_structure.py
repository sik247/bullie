from pydantic import BaseModel, Field, ConfigDict
from typing import List

class Asset(BaseModel):
    model_config = ConfigDict(extra='forbid')
    
    ticker: str = Field(description="Stock ticker symbol (e.g., AAPL, MSFT)")
    allocation_percentage: float = Field(description="Percentage of portfolio (e.g., 25.0 for 25%)")
    rationale: str = Field(description="Why this asset was selected")

class Portfolio(BaseModel):
    model_config = ConfigDict(extra='forbid')
    
    assets: List[Asset] = Field(description="List of assets with allocations")
    total_allocation: float = Field(default=100.0, description="Should sum to 100%")
    strategy_summary: str = Field(description="Overall portfolio strategy")

