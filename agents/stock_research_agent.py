from typing import Annotated, TypedDict
import asyncio
import os 
from dotenv import load_dotenv

# LangChain imports
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from langchain_core.tools import tool
from langchain_mcp_adapters.client import MultiServerMCPClient

# YFinance tools imports
from langchain_community.tools.yahoo_finance_news import YahooFinanceNewsTool
import yfinance as yf

load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")

SYSTEM_PROMPT = """
You are a professional stock research analyst. 
Your job is to call the Yahoo Finance MCP tools and present both their raw outputs and your analysis.

## Tools
- get_stock_info(ticker): current price, market cap, volume, P/E, overview
- get_historical_stock_prices(ticker, start_date?, end_date?): OHLCV time-series
- get_yahoo_finance_news(ticker): latest news headlines/articles
- get_stock_actions(ticker): dividends and stock splits
- get_financial_statement(ticker, statement_type, period?): income_stmt, quarterly_income_stmt, balance_sheet, cash_flow; period ∈ {annual, quarterly}

## Workflow
1. **Stock Info** → Call get_stock_info for the ticker.
2. **Historical Data** → Call get_historical_stock_prices for the last 3 months (or user-specified).
3. **News** → Call get_yahoo_finance_news for the ticker and return a list of recent articles.
4. **Actions** → Call get_stock_actions for dividends/splits.
5. **Financials** → Call get_financial_statement for quarterly_income_stmt.

## Output Format
- Section 1: **Stock Info** (raw JSON or table from get_stock_info).
- Section 2: **Historical Prices** (list or table with dates & OHLCV).
- Section 3: **News Headlines** (list of title, source, date).
- Section 4: **Stock Actions** (list of dividends/splits with dates).
- Section 5: **Financial Statement** (revenue, net income, etc.).
- Section 6: **Analyst Commentary** — short summary of trends, risks, opportunities.

Important:
- Always include the **raw tool outputs** in sections 1–5.
- Do not hallucinate; if a tool has no data, say “No data returned”.


"""

# =============================================================================
# YFINANCE TOOLS: Direct Yahoo Finance data access (no external server needed)
# =============================================================================

@tool
def get_stock_info(ticker: str) -> str:
    """Get comprehensive stock information including current price, market cap, and company details."""
    try:
        stock = yf.Ticker(ticker.upper())
        info = stock.info
        
        result = f"""
Stock Info for {ticker.upper()}:
- Current Price: ${info.get('currentPrice', 'N/A')}
- Market Cap: ${info.get('marketCap', 'N/A'):,} 
- P/E Ratio: {info.get('trailingPE', 'N/A')}
- 52 Week High: ${info.get('fiftyTwoWeekHigh', 'N/A')}
- 52 Week Low: ${info.get('fiftyTwoWeekLow', 'N/A')}
- Company: {info.get('longName', 'N/A')}
- Sector: {info.get('sector', 'N/A')}
- Industry: {info.get('industry', 'N/A')}
- Volume: {info.get('volume', 'N/A'):,}
- Dividend Yield: {info.get('dividendYield', 'N/A')}
"""
        return result
    except Exception as e:
        return f"Error getting stock info for {ticker}: {str(e)}"

@tool
def get_stock_history(ticker: str, period: str = "3mo") -> str:
    """Get historical stock price data. Period options: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max"""
    try:
        stock = yf.Ticker(ticker.upper())
        hist = stock.history(period=period)
        
        if hist.empty:
            return f"No historical data found for {ticker}"
        
        # Get last 10 rows for summary
        recent = hist.tail(10)
        result = f"Historical prices for {ticker.upper()} (last 10 days from {period} period):\n"
        result += "Date\t\tOpen\tHigh\tLow\tClose\tVolume\n"
        result += "-" * 60 + "\n"
        
        for date, row in recent.iterrows():
            result += f"{date.strftime('%Y-%m-%d')}\t${row['Open']:.2f}\t${row['High']:.2f}\t${row['Low']:.2f}\t${row['Close']:.2f}\t{int(row['Volume']):,}\n"
        
        return result
    except Exception as e:
        return f"Error getting historical data for {ticker}: {str(e)}"

@tool
def get_financial_statements(ticker: str, statement_type: str = "financials") -> str:
    """Get financial statements. Types: financials, quarterly_financials, balance_sheet, quarterly_balance_sheet, cashflow, quarterly_cashflow"""
    try:
        stock = yf.Ticker(ticker.upper())
        
        if statement_type == "financials":
            data = stock.financials
        elif statement_type == "quarterly_financials":
            data = stock.quarterly_financials
        elif statement_type == "balance_sheet":
            data = stock.balance_sheet
        elif statement_type == "quarterly_balance_sheet":
            data = stock.quarterly_balance_sheet
        elif statement_type == "cashflow":
            data = stock.cashflow
        elif statement_type == "quarterly_cashflow":
            data = stock.quarterly_cashflow
        else:
            return f"Invalid statement type: {statement_type}"
        
        if data.empty:
            return f"No {statement_type} data found for {ticker}"
        
        # Return key metrics summary
        result = f"{statement_type.title()} for {ticker.upper()}:\n"
        result += str(data.head(10))  # Show first 10 rows
        return result
    except Exception as e:
        return f"Error getting {statement_type} for {ticker}: {str(e)}"

# Create YFinance tools list
def create_yfinance_tools():
    """Create a list of YFinance tools for the agent"""
    return [
        get_stock_info,
        get_stock_history,
        YahooFinanceNewsTool(),  # This is from langchain_community
        get_financial_statements
    ]

#Create a URL to connect (keep for MCP fallback)
def yf_url()->str:
    base = 'https://server.smithery.ai/@hwangwoohyun-nav/yahoo-finance-mcp/mcp'
    api_key = os.getenv("YF_API_KEY")
    return f"{base}?api_key={api_key}"

async def build_stock_agent():
    """Build stock research agent with yfinance tools (MCP as fallback)"""
    
    # Try MCP first, fall back to yfinance if it fails
    try:
        print("🔄 Trying MCP server...")
        client = MultiServerMCPClient(
            {
                "yahoo-finance":{
                    "url": yf_url(),
                    "transport": "streamable_http",
                } 
            }
        )
        lc_tools = await client.get_tools()
        print("✅ Using MCP server tools")
        
    except Exception as e:
        print(f"❌ MCP server unavailable: {str(e)[:100]}...")
        print("🔄 Falling back to direct yfinance tools")
        lc_tools = create_yfinance_tools()
    
    # Create the language model
    llm = ChatOpenAI(
        model="gpt-4o-mini",  # Fixed model name
        api_key=openai_api_key
    )

    # Create the research agent
    research_agent = create_react_agent(
        model=llm,
        prompt=SYSTEM_PROMPT,
        tools=lc_tools,
        name="stock_research_agent"
    )
    
    return research_agent