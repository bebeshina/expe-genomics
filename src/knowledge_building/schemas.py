from typing import List

from pydantic import BaseModel, RootModel


class Summary(BaseModel):
    gene: str
    diseases: List[str]
    symptoms: List[str]
    comment: str


class Summaries(RootModel):
    root: List[Summary]