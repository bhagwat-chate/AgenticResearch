import operator

from typing import Annotated, List
from typing_extensions import TypedDict
from pydantic import BaseModel, Field
from langgraph.graph.message import MessagesState


# ----------------------------------
# Section Model
# ----------------------------------
class Section(BaseModel):
    title: str
    content: str


# ----------------------------------
# Analyst Model
# ----------------------------------
class Analyst(BaseModel):
    affiliation: str = Field(description="Primary affiliation of the analyst.")
    name: str = Field(description="Name of the analyst")
    role: str = Field(description="Role of the analyst in the context of the topic.")
    description: str = Field(description="Description of the analyst focus, conscerns, motives")

    @property
    def persona(self) -> str:
        return(
            f"Name: {self.name}\n"
            f"Affiliation: {self.affiliation}\n"
            f"Role: {self.role}\n"
            f"Description: {self.description}\n"
        )
    

# ----------------------------------
# Search Query output parser
# ----------------------------------
class SearchQuery(BaseModel):
    search_query: str = Field(None, description="Search query for retrieval")


# ----------------------------------
# State classes for Graphs
# ----------------------------------
class GenerateAnalystsState(TypedDict):
    topic: str
    max_analysts: int
    max_analyst_feedback: str
    analysts: List[Analyst]


class InterviewState(MessagesState):
    max_num_turns: int
    context: Annotated[list, operator.add]
    interview: str
    sections: list


class ResearchGraphState(MessagesState):
    topic: str
    max_analysts: int
    human_analyst_feedback: str
    analysts: List[Analyst]
    sections: Annotated[list, operator.add]
    introduction: str
    content: str
    conclusion: str
    final_report: str
