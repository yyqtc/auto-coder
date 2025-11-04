from pydantic import BaseModel, Field

from typing_extensions import TypedDict
from typing import Union, List, Tuple, Annotated

import operator

# PlanExecute不需要校验
class PlanExecute(TypedDict):
    input: str
    plan: List[str]
    past_steps: Annotated[List[Tuple], operator.add]
    response: str
    mapping_table: dict  # 映射表，用于存储脱敏占位符到原始实体的映射

class Plan(BaseModel):
    steps: List[str] = Field(
        descriptions="将要执行的步骤，确保步骤按照先后顺序排序"
    )

class Response(BaseModel):
    response: str

class Act(BaseModel):
    action: Union[Response, Plan] = Field(
        description="""
            将要执行的动作，可以是Response类型也可以是Plan类型。
            如果不需要再执行任何步骤就可以输出结果，就使用Response。
            如果需要执行更多步骤，就使用Plan。
        """
    )
