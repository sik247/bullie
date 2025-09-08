# Stock Research Agent with Yahoo Finance MCP

This is a LangGraph/LangChain agent that uses the Yahoo Finance MCP (Model Context Protocol) server to provide comprehensive stock market analysis.

## Features

- 📈 Real-time stock quotes and pricing data
- 📊 Historical price analysis and trends  
- 📰 Latest financial news and market sentiment
- 👥 Analyst recommendations and ratings
- 🔍 Interactive and programmatic querying
- ⚡ Async/await support for better performance

## Setup

### 1. Install Dependencies

```bash
# From the project root
pip install -r requirements.txt
```

### 2. Environment Setup

Create a `.env` file in the project root with your OpenAI API key:

```bash
OPENAI_API_KEY=your_openai_api_key_here
```

### 3. Quick Test

```bash
# Test the Yahoo Finance MCP connection
cd mcp
python yahoo_finance_mcp.py

# Run the stock research agent
cd ../agents
python main.py
```

## Usage Examples

### Basic Usage

```python
from stock_research_agent import research_stock

# Get comprehensive analysis of Apple stock
result = research_stock("AAPL")
print(result)

# Ask specific questions
result = research_stock("TSLA", "What's the current price and recent news?")
print(result)
```

### Async Usage

```python
import asyncio
from stock_research_agent import research_stock_async

async def main():
    result = await research_stock_async("GOOGL")
    print(result)

asyncio.run(main())
```

### Interactive Mode

```bash
python main.py --interactive
```

### Direct Agent Usage

```python
from stock_research_agent import agent

# Use the agent directly with LangGraph
result = agent.invoke({
    "messages": [{"role": "user", "content": "Analyze Netflix stock performance"}]
})

print(result["messages"][-1].content)
```

## Available Stock Analysis Features

The agent can:

1. **Get Stock Quotes**: Current price, market cap, P/E ratio, volume
2. **Historical Analysis**: Price trends, technical indicators
3. **News Analysis**: Latest headlines affecting stock price
4. **Analyst Data**: Professional recommendations and price targets
5. **Financial Data**: Revenue, earnings, financial ratios

## Tool Architecture

### Yahoo Finance Tool (`yahoo_finance_tool.py`)

A LangChain-compatible tool that wraps the Yahoo Finance MCP server:

- **Input Schema**: Stock symbol, action type, time period
- **Actions**: quote, history, financials, news, analyst
- **Error Handling**: Graceful fallbacks and error messages
- **Async Support**: Non-blocking MCP server communication

### Stock Research Agent (`stock_research_agent.py`)

A LangGraph ReAct agent configured with:

- **Model**: GPT-4o-mini (configurable)
- **Tools**: Yahoo Finance MCP tool
- **Prompt**: Professional stock analyst persona
- **State**: TypedDict for structured data flow

## Customization

### Adding More Tools

```python
from langchain_core.tools import tool

@tool
def your_custom_tool(input: str) -> str:
    """Your custom tool description."""
    return "tool output"

# Add to agent
agent = create_react_agent(
    model=llm,
    tools=[yahoo_finance_tool, your_custom_tool],
    state_modifier=SYSTEM_PROMPT
)
```

### Modifying the Prompt

Edit the `SYSTEM_PROMPT` in `stock_research_agent.py` to change the agent's behavior and analysis style.

### Changing the Model

```python
llm = ChatOpenAI(
    model="gpt-4",  # or any other model
    temperature=0.1,
    api_key=openai_api_key
)
```

## Error Handling

The agent includes comprehensive error handling for:

- Missing API keys
- Network connectivity issues
- Invalid stock symbols
- MCP server errors
- Rate limiting

## Performance Tips

1. **Use Async**: For multiple queries, use `research_stock_async()`
2. **Cache Results**: Consider caching for repeated queries
3. **Batch Queries**: Group related analysis requests
4. **Specific Queries**: More targeted questions get faster responses

## Troubleshooting

### Common Issues

1. **"Import could not be resolved"**: Install missing dependencies
   ```bash
   pip install langchain langchain-openai langgraph
   ```

2. **"OPENAI_API_KEY not found"**: Set your environment variable
   ```bash
   export OPENAI_API_KEY=your_key_here
   ```

3. **MCP Connection Error**: Check internet connection and API key

### Debug Mode

Enable detailed logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Integration Examples

### Django Integration

```python
# In your Django views
from agents.stock_research_agent import research_stock

def stock_analysis_view(request, symbol):
    analysis = research_stock(symbol.upper())
    return JsonResponse({"analysis": analysis})
```

### API Endpoint

```python
from fastapi import FastAPI
from agents.stock_research_agent import research_stock_async

app = FastAPI()

@app.get("/analyze/{symbol}")
async def analyze_stock(symbol: str):
    result = await research_stock_async(symbol)
    return {"symbol": symbol, "analysis": result}
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## License

MIT License - see LICENSE file for details
