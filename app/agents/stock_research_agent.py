from typing import Annotated, TypedDict
import asyncio
import os 
from dotenv import load_dotenv

# LangChain imports
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool
from langchain.agents import create_agent
# YFinance tools imports
from langchain_community.tools.yahoo_finance_news import YahooFinanceNewsTool
from langchain_core.messages import HumanMessage
from langgraph.types import Command
import yfinance as yf

from app.models.stock_report import StockReport
from langgraph.graph import END
load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")

SYSTEM_PROMPT = """
You are a professional stock research analyst with expertise in fundamental analysis and portfolio evaluation.

## Your Role:
Conduct comprehensive research on portfolio assets and provide actionable investment recommendations aligned with client objectives.

## Input Context:
- Client Profile: Risk tolerance, investment goals, time horizon, and capital
- Portfolio: Asset tickers and allocations from portfolio constructor
- Available Tools: YFinance data access for real-time market information

## Research Workflow:

### Step 1: Data Collection
For EACH ticker in the portfolio, use the available tools to gather:
- Current stock information (price, market cap, P/E, volume) using `get_stock_info`
- Historical performance (3-month trend analysis) using `get_stock_history`
- Financial statements (income statement, balance sheet, cash flow) using `get_financial_statements`
- **CALCULATED financial ratios** using `calculate_financial_ratios` tool
- Recent news and market sentiment using `YahooFinanceNewsTool`

### Step 2: Fundamental Analysis
Calculate and analyze key metrics:
- **Financial Health**: Revenue growth, EPS trends, profit margins, debt levels
- **Valuation Ratios**: P/E, EV/EBITDA, Price-to-Book, PEG ratio
- **Profitability**: ROE, ROA, operating margins, free cash flow
- **Risk Indicators**: Beta, volatility, debt-to-equity, sector concentration

**CRITICAL**: You MUST use the `calculate_financial_ratios` tool for each ticker to get computed ratios:
- ALWAYS call `calculate_financial_ratios` for each ticker in the portfolio
- Use the calculated values directly in your StockReport
- The tool returns 0.0 for unavailable data, so ratios will never be None
- Never manually estimate ratios - always use the calculated values from the tool

### Step 3: Client Alignment Assessment
Evaluate each asset against client profile:
- **Risk Compatibility**: Does asset volatility match client risk tolerance?
- **Goal Alignment**: Does asset support client's investment objectives?
- **Time Horizon Fit**: Is asset suitable for client's investment timeline?
- **Portfolio Balance**: Does asset contribute to proper diversification?

### Step 4: Investment Recommendations
For each asset, provide:
- **Rating**: BUY, HOLD, or SELL with clear rationale
- **Action**: Keep current allocation, Increase/Decrease position, or Replace entirely
- **Target Price**: Based on fundamental analysis and valuation methods
- **Risk Assessment**: Key risks and mitigation strategies

## Output Requirements:

Generate a comprehensive research analysis that includes:

1. **Executive Summary** (2-3 paragraphs)
   - Overall portfolio assessment
   - Key findings and recommendations
   - Risk-return profile evaluation

2. **Individual Asset Analysis** (for each ticker)
   - Company overview and business model
   - Financial performance and key metrics
   - Valuation analysis and price targets
   - Investment thesis and risk factors
   - Specific recommendation with rationale
   

3. **Portfolio-Level Assessment**
   - Diversification analysis
   - Risk concentration areas
   - Alignment with client goals
   - Suggested portfolio adjustments

4. **Alternative Recommendations** (if applicable)
   - Replacement assets for underperforming holdings
   - Additional opportunities for better diversification
   - Sector or geographic rebalancing suggestions

## Analysis Standards:
- Use current market data from YFinance tools
- Apply rigorous fundamental analysis principles
- Provide quantitative support for all recommendations
- Consider both upside potential and downside risks
- Maintain objectivity and professional judgment
- Focus on actionable, practical investment advice

## Important Notes:
- Always research ALL tickers in the provided portfolio
- Base recommendations on real financial data, not assumptions
- Consider client's specific risk tolerance and investment timeline
- Provide clear, concise reasoning for each recommendation
- Include both bullish and bearish perspectives where relevant

## Data Handling Requirements:
- **For missing ratios**: Use 0.0 (never null/None)
- **For missing text data**: Use "N/A" or descriptive text
- **For financial statements**: Include at least 3 years of data when available
- **For target prices**: Must be positive numbers (minimum 0.01)
- **For ratings**: Use exactly "BUY", "HOLD", or "SELL"
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
        
        # Get current price safely
        current_price = info.get('currentPrice') or info.get('regularMarketPrice', 0.0)
        
        result = f"""
        Stock Info for {ticker.upper()}:
        - Current Price: ${current_price}
        - Market Cap: ${info.get('marketCap', 0):,} 
        - P/E Ratio: {info.get('trailingPE', 0.0)}
        - 52 Week High: ${info.get('fiftyTwoWeekHigh', 0.0)}
        - 52 Week Low: ${info.get('fiftyTwoWeekLow', 0.0)}
        - Company: {info.get('longName', 'Unknown')}
        - Sector: {info.get('sector', 'Unknown')}
        - Industry: {info.get('industry', 'Unknown')}
        - Volume: {info.get('volume', 0):,}
        - Dividend Yield: {info.get('dividendYield', 0.0)}
        - Beta: {info.get('beta', 0.0)}
        - Book Value: {info.get('bookValue', 0.0)}
        - Price to Book: {info.get('priceToBook', 0.0)}
        - Enterprise Value: {info.get('enterpriseValue', 0)}
        - EBITDA: {info.get('ebitda', 0)}
        """
        return result
    except Exception as e:
        return f"Error getting stock info for {ticker}: {str(e)}"

@tool
def get_stock_history(ticker: str, period: str) -> str:
    """Get historical stock price data. Period options: 1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max. Default period should be '3mo'."""
    try:
        stock = yf.Ticker(ticker.upper())
        # Use default if period is not provided or empty
        if not period or period.strip() == "":
            period = "3mo"
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
def get_financial_statements(ticker: str, statement_type: str) -> str:
    """Get financial statements. Types: financials, quarterly_financials, balance_sheet, quarterly_balance_sheet, cashflow, quarterly_cashflow. Default should be 'financials'."""
    try:
        stock = yf.Ticker(ticker.upper())
        
        # Use default if statement_type is not provided or empty
        if not statement_type or statement_type.strip() == "":
            statement_type = "financials"
        
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

@tool
def calculate_financial_ratios(ticker: str) -> str:
    """Calculate key financial ratios for a stock using available financial data."""
    try:
        stock = yf.Ticker(ticker.upper())
        info = stock.info
        
        # Get financial statements
        financials = stock.financials
        balance_sheet = stock.balance_sheet
        
        # Initialize ratios with defaults
        ratios = {
            'pe_ratio': 0.0,
            'ev_ebitda': 0.0,
            'roe': 0.0,
            'debt_to_equity': 0.0,
            'price_to_book': 0.0,
            'current_ratio': 0.0,
            'gross_margin': 0.0,
            'operating_margin': 0.0
        }
        
        # Calculate P/E Ratio - try multiple methods
        pe = info.get('trailingPE') or info.get('forwardPE')
        if pe and pe > 0:
            ratios['pe_ratio'] = round(pe, 2)
        else:
            # Manual P/E calculation: Current Price / EPS
            current_price = info.get('currentPrice') or info.get('regularMarketPrice')
            eps = info.get('trailingEps') or info.get('forwardEps')
            if current_price and eps and eps > 0:
                ratios['pe_ratio'] = round(current_price / eps, 2)
        
        # Calculate EV/EBITDA - try multiple methods
        ev = info.get('enterpriseValue')
        ebitda = info.get('ebitda')
        if ev and ebitda and ebitda > 0:
            ratios['ev_ebitda'] = round(ev / ebitda, 2)
        else:
            # Manual EV/EBITDA calculation from financial statements
            market_cap = info.get('marketCap', 0)
            total_debt = info.get('totalDebt', 0)
            cash = info.get('totalCash', 0)
            if market_cap and not financials.empty:
                try:
                    latest_financials = financials.iloc[:, 0]
                    operating_income = latest_financials.get('Operating Income', 0)
                    depreciation = latest_financials.get('Depreciation', 0) or 0
                    ebitda_calc = operating_income + depreciation
                    ev_calc = market_cap + total_debt - cash
                    if ebitda_calc > 0 and ev_calc > 0:
                        ratios['ev_ebitda'] = round(ev_calc / ebitda_calc, 2)
                except:
                    pass
        
        # Calculate ROE - try multiple methods
        roe_from_info = info.get('returnOnEquity')
        if roe_from_info:
            ratios['roe'] = round(roe_from_info * 100, 2)  # Convert to percentage
        elif not financials.empty and not balance_sheet.empty:
            try:
                # Manual ROE calculation from financial statements
                latest_financials = financials.iloc[:, 0]
                latest_balance = balance_sheet.iloc[:, 0]
                
                # Try multiple field names for net income
                net_income = (latest_financials.get('Net Income') or 
                            latest_financials.get('Net Income Common Stockholders') or 
                            latest_financials.get('Net Income Applicable To Common Shares', 0))
                
                # Try multiple field names for shareholders equity
                shareholders_equity = (latest_balance.get('Stockholders Equity') or 
                                     latest_balance.get('Total Stockholder Equity') or
                                     latest_balance.get('Shareholders Equity') or
                                     latest_balance.get('Total Equity', 0))
                
                if net_income and shareholders_equity and shareholders_equity > 0:
                    ratios['roe'] = round((net_income / shareholders_equity) * 100, 2)
            except:
                pass
        
        # Calculate Debt-to-Equity - try multiple methods
        if not balance_sheet.empty:
            try:
                latest_balance = balance_sheet.iloc[:, 0]
                
                # Try multiple field names for total debt
                total_debt = (latest_balance.get('Total Debt') or 
                            latest_balance.get('Long Term Debt') or
                            latest_balance.get('Net Debt') or
                            latest_balance.get('Total Liabilities', 0))
                
                # Try multiple field names for shareholders equity
                shareholders_equity = (latest_balance.get('Stockholders Equity') or 
                                     latest_balance.get('Total Stockholder Equity') or
                                     latest_balance.get('Shareholders Equity') or
                                     latest_balance.get('Total Equity', 0))
                
                if total_debt and shareholders_equity and shareholders_equity > 0:
                    ratios['debt_to_equity'] = round(total_debt / shareholders_equity, 2)
            except Exception as calc_error:
                print(f"Error in debt-to-equity calculations: {calc_error}")
        
        # Calculate margins from financial statements
        if not financials.empty:
            try:
                latest_financials = financials.iloc[:, 0]
                revenue = latest_financials.get('Total Revenue', 0)
                gross_profit = latest_financials.get('Gross Profit', 0)
                operating_income = latest_financials.get('Operating Income', 0)
                
                if revenue and revenue > 0:
                    if gross_profit:
                        ratios['gross_margin'] = round((gross_profit / revenue) * 100, 2)
                    if operating_income:
                        ratios['operating_margin'] = round((operating_income / revenue) * 100, 2)
            except Exception as calc_error:
                print(f"Error in margin calculations: {calc_error}")
        
        # Calculate Price-to-Book - try multiple methods
        pb_ratio = info.get('priceToBook')
        if pb_ratio and pb_ratio > 0:
            ratios['price_to_book'] = round(pb_ratio, 2)
        else:
            # Manual P/B calculation: Market Price / Book Value per Share
            current_price = info.get('currentPrice') or info.get('regularMarketPrice')
            book_value = info.get('bookValue')
            if current_price and book_value and book_value > 0:
                ratios['price_to_book'] = round(current_price / book_value, 2)
            elif current_price and not balance_sheet.empty:
                try:
                    # Calculate book value per share from balance sheet
                    latest_balance = balance_sheet.iloc[:, 0]
                    shareholders_equity = (latest_balance.get('Stockholders Equity') or 
                                         latest_balance.get('Total Stockholder Equity') or
                                         latest_balance.get('Total Equity', 0))
                    shares_outstanding = info.get('sharesOutstanding', 0)
                    if shareholders_equity and shares_outstanding and shares_outstanding > 0:
                        book_value_per_share = shareholders_equity / shares_outstanding
                        ratios['price_to_book'] = round(current_price / book_value_per_share, 2)
                except:
                    pass
        
        # Calculate Current Ratio - try multiple methods
        current_ratio = info.get('currentRatio')
        if current_ratio and current_ratio > 0:
            ratios['current_ratio'] = round(current_ratio, 2)
        elif not balance_sheet.empty:
            try:
                # Manual Current Ratio calculation: Current Assets / Current Liabilities
                latest_balance = balance_sheet.iloc[:, 0]
                current_assets = (latest_balance.get('Current Assets') or 
                                latest_balance.get('Total Current Assets', 0))
                current_liabilities = (latest_balance.get('Current Liabilities') or 
                                     latest_balance.get('Total Current Liabilities', 0))
                if current_assets and current_liabilities and current_liabilities > 0:
                    ratios['current_ratio'] = round(current_assets / current_liabilities, 2)
            except:
                pass
        
        result = f"""
        Calculated Financial Ratios for {ticker.upper()}:
        - P/E Ratio: {ratios['pe_ratio']}
        - EV/EBITDA: {ratios['ev_ebitda']}
        - ROE: {ratios['roe']}%
        - Debt-to-Equity: {ratios['debt_to_equity']}
        - Price-to-Book: {ratios['price_to_book']}
        - Current Ratio: {ratios['current_ratio']}
        - Gross Margin: {ratios['gross_margin']}%
        - Operating Margin: {ratios['operating_margin']}%
        
        Note: All ratios calculated from available data. Zero values indicate data not available or not applicable.
        """
        
        return result
    except Exception as e:
        return f"Error calculating ratios for {ticker}: {str(e)}"

# Create YFinance tools list
def create_yfinance_tools():
    """Create a list of YFinance tools for the agent"""
    return [
        get_stock_info,
        get_stock_history,
        get_financial_statements,
        calculate_financial_ratios,  # New dedicated ratio calculation tool
        YahooFinanceNewsTool()  # This is from langchain_community
    ]

    
def stock_research_node(state):
    """Stock research node function for LangGraph workflow"""
    lc_tools = create_yfinance_tools()
    
    # Create the language model
    llm = ChatOpenAI(
        model="gpt-4.1",  # Fixed model name
        api_key=openai_api_key
    )
    
    # Create the research agent with structured output
    stock_agent = create_agent(
        model=llm, 
        prompt=SYSTEM_PROMPT, 
        tools=lc_tools, 
        name="stock_research_agent",
        response_format=StockReport
    )
    
    # Get structured output from previous agent (Portfolio)
    latest_structured_output = state['messages'][-1].content if state['messages'] else ""
    
    # Get full conversation history for context
    chat_history = "\n".join([f"{msg.name}: {msg.content}" for msg in state['messages']]) if state['messages'] else ""
    
    # Combine structured data + chat history + client profile
    input_content = f"""
    CLIENT PROFILE:
    {state['client_profile']}
    
    PREVIOUS AGENT OUTPUT (Portfolio):
    {latest_structured_output}
    
    CONVERSATION HISTORY:
    {chat_history}
    """
    
    result = stock_agent.invoke({"messages": [HumanMessage(content=input_content)]})
    
    return Command(
        update={
            "messages": [HumanMessage(content=str(result["structured_response"]), name="stock_research_agent")]
        },
        goto="portfolio_refine_agent"
    )

      
