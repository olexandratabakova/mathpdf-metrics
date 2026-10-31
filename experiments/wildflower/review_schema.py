from typing import Literal
from pydantic import BaseModel,ConfigDict,Field

class Item(BaseModel):
    model_config=ConfigDict(extra='forbid')
    id:int
    decision:Literal['accept','revise','reject']
    self_contained:bool
    statement_correct:bool
    solution_correct:bool
    complete_solution:bool
    source_method_supported:bool
    novelty:Literal['substantive','cosmetic','copied','uncertain']
    formatting_issue:bool
    explanation:str
    suggested_fix:str

class ProblemAudit(BaseModel):
    model_config=ConfigDict(extra='forbid')
    items:list[Item]=Field(min_length=10,max_length=10)
