import os
from datetime import datetime
from typing import Optional
from langgraph.types import Send
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.messages import get_buffer_string
from langchain_community.tools.tavily_search import TavilySearchResults

from research_and_analysis.prompt_lib.prompts import *
from docx import Document
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from research_and_analysis.backend_server.models import Perspectives, GenerateAnalystsState, InterviewState, ResearchGraphState, SearchQuery
from research_and_analysis.utils.model_loader import ModelLoader

import warnings
warnings.filterwarnings('ignore')


def build_interview_graph(llm, tavily_search=None):

    memory = MemorySaver()

    def generate_question(state: InterviewState):
        analyst = state.get("analyst")
        if not analyst:
            raise ValueError("Missing analyst in InterviewState")

        # Render your Jinja2 prompt
        prompt_text = ANALYST_ASK_QUESTIONS.render(goals=analyst.persona)

        # Build the base message list
        messages = [
            SystemMessage(content=prompt_text),
            HumanMessage(content="Begin by asking your first interview question.")
        ]

        # Invoke LLM directly with the messages
        # question_response = state["llm"].invoke(messages)
        question_response = llm.invoke(messages)

        # Append the generated question into the dialogue
        return {"messages": state["messages"] + [AIMessage(content=question_response.content)]}

    def search_web(state: InterviewState):
        """
        Retrieve data from the web
        """
        structured_llm = llm.with_structured_output(SearchQuery)
        prompt_text = GENERATE_SEARCH_QUERY.render()
        search_query = structured_llm.invoke([SystemMessage(content=prompt_text)] + state["messages"])

        # Perform search
        raw_results = tavily_search.invoke(search_query.search_query)

        # If it's a dict (APIWrapper), extract the real docs
        if isinstance(raw_results, dict) and "results" in raw_results:
            search_docs = raw_results["results"]
        else:
            # fallback if Tavily tool returns a list or string
            search_docs = raw_results

        # Format nicely
        formatted_search_docs = "\n\n---\n\n".join(
            [
                (
                    f'<Document href="{doc.get("url", "unknown")}">\n{doc.get("content", "")}\n</Document>'
                    if isinstance(doc, dict)
                    else f'<Document>\n{doc}\n</Document>'
                )
                for doc in search_docs
            ]
        )

        return {"context": [formatted_search_docs]}

    def generate_answer(state: InterviewState):
        # Get state
        analyst = state["analyst"]
        messages = state["messages"]
        context = state["context"]

        # Answer question
        system_message = GENERATE_ANSWERS.render(goals=analyst.persona, context=context)

        answer = llm.invoke([SystemMessage(content=system_message)] + messages)

        # Name the message as coming from the expert
        answer.name = "expert"

        # Append it to state
        return {"messages": [answer]}

    def save_interview(state: InterviewState):

        """ Save interviews """

        # Get messages
        messages = state["messages"]

        # Convert interview to a string
        interview = get_buffer_string(messages)

        # Save to interviews key
        return {"interview": interview}

    def write_section(state: InterviewState):
        """ Node to answer a question """

        # Get state
        interview = state["interview"]
        context = state["context"]
        analyst = state["analyst"]

        # Write section using either the gathered source docs from interview (context) or the interview itself (interview)
        system_message = WRITE_SECTION.render(focus=analyst.description)
        section = llm.invoke([SystemMessage(content=system_message)] + [
            HumanMessage(content=f"Use this source to write your section: {context}")])

        # Append it to state
        return {"sections": [section.content]}

    builder = StateGraph(InterviewState)

    builder.add_node('ask_question', generate_question)
    builder.add_node('search_web', search_web)
    builder.add_node('generate_answer', generate_answer)
    builder.add_node('save_interview', save_interview)
    builder.add_node('write_section', write_section)

    builder.add_edge(START, 'ask_question')
    builder.add_edge('ask_question', 'search_web')
    builder.add_edge('search_web', 'generate_answer')
    builder.add_edge('generate_answer', 'save_interview')
    builder.add_edge('save_interview', 'write_section')
    builder.add_edge('write_section', END)

    return builder.compile(checkpointer=memory)


class AutonomousReportGeneration:
    def __init__(self, llm):
        self.llm = llm
        self.memory = MemorySaver()
        self.tavily_search = TavilySearchResults()

    def create_analyst(self, state: GenerateAnalystsState):
        structured_llm = self.llm.with_structured_output(Perspectives)

        # Render Jinja template into a plain string
        prompt_text = CREATE_ANALYSTS_PROMPT.render(
            topic=state.get("topic", ""),
            human_analyst_feedback=state.get("human_analyst_feedback", ""),
            max_analysts=state.get("max_analysts", 3)
        )

        # Now pass the rendered string to SystemMessage
        analysts = structured_llm.invoke([
            SystemMessage(content=prompt_text),
            HumanMessage(content="Generate the set of analysts.")
        ])

        return {"analysts": analysts.analysts}

    def human_feedback(self):
        pass

    def write_report(self, state: ResearchGraphState):
        sections = state.get("sections", [])
        topic = state.get("topic", "")

        if not sections:
            sections = ['[No sections generated — kindly verify the interview stage.]']

        # Render your template
        prompt_text = REPORT_WRITER_INSTRUCTIONS.render(
            topic=topic
        )

        # Send prompt properly
        report = self.llm.invoke([
            SystemMessage(content=prompt_text),
            HumanMessage(content="\n\n".join(sections))
        ])

        return {"content": report}

    def write_introduction(self, state: ResearchGraphState):
        topic = state.get("topic", '')
        intro = self.llm.invoke([
            SystemMessage(content=f'Write a 100 word markdown introduction for {topic}')
        ])

        return {"introduction": intro}

    def write_conclusion(self, state: ResearchGraphState):
        topic = state.get("topic", "")
        sections = state.get("sections", [])

        # If no sections exist yet, add placeholder
        if not sections:
            sections = ["[No sections provided — conclusion will summarize general insights.]"]

        # Render prompt template (Jinja2)
        prompt_text = INTRO_CONCLUSION_INSTRUCTIONS.render(
            topic=topic,
            formatted_str_sections="\n".join(sections)
        )

        # Call LLM
        conclusion = self.llm.invoke([
            SystemMessage(content=prompt_text),
            HumanMessage(content="Write the conclusion section.")
        ])

        return {"conclusion": conclusion}

    def finalize_report(self, state: ResearchGraphState):
        """
        Combine introduction, main content, and conclusion into a single final report.
        This is the last node of the graph.
        """

        intro = state.get("introduction", "")
        content = state.get("content", "")
        conclusion = state.get("conclusion", "")
        topic = state.get("topic", "Untitled Research Report")

        # Assemble markdown report
        final_report = f"# {topic}\n\n"
        if intro:
            final_report += f"{intro}\n\n"
        if content:
            final_report += f"{content}\n\n"
        if conclusion:
            final_report += f"{conclusion}\n\n"

        print("\nFinal report assembled successfully.\n")

        # Return to graph
        return {"final_report": final_report}

    def save_report(self, final_report: str, topic: str, format_: str = "docx", save_dir: Optional[str] = None):
        """
        Save the final report in DOCX or PDF format inside a timestamped folder.
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_topic = topic.replace(" ", "_").replace("/", "_")

        # Default save directory
        if not save_dir:
            save_dir = os.path.join(os.getcwd(), "reports", safe_topic)
        os.makedirs(save_dir, exist_ok=True)

        file_path = os.path.join(save_dir, f"{safe_topic}_{timestamp}.{format_}")

        if format_ == "docx":
            self._save_as_docx(final_report, file_path)
        elif format_ == "pdf":
            self._save_as_pdf(final_report, file_path)
        else:
            raise ValueError(f"Unsupported format: {format_}")

        print(f"Saved {format_.upper()} report → {file_path}")

    # ----------------------------------------------------------------------
    def _save_as_docx(self, text: str, file_path: str):
        """
        Save report text (Markdown or plain) as a DOCX file using python-docx.
        """
        doc = Document()
        doc.add_paragraph(text)
        doc.save(file_path)

    # ----------------------------------------------------------------------
    def _save_as_pdf(self, text: str, file_path: str):
        """
        Save report text as a simple paginated PDF using ReportLab.
        """
        c = canvas.Canvas(file_path, pagesize=letter)
        width, height = letter
        margin, y = 72, height - 72  # 1-inch margins
        line_height = 14

        for line in text.split("\n"):
            # Auto page-break
            if y <= margin:
                c.showPage()
                y = height - margin
            c.drawString(margin, y, line[:110])  # clip long lines
            y -= line_height

        c.save()

    def build_graph(self):

        builder = StateGraph(ResearchGraphState)

        interview_graph = build_interview_graph(self.llm, self.tavily_search)

        def initiate_all_interview(state: ResearchGraphState):
            topic = state.get('topic', [])
            analysts = state.get('analysts', [])

            if not analysts:
                print("No analysts found - skipping interviews.")
                return END

            return [
                Send(
                    "conduct_interview",
                    {
                        "analyst": analyst,
                        "messages": [HumanMessage(content=f"So, let's discuss about {topic}.")],
                        "max_num_turns": 2,
                        "context": [],
                        "interview": "",
                        "sections": [],
                    }
                )
                for analyst in analysts
            ]
        # Add nodes and edges
        builder = StateGraph(ResearchGraphState)
        builder.add_node("create_analysts", self.create_analyst)
        builder.add_node("human_feedback", self.human_feedback)
        builder.add_node("conduct_interview", interview_graph)
        builder.add_node("write_report", self.write_report)
        builder.add_node("write_introduction", self.write_introduction)
        builder.add_node("write_conclusion", self.write_conclusion)
        builder.add_node("finalize_report", self.finalize_report)

        # Logic
        builder.add_edge(START, "create_analysts")
        builder.add_edge("create_analysts", "human_feedback")
        builder.add_conditional_edges("human_feedback", initiate_all_interview,["conduct_interview"])
        builder.add_edge("conduct_interview", "write_report")
        builder.add_edge("conduct_interview", "write_introduction")
        builder.add_edge("conduct_interview", "write_conclusion")
        builder.add_edge(["write_conclusion", "write_report", "write_introduction"], "finalize_report")
        builder.add_edge("finalize_report", END)

        return builder.compile(interrupt_before=["human_feedback"], checkpointer=self.memory)


if __name__ == '__main__':
    llm = ModelLoader().load_llm()

    reporter = AutonomousReportGeneration(llm)
    graph = reporter.build_graph()

    topic = "Generative AI for Drug discovery."

    thread = {"configurable": {"thread_id": "1"}}

    for _ in graph.stream({"topic": topic, "amx_analysts": 3}, thread, stream_mode="values"):
        pass

    state = graph.get_state(thread)

    feedback = input("\nEnter your feedback or press 'Enter' to continue as is: ").strip()

    graph.update_state(thread, {'human_feedback': feedback}, as_node="human_feedback")

    for _ in graph.stream(None, thread, stream_mode='values'):
        pass

    final_state = graph.get_state(thread)
    final_report = final_state.values.get("final_report")

    if final_report:
        reporter.save_report(final_report, topic, "docx")
        reporter.save_report(final_report, topic, "pdf")

    else:
        print("no report content generated.")


# Also add 1 clinician in analysts panel