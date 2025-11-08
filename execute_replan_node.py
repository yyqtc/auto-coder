from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from execute_custom_type import Plan, Response, Act, PlanExecute
from execute_replan_utils import analyze_what_to_do
from constants import (
    UNKNOWN_ERROR_MESSAGE,
)

import os
import json
import shutil
import logging
import asyncio

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

config = json.load(open("config.json", "r", encoding="utf-8"))

_model = ChatOpenAI(
    model="qwen-max",
    openai_api_key=config["QWEN_API_KEY"],
    openai_api_base=config["QWEN_API_BASE"],
    temperature=0.7,
)

summary_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            f"""
        你是一位非常专业的总结专家，善于抓住项目日志中的重点内容。请把项目日志的字数控制在{config["SUMMARY_MAX_LENGTH"]}个token以内。
        注意！
        尽量保留日志中的重要信息，适当压缩其他信息，不要遗漏重要信息！
        """,
        ),
        ("user", "{input}"),
    ]
)

summary_pro = summary_prompt | _model

_prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
        你是一位非常苛刻的需求分析专家，善于根据计划执行情况分析当前计划是否符合客户需求。

        我们的客户的需求是：
        {todo}

        我们最近一次计划是：
        {plan}

        你的检查项目实际状况的助手告诉给你的项目实际状况是：
        {project_status}

        根据以上信息更新我们的计划。如果你认为不需要执行更多步骤，你可以直接输出"开发完成"。否则你需要在计划中补充更多步骤。
            
        注意！
        1. 你必须默认项目文件夹已经被创建了！
        2. 你输出的计划内的步骤应该是相互独立的、可以与需求点一一对应的！
        3. 你必须知道执行你计划的团队的能力包括：分析项目代码、编写代码和文档、创建文件夹、删除文件夹或文件、扫描项目目录和阅读需求文档。他们无法执行超出他们能力范围的命令！
        4. 他们非常的忙！所以必须把任务中他们需要知道的信息明确地告诉他们！不要让他们去猜！让他们能够快速完成任务！
        5. 我们的预算非常有限！不要反复的创建删除同一个文件或目录！
        6. 确保计划中的每一步都能够得到所有需要的信息！你必须明确在每个步骤中告诉你的执行团队需要的信息！不要让他们去猜！
        7. 确保计划的最后一步完成后用户能够得到一个完整可运行的项目！
        8. 如果你认为需要修正计划，请直接返回计划列表，不要返回答案！
        9. 只有你通过项目的实际情况发现项目已经满足客户需求且已经修复完审核意见，你才能输出“开发完成”！
        10. 计划请以JSON格式输出，包含action字段，action字段应该包含steps字段，steps字段类型List[str]！
        11. 答案请以JSON格式输出，包含action字段，action字段应该包含response字段，response字段类型str！
        12. 你只允许在计划中补充步骤，不要删除原有的步骤！
        13. 已经执行的步骤不要再次执行！
        """,
        )
    ]
)

agent = _prompt | _model.with_structured_output(Act)


async def execute_replan_node(state: PlanExecute) -> PlanExecute:
    logger.info("正在根据当前开发结果调整计划...")

    plan = state.get("plan", [])
    plan = "\n".join(plan)

    async def read_todo_content():
        todo = ""
        try:
            with open(f"./todo/{config['PROJECT_NAME']}/todo.md", "r", encoding="utf-8") as f:
                todo = f.read()
                if len(todo) > config["SUMMARY_THRESHOLD"]:
                    todo = summary_pro.invoke(
                        f"请适当总结项目需求，项目需求内容如下：\n{todo}"
                    ).content.strip()

        except Exception as e:
            logger.error(f"读取需求文档失败: {e}")
            # 如果是在 await 过程中发生异常，确保协程被清理
            return ("todo", "")

        return ("todo", todo)

    past_steps = state.get("past_steps", [])

    async def read_past_steps(past_steps):
        past_steps_content = ""
        for past_step in past_steps:
            step, response = past_step
            past_steps_content += f"步骤：\n{step}\n响应：{response}\n\n"

        if len(past_steps_content) > config["SUMMARY_THRESHOLD"]:
            past_steps_content = summary_pro.invoke(
                f"请适当总结项目开发日志，项目开发日志内容如下：\n{past_steps_content}"
            ).content.strip()
            past_steps = [("过去一系列任务摘要", past_steps_content)]

        return ("past_steps_content", (past_steps, past_steps_content))

    async_tasks = [read_past_steps(past_steps), read_todo_content()]
    async_results = await asyncio.gather(*async_tasks)

    past_steps_content = ""
    todo = ""
    for key, result in async_results:
        if key == "past_steps_content":
            past_steps, past_steps_content = result
        elif key == "todo":
            todo = result

    logger.info(f"开发成果: \n{past_steps_content}")

    analysis_count = 0
    project_status = ""
    while analysis_count < 3:
        project_status = analyze_what_to_do(
            count=0, past_steps_content=past_steps_content, plan=plan
        )
        if project_status != "分析失败！" and project_status != "执行失败！":
            break

        analysis_count += 1

    if len(project_status) > config["SUMMARY_THRESHOLD"]:
        project_status = summary_pro.invoke(
            f"请适当总结项目实际状况，项目实际状况内容如下：\n{project_status}"
        ).content.strip()
        logger.info("压缩开发日志成功")

    logger.info(f"项目实际状况: \n{project_status}")

    result = await agent.ainvoke(
        {
            "todo": todo,
            "plan": plan,
            "past_steps": past_steps_content,
            "project_status": project_status,
        }
    )

    logger.info("分析和重新规划结束")

    if isinstance(result.action, Response):
        return {"response": result.action.response}
    elif isinstance(result.action, Plan):
        if os.path.exists(f"./history/{config['PROJECT_NAME']}"):
            shutil.rmtree(f"./history/{config['PROJECT_NAME']}")
        shutil.copytree(
            f"./dist/{config['PROJECT_NAME']}",
            f"./history/{config['PROJECT_NAME']}",
            dirs_exist_ok=True,
        )

        return {"plan": result.action.steps, "past_steps": past_steps}
    else:
        return {"response": UNKNOWN_ERROR_MESSAGE}


if __name__ == "__main__":
    asyncio.run(
        execute_replan_node(
            {
                "plan": ["创建一个Hello World程序"],
                "past_steps": [("创建一个Hello World程序", "Hello World程序创建成功")],
            }
        )
    )
