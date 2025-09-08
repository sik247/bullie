import asyncio
from dotenv import load_dotenv
import os 


from pydantic import BaseModel
from langgraph_supervisor import create_supervisor
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from langchain_community.tools.yahoo_finance_news import YahooFinanceNewsTool
from agents.stock_research_agent import build_stock_agent


load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")

# Structured response schema
class StockReport(BaseModel):
    stock_price: float
    date: str
    sentiment: str
    financial_statement: str
    recommendations: str


TRIAGE_PROMPT = """
You are a triage financial analyst.

## Workflow
1. Call the stock research agent to get the latest stock info.
2. Summarize the most recent stock price and date.
3. Perform a sentiment analysis based on news & price action.
4. Curate a key highlight from the financial statement.
5. Provide a buy/hold/sell style recommendation.

Respond strictly in the StockReport format.
"""


async def main():
    # Build sub-agent (stock research agent with Yahoo Finance MCP tools)
    research_agent = await build_stock_agent()

    # Build supervisor agent
    supervisor = create_supervisor(
        agents=[research_agent],
        tools = [YahooFinanceNewsTool()],   # name your sub-agent
        model=ChatOpenAI(model="gpt-4.1"),
        prompt=TRIAGE_PROMPT,
        response_format=StockReport,
        output_mode = "last_message"
    ).compile()

    user_input = HumanMessage(content="Generate a full stock report for AAPL")

    # Run supervisor
    result = await supervisor.ainvoke({"messages": [user_input]})

    print("\n=== Structured Stock Report ===")
    print(result)


if __name__ == "__main__":
    asyncio.run(main())
