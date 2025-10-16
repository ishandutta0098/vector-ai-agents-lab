# Web Search Tool
import os

from crewai_tools import EXASearchTool


def exa_search_tool():
    """
    Search the web for information using ExaSearchTool
    """
    exa_search_tool = EXASearchTool()

    return exa_search_tool
