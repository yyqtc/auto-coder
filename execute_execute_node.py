from execute_execute_tool import tools
from execute_custom_type import PlanExecute
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langgraph.checkpoint.memory import InMemorySaver
from langchain.agents.middleware import SummarizationMiddleware

import json
import asyncio
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

config = json.load(open("config.json", encoding="utf-8"))


def _init_agent():
    _model = ChatOpenAI(
        model="qwen-plus",
        openai_api_key=config["QWEN_API_KEY"],
        openai_api_base=config["QWEN_API_BASE"],
        temperature=0.7,
        max_tokens=10000,
    )

    _prompt = """
        你是一位代码专家、一个删除文件的助手、一位可以列出工作目录下文件的助手、一位可以浏览需求目录下所有文件的助手以及一位创建目录的助手的组长。
        你的任务是结合需求文档中相关信息理解分配给你的任务，然后你再分配任务给代码专家、列出文件的助手以及创建目录的助手。
        注意！
        1. 你必须做到将任务分配给正确的人，否则项目将会失败！
        2. 当你需要把任务分配给删除文件的助手、列出文件的助手、可以浏览需求目录下所有文件的助手和创建目录的助手时，你给出的目录路径应该是相对路径！
        3. 当你需要把任务分配给代码专家时，你必须在命令中告诉他文件的相对路径！
        4. 创建目录、删除文件和编写文件的命令是不可逆的，所以你必须确保你给出命令和任务是相关的！
        5. 你的组员都非常地忙！所以你必须确保你的命令是没有歧义的、没有错误的！他们没有时间去理解有错误或歧义的命令！
        6. 你的代码专家是个除了分析项目代码、编写代码和文档的时候比较清醒其他时候都不太清醒的糊涂虫！所以你必须告诉他应该把文件放在哪个目录下！另外提醒他不允许对所在目录的父目录进行写入操作！
        7. 你的删除文件的助手可以删除文件和文件夹，但是他非常的蠢，如果是文件务必带上扩展名！
        8. 你的可以浏览需求目录下所有文件的助手可以浏览需求目录下所有文件，但是他非常的蠢，他只会用你告诉他的文件名去搜索需求目录下所有文件！必须告诉在他的文件名后面带上扩展名！
    """

    agent = create_agent(
        model=_model,
        system_prompt=_prompt,
        tools=tools,
        checkpointer=InMemorySaver(),
        middleware=[
            SummarizationMiddleware(
                model=_model,
                max_tokens_before_summary=config["SUMMARY_MAX_LENGTH"],
                messages_to_keep=20,
            )
        ],
    )

    return agent


agent = _init_agent()


async def execute_node(state: PlanExecute) -> PlanExecute:
    count = 0
    try:
        count = int(state["input"].split("：")[1])
    except (IndexError, ValueError) as e:
        logger.info(f"解析input失败: {state.get('input', '')}, 错误: {e}")
        return {"response": "输入格式错误，无法解析开发轮数"}

    if not state.get("plan") or len(state["plan"]) == 0:
        logger.error("计划列表为空，无法执行任务")
        return {"response": "计划列表为空，无法执行任务"}

    task = state["plan"].pop(0)
    logger.info(f"开发团队正在完成任务：{task}...")
    formatted_task = f"""
    完成这个任务：{task}。不要做和{task}无关的内容。
    """

    agent_response = await agent.ainvoke(
        {"messages": [("user", formatted_task)]}, {"configurable": {"thread_id": f"{count}"}}
    )

    return {
        "past_steps": [(task, agent_response["messages"][-1].content)],
    }


if __name__ == "__main__":
    # result = asyncio.run(execute_node({
    #     "input": "测试问题",
    #     "plan": ["在test目录下的hello.txt里写点废话"]
    # }))

    result = asyncio.run(
        execute_node(
            {"input": "测试问题", "plan": ["在test目录下的hello.txt里为里面的废话写个感受总结"]}
        )
    )

    print(result)
