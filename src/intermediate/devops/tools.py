import os

from crewai_tools import EXASearchTool, FileReadTool
from dotenv import load_dotenv

load_dotenv()

# TOOL 1: FileReadTool
# Initialize FileReadTool for reading log files
log_reader_tool = FileReadTool()

# TOOL 2: EXASearchTool
os.environ["EXA_API_KEY"] = os.getenv("EXA_API_KEY")

try:
    exa_search_tool = EXASearchTool()
except Exception as e:
    print(f"EXA Search Tool initialization failed: {e}")
    # Fallback: try with empty lists for domains
    try:
        exa_search_tool = EXASearchTool(include_domains=[], exclude_domains=[])
    except Exception as e2:
        print(f"Fallback EXA Search Tool initialization also failed: {e2}")
        # Use basic initialization as last resort
        exa_search_tool = EXASearchTool()
