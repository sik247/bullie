
from dotenv import load_dotenv
import os 
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain_core.messages import HumanMessage
from langgraph.types import Command
from typing import Literal
from langgraph.graph import END

from app.models.portfolio_structure import Portfolio
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

llm = ChatOpenAI(
    model="gpt-5",
    api_key=openai_api_key
)
SYSTEM_PROMPT = """
You are a professional portfolio manager. 

## Task:
1. Analyze client profile and investment goals
2. Create an initial portfolio allocation with specific assets (stocks/ETFs)
3. Output a Portfolio with assets and their allocation percentages

## Guidelines:
- Create 6-10 assets maximum for portfolio
- Ensure allocations add up to 100%
- Choose assets that match client's risk tolerance and goals
- Include asset tickers (e.g., AAPL, VOO, BND) and allocation percentages
- Provide rationale for each asset selection

## Output Format:
Return a Portfolio with:
- assets: List of Asset objects (ticker, allocation_percentage, rationale)
- total_allocation: Should be 100.0
- strategy_summary: Brief explanation of portfolio approach
"""
def portfolio_construct_node(state) ->Command[Literal["stock_research_agent"]]:
    portfolio_agent = create_agent(
        model=llm,
        prompt=SYSTEM_PROMPT,
        tools=[],
        name="portfolio_constructor_agent",
        response_format=Portfolio
    )
    
    # Get structured output from previous agent (ClientSummary)
    latest_structured_output = state['messages'][-1].content if state['messages'] else ""
    
    # Get full conversation history for context
    
    # Combine structured data + chat history + client profile
    input_content = f"""
    CLIENT PROFILE:
    {state['client_profile']}
    
    PREVIOUS AGENT OUTPUT (ClientSummary):
    {latest_structured_output}
    
  
    """
    
    result = portfolio_agent.invoke({"messages": [HumanMessage(content=input_content)]})
    
    return Command(
        update={
            "messages": [HumanMessage(content=str(result["structured_response"]), name="portfolio_constructor_agent")]
        },
        goto="stock_research_agent"
    )

def portfolio_refine_node(state):
    """Second portfolio node that refines based on stock research"""
    portfolio_agent = create_agent(
        model=llm,
        prompt=SYSTEM_PROMPT + """
        
## REFINEMENT TASK:
You have received stock research analysis. Based on this research:
1. Keep assets that got positive recommendations
2. Replace assets that got negative recommendations with better alternatives
3. Adjust allocations based on research findings
4. Create a FINAL optimized portfolio

Ensure the final portfolio allocations add up to 100%.
        """,
        tools=[],
        name="portfolio_refine_agent",
        response_format=Portfolio
    )
    
    # Get structured output from previous agent (StockReport/Research Analysis)
    latest_structured_output = state['messages'][-1].content if state['messages'] else ""
    
    # Get full conversation history for context
    chat_history = "\n".join([f"{msg.name}: {msg.content}" for msg in state['messages']]) if state['messages'] else ""
    
    # Combine structured data + chat history + client profile
    input_content = f"""
    CLIENT PROFILE:
    {state['client_profile']}
    
    PREVIOUS AGENT OUTPUT (Stock Research Analysis):
    {latest_structured_output}
    
    CONVERSATION HISTORY:
    {chat_history}
    """
    
    result = portfolio_agent.invoke({"messages": [HumanMessage(content=input_content)]})
    
    return Command(
        update={
            "messages": [HumanMessage(content=str(result["structured_response"]), name="portfolio_refine_agent")]
        },
        goto=END
    )