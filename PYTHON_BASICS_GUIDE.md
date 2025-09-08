# 🐍 Python Basics Guide for Beginners

This guide explains the Python concepts used in your stock research agent. Don't worry if this seems like a lot - you'll learn as you go!

## 📚 Table of Contents

1. [Variables and Data Types](#variables-and-data-types)
2. [Functions](#functions)
3. [Imports and Modules](#imports-and-modules)
4. [Strings and F-strings](#strings-and-f-strings)
5. [Lists and Dictionaries](#lists-and-dictionaries)
6. [Conditionals (if/else)](#conditionals-ifelse)
7. [Error Handling (try/except)](#error-handling-tryexcept)
8. [Classes and Objects](#classes-and-objects)
9. [Decorators](#decorators)
10. [Async/Await](#asyncawait)

---

## Variables and Data Types

```python
# Variables store data
name = "Apple"              # str (string/text)
price = 150.50             # float (decimal number)
shares = 100               # int (whole number)
is_profitable = True       # bool (True/False)

# You can change variables
price = 151.25             # Now price is 151.25
```

**In your code:**
```python
openai_api_key = os.getenv("OPENAI_API_KEY")  # String variable
temperature=0.1                               # Float variable
```

---

## Functions

Functions are reusable blocks of code that do specific tasks.

```python
# Define a function
def greet(name):
    """This is a docstring - it explains what the function does"""
    return f"Hello, {name}!"

# Call the function
message = greet("Alice")  # Returns "Hello, Alice!"
```

**Function parts:**
- `def` = "define a function"
- `name` = parameter (input)
- `return` = what the function gives back
- `"""docstring"""` = explanation of what it does

**In your code:**
```python
def research_stock(symbol: str, query: str = None) -> str:
    """Research a stock using the agent."""
    # Function body here
    return "Stock analysis results"
```

---

## Imports and Modules

Imports let you use code from other files or libraries.

```python
import os                          # Import entire module
from typing import Annotated       # Import specific thing
import sys                         # Built-in Python module
from langchain_openai import ChatOpenAI  # Third-party library
```

**What they do:**
- `os` = interact with operating system
- `sys` = system-specific functions
- `typing` = help with data types
- `langchain_openai` = AI/ML library

---

## Strings and F-strings

Strings are text data.

```python
# Regular strings
name = "Apple"
message = "Hello, world!"

# F-strings (formatted strings) - insert variables into text
stock = "AAPL"
text = f"Analyzing {stock} stock"  # "Analyzing AAPL stock"

# Multi-line strings
long_text = """
This is a long piece of text
that spans multiple lines.
"""
```

**In your code:**
```python
query = f"Please provide analysis of {symbol} stock"
return f"No data available for {symbol}"
```

---

## Lists and Dictionaries

**Lists** = ordered collections of items:
```python
# Create a list
fruits = ["apple", "banana", "orange"]

# Access items
first_fruit = fruits[0]        # "apple"
last_fruit = fruits[-1]       # "orange"

# Add items
fruits.append("grape")
```

**Dictionaries** = key-value pairs:
```python
# Create a dictionary
stock_data = {
    "symbol": "AAPL",
    "price": 150.50,
    "currency": "USD"
}

# Access values
symbol = stock_data["symbol"]  # "AAPL"
```

**In your code:**
```python
yahoo_finance_tools = [        # List of functions
    get_stock_info,
    get_stock_history,
    get_stock_news
]

result = agent.invoke({         # Dictionary
    "messages": [{"role": "user", "content": query}]
})
```

---

## Conditionals (if/else)

Make decisions in your code:

```python
price = 150

if price > 100:
    print("Expensive stock")
elif price > 50:               # "else if"
    print("Medium-priced stock")
else:
    print("Cheap stock")

# Check if something exists
if openai_api_key:             # True if not empty/None
    print("API key found")
```

**Common operators:**
- `==` = equal to
- `!=` = not equal to
- `>` = greater than
- `<` = less than
- `and` = both conditions must be true
- `or` = at least one condition must be true
- `not` = opposite of condition

**In your code:**
```python
if query is None:
    query = f"Please provide analysis of {symbol}"

if result and hasattr(result, 'content'):
    return str(result.content)
```

---

## Error Handling (try/except)

Handle errors gracefully:

```python
try:
    # Code that might fail
    result = 10 / 0
except ZeroDivisionError:
    # Handle specific error
    print("Cannot divide by zero!")
except Exception as e:
    # Handle any other error
    print(f"An error occurred: {e}")
```

**In your code:**
```python
try:
    result = research_stock("AAPL")
    print(f"Results: {result}")
except Exception as e:
    print(f"Error: {e}")
    print("Make sure your API key is set")
```

---

## Classes and Objects

Classes are templates for creating objects:

```python
class Car:
    """A simple car class"""
    
    def __init__(self, brand, color):
        """Constructor - runs when creating a new car"""
        self.brand = brand
        self.color = color
    
    def start(self):
        """Method - function that belongs to the class"""
        return f"The {self.color} {self.brand} is starting!"

# Create objects (instances) of the class
my_car = Car("Toyota", "red")
message = my_car.start()  # "The red Toyota is starting!"
```

**In your code:**
```python
class StockResearchState(TypedDict):
    """Template for stock data structure"""
    stock_symbol: Annotated[str, "The stock symbol"]
    stock_price: Annotated[float, "Current price"]
```

---

## Decorators

Decorators modify or enhance functions:

```python
@tool  # This is a decorator
def get_stock_info(symbol: str) -> str:
    """This function becomes a LangChain tool"""
    return "Stock information"
```

**What `@tool` does:**
1. Takes your function
2. Wraps it with extra functionality
3. Tells LangChain "this can be used by AI"
4. Returns the enhanced function

Think of it like putting a special label on a function.

---

## Async/Await

Async programming lets multiple things happen at the same time:

```python
# Regular function (synchronous)
def get_data():
    return "data"

# Async function (asynchronous)
async def get_data_async():
    return "data"

# Using async functions
async def main():
    result = await get_data_async()  # Wait for this to complete
    print(result)

# Run async function
import asyncio
asyncio.run(main())
```

**Why use async?**
- Don't block other code while waiting
- Can handle multiple requests at once
- Better performance for I/O operations (API calls, file reading)

**In your code:**
```python
# Sync version
result = asyncio.run(call_mcp_tool("get_stock_info", symbol))

# Async version
async def research_stock_async(symbol: str):
    result = await agent.ainvoke({"messages": [...]})
```

---

## 🎯 Practical Examples from Your Code

### 1. Creating a Tool
```python
@tool  # Decorator makes this usable by AI
def get_stock_info(symbol: str) -> str:  # Function with type hints
    """Function description"""
    import asyncio                       # Import what we need
    result = asyncio.run(                # Run async function
        call_mcp_tool("get_stock_info", symbol.upper())
    )
    if result and hasattr(result, 'content'):  # Check if data exists
        return str(result.content)             # Convert to string
    return f"No data for {symbol}"             # Error message
```

### 2. Setting up the AI
```python
llm = ChatOpenAI(           # Create AI instance
    model="gpt-4o-mini",    # Choose model
    temperature=0.1,        # Set creativity level
    api_key=openai_api_key  # Provide API key
)
```

### 3. Using the Agent
```python
def research_stock(symbol: str, query: str = None) -> str:
    if query is None:       # If no query provided
        query = f"Analyze {symbol} stock"  # Create default query
    
    result = agent.invoke({  # Send message to AI
        "messages": [{"role": "user", "content": query}]
    })
    
    return result["messages"][-1].content  # Get AI's response
```

---

## 🚀 Next Steps

1. **Start small**: Try modifying simple variables and strings
2. **Experiment**: Change the SYSTEM_PROMPT to see how the AI behaves differently
3. **Add features**: Try creating new tools or modifying existing ones
4. **Practice**: The best way to learn Python is by doing!

## 📖 Helpful Resources

- [Python.org Tutorial](https://docs.python.org/3/tutorial/)
- [Real Python](https://realpython.com/) - Great beginner tutorials
- [Python Tutor](http://pythontutor.com/) - Visualize code execution
- [Automate the Boring Stuff](https://automatetheboringstuff.com/) - Free online book

Remember: Every expert was once a beginner. Take your time, experiment, and don't be afraid to break things - that's how you learn! 🌟
