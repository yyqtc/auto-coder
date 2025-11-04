from pydantic import BaseModel, Field

from typing_extensions import TypedDict

from typing import Union

class ActionReview(TypedDict):
    count: int
    response: str

class Action(BaseModel):
    count: int = Field(description="执行次数")

class Response(BaseModel):
    response: str

class Act(BaseModel):
    action: Union[Action, Response] = Field(
        description="""
            将执行的操作，可以是Action类型也可以是Response类型。
            如果生成的模拟sdk需要进一步修改，就使用Action类型。
            如果不需要执行更多步骤，就使用Response类型。
        """
    )
