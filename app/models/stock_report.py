from typing import List, Optional, Dict
from pydantic import BaseModel, Field, ConfigDict


class KeyPoint(BaseModel):
    point: str = Field(..., description="Concise key investment thesis point")


class FinancialStatement(BaseModel):
    
    year: int = Field(..., description="Fiscal year")
    revenue: float = Field(..., description="Revenue in billions USD")
    eps: float = Field(..., description="Earnings per share")
    operating_margin: float = Field(0.0, ge=0, le=100)
    net_income: float = 0.0
    free_cash_flow: float = 0.0


class RatioAnalysis(BaseModel):    
    pe_ratio: float = Field(0.0, ge=0, description="Price-to-Earnings ratio, use 0.0 if not available")
    ev_ebitda: float = Field(0.0, description="Enterprise Value to EBITDA ratio, use 0.0 if not available")
    roe: float = Field(0.0, description="Return on Equity percentage, use 0.0 if not available")
    debt_to_equity: float = Field(0.0, description="Debt-to-Equity ratio, use 0.0 if not available")


class Valuation(BaseModel):
    
    method: str = Field(..., description="e.g., DCF, Comparables")
    target_price: float = Field(1.0, ge=0.01)
    assumptions: str = "TBD"
    sensitivity_analysis: str = "TBD"
    multiples: Dict[str, float] = Field(default_factory=dict, description="e.g., {'PE': 25.0}")


class Risk(BaseModel):
    model_config = ConfigDict(extra='forbid')
    
    category: str = Field(..., description="Market, Company-specific, or Industry")
    description: str


class ReportSection(BaseModel):
    title: str
    content: str


class StockReport(BaseModel):
    model_config = ConfigDict(extra='forbid')
    
    # Cover page / metadata
    company_name: str
    ticker: str
    exchange: str
    analyst: str
    report_date: str
    rating: str = Field(..., description="Buy, Hold, or Sell")
    current_price: float = Field(1.0, ge=0.01)  # Default value with constraint
    target_price: float = Field(1.0, ge=0.01)   # Default value with constraint
    upside_percent: float

    # Sections
    summary_points: List[KeyPoint]
    executive_summary: str
    business_overview: str
    recent_performance: str

    financials: List[FinancialStatement]
    ratios: RatioAnalysis

    valuation: Valuation
    investment_thesis: List[KeyPoint]
    risks: List[Risk]

    conclusion: str