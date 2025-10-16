import os

from agents import analyst, data_explorer, fin_expert, news_info_explorer
from crewai import Task

# Create output directory for task results
os.makedirs("src/intermediate/investment_advisor/task_outputs", exist_ok=True)

# Task to gather financial data of a stock
get_company_financials = Task(
    description="Get financial data like income statements and other fundamental ratios for stock: {stock}",
    expected_output="Detailed information from income statement, key ratios for {stock}. "
    "Indicate also about current financial status and trend over the period.",
    agent=data_explorer,
)

# Task to gather company news
get_company_news = Task(
    description="Get latest news and business information about company: {stock}",
    expected_output="Latest news and business information about the company. Provide a summary also.",
    agent=news_info_explorer,
)

# Task to analyze financial data and news
analyse = Task(
    description="Make thorough analysis based on given financial data and latest news of a stock",
    expected_output="Comprehensive analysis of a stock outlining financial health, stock valuation, risks, and news. "
    "Mention currency information and number units in Indian context (lakh/crore).",
    agent=analyst,
    context=[get_company_financials, get_company_news],
    output_file="src/intermediate/investment_advisor/task_outputs/financial_analysis.md",
)

# Task to provide financial advice
advise = Task(
    description="Make a recommendation about investing in a stock, based on analysis provided and current stock price. "
    "Explain the reasons.",
    expected_output="Recommendation (Buy / Hold / Sell) of a stock backed with reasons elaborated."
    "Response in Mark down format.",
    agent=fin_expert,
    context=[analyse],
    output_file="src/intermediate/investment_advisor/task_outputs/investment_recommendation.md",
)
