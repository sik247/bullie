from typing import Union 
from fastapi import FastAPI 
from main import main
import asyncio
from dotenv import load_dotenv
import os 


from pydantic import BaseModel
from langgraph_supervisor import create_supervisor
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from yfinance import ticker
from agents.stock_research_agent import build_stock_agent

load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")


app = FastAPI() 

class StockReport(BaseModel):
    stock_price: float
    date: str
    sentiment: str
    financial_statement: str
    recommendations: str

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/items/{ticker}")
async def read_item(ticker: str):
    TRIAGE_PROMPT = f"""
        You are a triage financial analyst.

        ## Workflow
        1. Call the stock research agent to get the latest stock info for ticker
        2. Summarize the most recent stock price and date.
        3. Perform a sentiment analysis based on news & price action.
        4. Curate a key highlight from the financial statement.
        5. Provide a buy/hold/sell style recommendation.

        Respond strictly in the StockReport format.
        """
    #main logic 
    #return
    research_agent = await build_stock_agent()

    # Build supervisor agent
    supervisor = create_supervisor(
        agents=[research_agent],
        model=ChatOpenAI(model="gpt-4.1"),
        prompt=TRIAGE_PROMPT,
        response_format=StockReport,
        output_mode = "last_message"
    ).compile()
    user_input = HumanMessage(content=f"Generate a full stock report for {ticker}")

    # Run supervisor

    result = await supervisor.ainvoke({"messages": [user_input]})
    return {"result": result["contents"]}