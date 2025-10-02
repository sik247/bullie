"""
Financial AI Supervisor - LangGraph Node Workflow

Client Profile → Portfolio Constructor → Stock Research → Portfolio Refiner → END
"""
import asyncio
from datetime import date
from langgraph.graph import StateGraph, START, END

# Import agent node functions
from app.agents.client_profile_agent import client_profile_node
from app.agents.stock_research_agent import stock_research_node
from app.agents.portfolio_constructor_agent import portfolio_construct_node, portfolio_refine_node
from app.models.client_profile import ClientProfile
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage

class WorkflowState(TypedDict):
    """State schema for the LangGraph workflow"""
    messages: Annotated[list[BaseMessage], add_messages]
    client_profile: ClientProfile

async def main():
    
    # Create sample client data
    client_profile = ClientProfile(
        risk_tolerance=7,
        investment_goals="aggressive growth for retirement",
        cash_flow=100000,
        start_date=date(2024, 1, 1),
        end_date=date(2034, 1, 1)
    )
    
    # Create StateGraph with WorkflowState as state
    workflow = StateGraph(WorkflowState)
    
    # Add nodes using your node functions
    workflow.add_node("client_profile_agent", client_profile_node)
    workflow.add_node("portfolio_constructor_agent", portfolio_construct_node)
    workflow.add_node("stock_research_agent", stock_research_node)
    workflow.add_node("portfolio_refine_agent", portfolio_refine_node)
    
    # Add edges
    workflow.add_edge(START, "client_profile_agent")


    # Compile
    app = workflow.compile()
    
    print("🔄 Running LangGraph node workflow...")
    
    # Create initial workflow state
    initial_state = {
        "client_profile": client_profile,
        "messages": []
    }
    
    # Run workflow with WorkflowState as initial state
    result = await app.ainvoke(initial_state)
    
    # Extract just the final portfolio from the last message
    final_message = result['messages'][-1]  # Last message from portfolio_refine_agent
    portfolio_content = final_message.content
    
    print("📊 FINAL PORTFOLIO RECOMMENDATION")
    
    # Try to parse and pretty print as JSON
    import json
    try:
        portfolio_json = json.loads(portfolio_content)
        print(json.dumps(portfolio_json, indent=2))
    except json.JSONDecodeError:
        # If it's not valid JSON, just print as is
        print(portfolio_content)

if __name__ == "__main__":
    asyncio.run(main())
