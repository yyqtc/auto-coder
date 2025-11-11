from langgraph.graph import StateGraph, START, END
from execute_custom_type import PlanExecute
from custom_type import ActionReview
from execute_plan_node import execute_plan_node
from execute_replan_node import execute_replan_node
from execute_execute_node import execute_node
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

import asyncio
import json
import stat
import logging
import shutil
import os

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
        你只需要保留完成了哪些需求，遗留了哪些问题，重复出现的信息和除了需求和问题之外的其他信息都删除！
        """,
        ),
        ("user", "{input}"),
    ]
)

summary_pro = summary_prompt | dp_model

def remove_readonly(func, path, _):
    """用于处理只读文件的错误回调函数"""
    os.chmod(path, stat.S_IWRITE)
    func(path)


def _should_end(state: PlanExecute):
    if "response" in state and state["response"]:
        return END
    else:
        return "execute_execute"


def _init_graph():
    workflow = StateGraph[PlanExecute, None, PlanExecute, PlanExecute](PlanExecute)
    workflow.add_node("execute_plan", execute_plan_node)
    workflow.add_node("execute_replan", execute_replan_node)
    workflow.add_node("execute_execute", execute_node)

    workflow.add_edge(START, "execute_plan")
    workflow.add_conditional_edges("execute_plan", _should_end, ["execute_execute", END])
    workflow.add_edge("execute_execute", "execute_replan")
    workflow.add_conditional_edges("execute_replan", _should_end, ["execute_execute", END])

    app = workflow.compile()

    return app


async def execute_zgraph(state: ActionReview) -> ActionReview:
    count = 0
    if "count" in state:
        count = state["count"]

    logger.info("正在开发项目...")

    # 每次调用时重建图，避免recursion_limit累计
    app = _init_graph()

    recursion_limit = config.get("RECURSION_LIMIT", 50)
    logger.info(f"迭代次数：{recursion_limit}")

    try:
        await app.ainvoke({"input": f"开发轮数：{count}"}, {"recursion_limit": recursion_limit})

    except Exception as e:
        logger.error(f"执行计划失败: {e}")
        dist_dir = os.path.join(".", "dist", config['PROJECT_NAME'])
        shutil.rmtree(dist_dir, onerror=remove_readonly)
        history_dir = os.path.join(".", "history", config['PROJECT_NAME'])
        if os.path.exists(history_dir):
            shutil.copytree(history_dir, dist_dir)

    finally:
        development_log_path = os.path.join(".", "dist", config['PROJECT_NAME'], "development.log")
        if os.path.exists(development_log_path):
            content = ""
            with open(development_log_path, "r", encoding="utf-8") as f:
                content_parts = f.readlines()
                for part in content_parts:
                    content += part + "\n"
                    if len(content) > config["SUMMARY_THRESHOLD"]:
                        content = summary_pro.invoke(
                            f"请适当总结项目开发日志，项目开发日志内容如下：\n{content}"
                        ).content.strip()
                        content += "\n"

            with open(development_log_path, "w", encoding="utf-8") as f:
                f.write(content)

    return {"count": count}


if __name__ == "__main__":
    result = asyncio.run(execute_zgraph({"count": 0}))

    print(result)
