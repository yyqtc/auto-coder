from execute_custom_type import PlanExecute
from execute_plan_utils import convert_docx_to_markdown, convert_pdf_to_markdown, analyze_what_to_do
from pathlib import Path
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from constants import REQUIREMENT_FAIL_MESSAGE
from execute_custom_type import Plan

import os
import json
import shutil
import asyncio
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

config = json.load(open("config.json", "r", encoding="utf-8"))

plan_model = ChatOpenAI(
    model="qwen-max",
    openai_api_key=config["QWEN_API_KEY"],
    openai_api_base=config["QWEN_API_BASE"],
    temperature=0.7
).with_structured_output(Plan)

plan_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """
            你是一位非常专业的需求分析专家，善于分析需求并给出执行计划。
            注意！
            1. 你必须默认项目文件夹已经被创建了！
            2. 你必须知道执行你计划的团队的能力包括：分析项目代码、编写代码和文档、创建文件夹、删除文件夹或文件、扫描项目目录和阅读需求文档。他们无法执行超出他们能力范围的命令！
            3. 他们非常的忙！所以必须把任务中他们需要知道的信息明确地告诉他们！不要让他们去猜！让他们能够快速完成任务！
            4. 你输出的计划内的步骤应该是相互独立的、可以与需求点一一对应的！
            5. 不要反复的创建删除同一个文件或目录！
            6. 确保计划中的每一个步骤都能够得到所有需要的信息！
            7. 确保计划的最后一步完成后用户能够得到一个完整可运行的项目！
            8. 如果你认为需要修正计划，请直接返回计划列表，不要返回答案！
        """
    ),
    ("user", "{input}")
])

agent = plan_prompt | plan_model

improve_opinion_model = ChatOpenAI(
    model="qwen-plus",
    openai_api_key=config["QWEN_API_KEY"],
    openai_api_base=config["QWEN_API_BASE"],
    temperature=0.7
)

improve_opinion_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """
            你是一位非常专业的需求分析专家，善于根据需求给出计划的改进意见。
        """
    ),
    ("user", "{input}")
])

improve_opinion_agent = improve_opinion_prompt | improve_opinion_model

def check_and_convert_file():
    skip_dirs = []
    with open(f".spanignore", "r", encoding="utf-8") as f:
        skip_dirs = f.read().splitlines()
    
    skip_dirs = [dir.strip() for dir in skip_dirs if len(dir.strip()) > 0]

    todo_dir = Path(f"./todo/{config['PROJECT_NAME']}/")
    warning_file = ""
    for file in todo_dir.glob("**/*"):
        if any(part in skip_dirs for part in file.parts):
            continue

        if file.is_file():
            if file.suffix.lower() == ".docx":
                try:
                    convert_docx_to_markdown(str(file))
                except Exception as e:
                    if not len(warning_file):
                        cnt = 0
                        while True:
                            if cnt == 0 and os.path.exists(f"./todo/{config['PROJECT_NAME']}/warning.md"):
                                cnt += 1
                            elif os.path.exists(f"./todo/{config['PROJECT_NAME']}/warning_{cnt}.md"):
                                cnt += 1
                            else:
                                break

                        warning_file = f"./todo/{config['PROJECT_NAME']}/warning.md" if cnt == 0 else f"./todo/{config['PROJECT_NAME']}/warning_{cnt}.md"

                    with open(warning_file, "a+", encoding="utf-8") as f:
                        f.write(f"文件无法解析内容，请手动转换成markdown文件: {str(file)}\n\n")

            elif file.suffix.lower() == ".pdf":
                convert_pdf_to_markdown(str(file))

            else:
                try:
                    file.read_text(encoding="utf-8")

                except Exception as e:
                    if not len(warning_file):
                        cnt = 0

                        while True:
                            if cnt == 0 and os.path.exists(f"./todo/{config['PROJECT_NAME']}/warning.md"):
                                cnt += 1
                            elif os.path.exists(f"./todo/{config['PROJECT_NAME']}/warning_{cnt}.md"):
                                cnt += 1
                            else:
                                break

                        warning_file = f"./todo/{config['PROJECT_NAME']}/warning.md" if cnt == 0 else f"./todo/{config['PROJECT_NAME']}/warning_{cnt}.md"

                    with open(warning_file, "a+", encoding="utf-8") as f:
                        f.write(f"文件无法解析内容，请手动转换成markdown文件: {file.name}\n\n")

    return warning_file

async def execute_plan_node(state: PlanExecute) -> PlanExecute:
    os.makedirs(f"./dist/{config['PROJECT_NAME']}", exist_ok=True)

    if os.path.exists(f"./todo/{config['PROJECT_NAME']}/todo.md"):
        user_input = input(f"todo.md文件已存在，是否删除？(y/n): ")
        if user_input == "y":
            os.remove(f"./todo/{config['PROJECT_NAME']}/todo.md")

    if os.path.exists(f"./todo/{config['PROJECT_NAME']}/todo_list.md"):
        user_input = input(f"todo_list.md文件已存在，是否删除？(y/n): ")
        if user_input == "y":
            os.remove(f"./todo/{config['PROJECT_NAME']}/todo_list.md")

    try:
        count = int(state["input"].split("：")[1])
    except (IndexError, ValueError) as e:
        logger.info(f"解析input失败: {state.get('input', '')}, 错误: {e}")
        return {
            "response": "输入格式错误，无法解析开发轮数"
        }

    logger.info(f"进行第{count + 1}轮需求分析-开发工作")

    warning_file = ""
    if count == 0:
        warning_file = check_and_convert_file()

    if len(warning_file) and os.path.exists(warning_file):
        while True:
            user_input = input(f"""
            存在无法解析内容的文件，请手动转换成markdown文件。
            详见{warning_file}（无法解析的文件将被系统忽略）。
            无疑问请输入pass继续执行：""")
            if user_input == "pass":
                break

    result = analyze_what_to_do()
    if result == "执行失败！" or result == "分析失败！":
        return {
            "response": REQUIREMENT_FAIL_MESSAGE
        }

    with open(f"./todo/{config['PROJECT_NAME']}/todo.md", "r", encoding="utf-8") as f:
        todo_content = f.read()

    user_input = f"""
    根据需求生成执行计划，需求内容如下：
    {todo_content}
    """

    todo_list = []
    improve_opinion = ""
    while True:
        user_prompt = user_input
        if len(improve_opinion) > 0:
            user_prompt = f"结合对原计划的改进意见，改进意见如下：\n{improve_opinion}\n\n{user_prompt}"

        if os.path.exists(f"./todo/{config['PROJECT_NAME']}/todo_list.md"):
            with open(f"./todo/{config['PROJECT_NAME']}/todo_list.md", "r", encoding="utf-8") as f:
                user_prompt = f"结合原todo_list内容，todo_list内容如下：\n{f.read()}\n\n{user_prompt}"
            
        result = await agent.ainvoke(user_prompt)
        steps_content = "\n\n".join(result.steps if result.steps else [])
        with open(f"./todo/{config['PROJECT_NAME']}/todo_list.md", "w+", encoding="utf-8") as f:
            f.write(steps_content)

        while True:
            user_check_opinion = input(f"请检查执行计划，执行计划内容详见./todo/{config['PROJECT_NAME']}/todo_list.md。如果你认为没有必要继续修改，请输入pass。如果你认为有必要继续修改，请输入reject：")
            if user_check_opinion == "pass" or user_check_opinion == "reject":
                break
         
        if user_check_opinion == "pass":
            with open(f"./todo/{config['PROJECT_NAME']}/todo_list.md", "r", encoding="utf-8") as f:
                temp_todo_list = f.read().splitlines()
                todo_list = [step for step in temp_todo_list if len(step.strip()) > 0]
            
            break

        improve_opinion_wrapper = await improve_opinion_agent.ainvoke(f"""
            请根据原计划和需求，给出改进意见：
            原计划：
            {steps_content}
            需求：
            {todo_content}

            注意！
            1. 执行计划的团队的能力包括：分析项目代码、编写代码和文档、创建文件夹、删除文件夹或文件、扫描项目目录和阅读需求文档。他们无法执行超出他们能力范围的命令！
        """)

        improve_opinion = improve_opinion_wrapper.content
    
    return {
        "plan": todo_list
    }

if __name__ == "__main__":
    result = asyncio.run(execute_plan_node({
        "input": ""
    }))
    print(result)
