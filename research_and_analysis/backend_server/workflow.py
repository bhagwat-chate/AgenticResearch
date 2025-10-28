import os
import sys
from datetime import datetime
from typing import Optional
from langgraph.types import Send
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.messages import get_buffer_string
from langchain_community.tools.tavily_search import TavilySearchResults

from docx import Document
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from research_and_analysis.backend_server.models import Analyst, Perspectives, GenerateAnalystsState, InterviewState, ResearchGraphState
from research_and_analysis.utils.model_loader import ModelLoader


class AutonomousReportGeneration:
    def __init__(self):
        pass

    def create_analyst(self):
        pass

    def human_feedback(self):
        pass

    def write_report(self):
        pass

    def write_introduction(self):
        pass

    def write_conclusion(self):
        pass

    def finalize_report(self):
        pass

    def save_report(self):
        pass

    def _save_as_docx(self):
        pass

    def _save_as_pdf(self):
        pass

    def build_graph(self):
        pass


if __name__ == '__main__':
    obj = AutonomousReportGeneration()
