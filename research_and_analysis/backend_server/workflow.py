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


def build_interview_graph(llm, tavily_search=None):

    memory = MemorySaver()

    def generate_question(state: InterviewState):
        pass

    def search_web(state: InterviewState):
        pass

    def generate_answer(state: InterviewState):
        pass

    def save_interview(state: InterviewState):
        pass

    def write_section(state: InterviewState):
        pass

    builder = StateGraph(InterviewState)

    builder.add_node('ask_question', generate_question)
    builder.add_node('search_web', search_web)
    # builder.add_node('search_wikipedia', search_wikipedia)
    builder.add_node('generate_answer', generate_answer)
    builder.add_node('save_interview', save_interview)
    builder.add_node('write_section', write_section)

    builder.add_edge(START, 'ask_question')
    builder.add_edge('ask_question', 'search_web')
    # builder.add_edge('ask_question', 'search_wikipedia')
    builder.add_edge('search_web', 'generate_answer')
    builder.add_edge('generate_answer', 'save_interview')
    builder.add_edge('save_interview', 'write_section')
    builder.add_edge('write_section', END)

    return builder.compile(checkpointer=memory).with_config(run_name='Conduct Interview')
    # display(Image(interview_graph.get_graph().draw_mermaid_png()))


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
    ml = ModelLoader()
    llm = ml.load_llm()
    print(llm.invoke('Hi').content)

    reporter = AutonomousReportGeneration()
    reporter.build_graph()
