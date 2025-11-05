from langgraph.graph import StateGraph, START, END
from execute_custom_type import PlanExecute
from custom_type import ActionReview
from execute_plan_node import execute_plan_node
from execute_replan_node import execute_replan_node
from execute_execute_node import execute_node

import asyncio
import json
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
    workflow.add_conditional_edges(
        "execute_plan", 
        _should_end,
        ["execute_execute", END]
    )
    workflow.add_edge("execute_execute", "execute_replan")
    workflow.add_conditional_edges(
        "execute_replan",
        _should_end,
        ["execute_execute", END]
    )
    
    app = workflow.compile()

    return app

app = _init_graph()

async def execute_zgraph(state: ActionReview) -> ActionReview:
    count = 0
    if "count" in state:
        count = state["count"]

    logger.info("正在开发项目...")

    recursion_limit = config.get("RECURSION_LIMIT", 50)

    await app.ainvoke({
        "input": f"开发轮数：{count}",
        config: {
            "recursion_limit": recursion_limit
        }
    })

    return {
        "count": count
    }

if __name__ == "__main__":
    result = asyncio.run(execute_zgraph({
        "count": 0
    }))

    print(result)
