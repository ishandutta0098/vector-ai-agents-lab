import argparse
import asyncio
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

from agents import analyst, data_explorer, fin_expert, llm, news_info_explorer
from crewai import Crew, Process
from tasks import advise, analyse, get_company_financials, get_company_news

os.environ["CREWAI_STORAGE_DIR"] = "src/intermediate/investment_advisor/crewai_memory"

# Configuration
ENABLE_PARALLEL_EXECUTION = True  # Set to False for sequential execution

# Create separate crews for parallel execution
financial_crew = Crew(
    agents=[data_explorer],
    tasks=[get_company_financials],
    verbose=True,
    process=Process.sequential,
    memory=True,
    cache=True,
    max_rpm=15,
)

news_crew = Crew(
    agents=[news_info_explorer],
    tasks=[get_company_news],
    verbose=True,
    process=Process.sequential,
    memory=True,
    cache=True,
    max_rpm=15,
)

# Analysis crew for sequential tasks that depend on parallel results
analysis_crew = Crew(
    agents=[analyst, fin_expert],
    tasks=[analyse, advise],
    verbose=True,
    process=Process.sequential,
    memory=True,
    cache=True,
    max_rpm=15,
)

# Traditional sequential crew (for when parallel execution is disabled)
sequential_crew = Crew(
    agents=[data_explorer, news_info_explorer, analyst, fin_expert],
    tasks=[get_company_financials, get_company_news, analyse, advise],
    verbose=True,
    process=Process.sequential,
    memory=True,
    cache=True,
    max_rpm=35,
)


def run_crew_task(crew, inputs, task_name):
    """Helper function to run a crew task."""
    print(f"🚀 Starting {task_name}...")
    result = crew.kickoff(inputs=inputs)
    print(f"✅ Completed {task_name}")
    return result


def run_parallel_execution(stock_input):
    """Run financial analysis with parallel execution."""
    print("🚀 Starting Enhanced Financial Analysis with Parallel Execution...")

    # Phase 1: Run financial data gathering and news gathering in parallel
    print("\n🔄 Phase 1: Running Financial Data & News Gathering in Parallel...")
    parallel_start = time.time()

    with ThreadPoolExecutor(max_workers=2) as executor:
        # Submit both tasks to run in parallel
        financial_future = executor.submit(
            run_crew_task, financial_crew, stock_input, "Financial Data Gathering"
        )
        news_future = executor.submit(
            run_crew_task, news_crew, stock_input, "News Gathering"
        )

        # Wait for both tasks to complete
        financial_result = financial_future.result()
        news_result = news_future.result()

    parallel_end = time.time()
    parallel_time = parallel_end - parallel_start
    print(f"✅ Phase 1 completed in {parallel_time:.2f} seconds")

    # Phase 2: Run analysis and recommendation sequentially (they depend on Phase 1 results)
    print("\n🔄 Phase 2: Running Analysis & Recommendation...")
    analysis_start = time.time()

    # The analysis crew will use the context from the completed tasks
    analysis_result = analysis_crew.kickoff(inputs=stock_input)

    analysis_end = time.time()
    analysis_time = analysis_end - analysis_start
    print(f"✅ Phase 2 completed in {analysis_time:.2f} seconds")

    return parallel_time, analysis_time


def run_sequential_execution(stock_input):
    """Run financial analysis with traditional sequential execution."""
    print("🚀 Starting Enhanced Financial Analysis with Sequential Execution...")

    print("\n🔄 Running All Tasks Sequentially...")
    sequential_start = time.time()

    result = sequential_crew.kickoff(inputs=stock_input)

    sequential_end = time.time()
    sequential_time = sequential_end - sequential_start
    print(f"✅ All tasks completed in {sequential_time:.2f} seconds")

    return sequential_time, 0  # Return 0 for analysis_time since it's all combined


def main():
    """Main function to run the financial analysis with configurable execution mode."""
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description="Financial Analysis with Configurable Execution Mode"
    )
    parser.add_argument(
        "--parallel",
        action="store_true",
        help="Enable parallel execution (overrides config)",
    )
    parser.add_argument(
        "--sequential",
        action="store_true",
        help="Enable sequential execution (overrides config)",
    )
    parser.add_argument(
        "--stock",
        default="RELIANCE",
        help="Stock symbol to analyze (default: RELIANCE)",
    )

    args = parser.parse_args()

    # Determine execution mode
    if args.parallel:
        use_parallel = True
    elif args.sequential:
        use_parallel = False
    else:
        use_parallel = ENABLE_PARALLEL_EXECUTION

    # Record start time
    start_time = time.time()

    # Scenario: Analyze specified stock
    print(f"\n📋 Stock Analysis: {args.stock}")
    stock_input = {"stock": args.stock}

    # Execute based on mode
    if use_parallel:
        parallel_time, analysis_time = run_parallel_execution(stock_input)

        # Calculate and display results
        end_time = time.time()
        execution_time = end_time - start_time

        print("\n🎉 Financial analysis completed!")
        print(f"⏱️  Phase 1 (Parallel): {parallel_time:.2f} seconds")
        print(f"⏱️  Phase 2 (Sequential): {analysis_time:.2f} seconds")
        print(
            f"⏱️  Total execution time: {execution_time:.2f} seconds ({execution_time/60:.2f} minutes)"
        )

        # Show potential time savings
        estimated_sequential_time = parallel_time * 2 + analysis_time
        time_saved = estimated_sequential_time - execution_time
        print(
            f"💡 Estimated time saved by parallel execution: {time_saved:.2f} seconds"
        )

    else:
        sequential_time, _ = run_sequential_execution(stock_input)

        # Calculate and display results
        end_time = time.time()
        execution_time = end_time - start_time

        print("\n🎉 Financial analysis completed!")
        print(
            f"⏱️  Total execution time: {execution_time:.2f} seconds ({execution_time/60:.2f} minutes)"
        )
        print(
            "💡 Running in sequential mode - use --parallel flag for faster execution"
        )


if __name__ == "__main__":
    main()
