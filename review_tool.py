from langchain.tools import tool
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from constants import CODE_EXTENSIONS

import json
import os
import logging
import asyncio

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

config = json.load(open("./config.json", "r", encoding="utf-8"))

dp_model = ChatOpenAI(
    model="deepseek-chat",
    openai_api_key=config["DEEPSEEK_API_KEY"],
    openai_api_base=config["DEEPSEEK_API_BASE"],
    temperature=0.4,
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

summary_pro = summary_prompt | dp_model


@tool
def write_opinion_file(content: str) -> str:
    """
    写入审核员意见文件的内容

    Args:
        content: 文件的内容

    Returns:
        返回字符串“文件写入成功”
    """
    logger.info("use write_opinion_file tool")
    opinion_file_path = os.path.join(".", "opinion", f"{config['PROJECT_NAME']}.md")
    with open(opinion_file_path, "w+", encoding="utf-8") as f:
        f.write(content)

    return "文件写入成功"


@tool
def read_opinion_file() -> str:
    """
    读取审核员意见文件的内容

    Args:
        无

    Returns:
        如果文件不存在，返回“文件不存在”
        如果文件存在，返回文件的内容
    """
    logger.info("use read_opinion_file tool")
    opinion_file_path = os.path.join(".", "opinion", f"{config['PROJECT_NAME']}.md")
    if not os.path.exists(opinion_file_path):
        return "文件不存在"

    with open(opinion_file_path, "r", encoding="utf-8") as f:
        return f.read()


@tool
def read_todo_content() -> str:
    """
    读取项目的需求文档内容

    Args:
        无

    Returns:
        如果文件不存在，返回“文件不存在”
        如果文件存在，返回文件的内容
    """
    logger.info("use read_todo_content tool")
    todo_file_path = os.path.join(".", "todo", config["PROJECT_NAME"], "todo.md")
    if not os.path.exists(todo_file_path):
        return "文件不存在"

    with open(todo_file_path, "r", encoding="utf-8") as f:
        return f.read()


@tool
def read_development_log() -> str:
    """
    读取项目开发日志内容

    Args:
        无

    Returns:
        如果文件不存在，返回“文件不存在”
        如果文件存在，返回文件的内容
    """
    logger.info("use read_development_log tool")
    development_log_path = os.path.join(".", "dist", config["PROJECT_NAME"], "development_log.md")
    if not os.path.exists(development_log_path):
        return "文件不存在"

    with open(development_log_path, "r", encoding="utf-8") as f:
        development_log = f.read()
        development_log_parts = development_log.split("\n")
        compressed_development_log = ""
        for part in development_log_parts:
            if len(compressed_development_log) + len(part) > config["SUMMARY_THRESHOLD"]:
                compressed_development_log = summary_pro.invoke(
                    f"请适当总结项目开发日志，只保留完成了哪些需求，项目开发日志内容如下：\n{compressed_development_log}"
                ).content.strip()
                compressed_development_log += "\n"

            compressed_development_log += part + "\n"

    with open(development_log_path, "w", encoding="utf-8") as f:
        f.write(compressed_development_log)

    return compressed_development_log


tools = [read_todo_content, write_opinion_file, read_opinion_file, read_development_log]
