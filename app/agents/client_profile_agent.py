"""
Client Profile Investment Advisor Agent

Pure handoff implementation - analyzes client and hands off to portfolio constructor.
"""
from app.models.client_profile import ClientProfile, ClientSummary
from langchain.agents import create_agent
from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv
from langgraph.types import Command
from typing import Literal
load_dotenv()

gpt_model = ChatOpenAI(
    model="gpt-5-2025-08-07",
    reasoning={"effort": "medium"},
    api_key=os.getenv("OPENAI_API_KEY")
)
SYSTEM_PROMPT = """
You are a professional financial advisor specializing in client profile analysis.
You are given client information and you must perform a rigorous examination of the client's financial goals.
Your report should provide detailed analysis and recommendations.

## Input Format Expected:
- risk_tolerance: Scale 1-10 (1=very conservative, 10=very aggressive)
- investment_goals: Specific investment objectives and goals
- cash_flow: Available investment capital (dollar amount)
- start_date: Investment start date
- end_date: Investment end date

## Workflow Steps:
Provide professional, thorough analysis based on modern portfolio theory and financial planning best practices.


1. Analyze client's risk tolerance and validate appropriateness
2. Analyze client's investment goals for clarity and feasibility
3. Using their cash flow, determine if risk tolerance and goals are adequate
4. If the client's risk tolerance and goals are inadequate, request clarification
5. Analyze the timeframe for investment horizon appropriateness
6. Analyze the portfolio type most adequate for the client's goals 
7. Analyze the expected yearly returns for the client's goals
8. Analyze the risk level for the client's goals
9. Analyze the initial portfolio allocation for the client's goals
10. Analyze the monthly contribution for the client's goals
11.. Create and refine a comprehensive client analysis.
12. Return a ClientSummary object with the following fields:



## Output Format (ClientSummary):
Return a ClientSummary object with the following fields:
```
    recommended_portfolio_type: str = Field(description="Recommended portfolio type")
    expected_yearly_returns: float = Field(description="Expected yearly returns")
    risk_level: str = Field(description="Risk level")
    initial_portfolio_allocation: str = Field(description="Initial portfolio allocation")
    monthly_contribution: float = Field(description="Monthly contribution")
```

"""



def client_profile_node(state)-> Command[Literal["portfolio_constructor_agent"]]:
    """Node function for LangGraph workflow"""
    client_agent = create_agent(
        model=gpt_model, 
        tools = [],
        prompt=SYSTEM_PROMPT, 
        response_format=ClientSummary,
        name="client_profile_agent"
    )
    # Get client profile data from state
    client_data = str(state["client_profile"])
    
    result = client_agent.invoke({"messages": [HumanMessage(content=client_data)]})
    return Command(
        update={
            "messages": [HumanMessage(content=str(result["structured_response"]), name="client_profile_agent")],
        },
        goto="portfolio_constructor_agent"
    )

