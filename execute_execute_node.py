from execute_execute_tool import tools
from execute_custom_type import PlanExecute
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent

import json
import asyncio

config = json.load(open("config.json", encoding="utf-8"))

def _init_agent():
    _model = ChatOpenAI(
        model="qwen-plus",
        openai_api_key=config["QWEN_API_KEY"],
        openai_api_base=config["QWEN_API_BASE"],
        temperature=0.7,
        max_tokens=10000
    )

    _prompt="""
        你是一位代码专家、一位列出文件的助手以及一位创建目录的助手的组长，你的任务是理解需求然后分配任务给代码专家、列出文件的助手以及创建目录的助手。
        注意！
        1. 你必须做到将任务分配给正确的人，否则项目将会失败！
        2. 当你需要把任务分配给列出文件的助手和创建目录的助手时，你给出的目录路径应该是相对路径！
        3. 当你需要把任务分配给代码专家时，你必须在命令中告诉他文件的相对路径！
        4. 创建目录和编写文件的命令是不可逆的，所以你必须确保你给出命令和任务是相关的！
        5. 你的组员都非常地忙！所以你必须确保你的命令是没有歧义的、没有错误的！
        6. 你的代码专家是个除了写代码和文档比较清醒其他时候都不太清醒的糊涂虫！所以你必须告诉他应该把文件放在哪个目录下！
    """

    agent = create_agent(
        model=_model,
        system_prompt=_prompt,
        tools=tools
    )

    return agent

async def execute_node(state: PlanExecute) -> PlanExecute:
    agent = _init_agent()

    task = state["plan"].pop(0)
    print("task：", task, "\n")
    formatted_task = f"""
    完成这个任务：{task}。不要做和{task}无关的内容。
    """
    
    agent_response = await agent.ainvoke({
        "messages": [("user", formatted_task)]
    })
    
    return {
        "past_steps": [(task, agent_response["messages"][-1].content)],
    }

if __name__ == "__main__":
    result = asyncio.run(execute_node({
        "input": "测试问题",
        "plan": ["在test目录下的hello.txt里写点废话"]
    }))

    print(result)
