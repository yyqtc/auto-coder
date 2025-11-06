from custom_type import ActionReview
from langgraph.graph import StateGraph, START, END
from count_node import counter_node
from review_node import review_node
from execute_zgraph import execute_zgraph

import os
import json
import asyncio
import argparse

config = json.load(open("./config.json", "r", encoding="utf-8"))

parser = argparse.ArgumentParser()
parser.add_argument("--count", type=int, default=0)
args = parser.parse_args()

count = args.count

def _init_project_structure():
    os.makedirs("experiment", exist_ok=True)
    os.makedirs("history", exist_ok=True)
    os.makedirs("opinion", exist_ok=True)
    os.makedirs("todo", exist_ok=True)
    os.makedirs("dist", exist_ok=True)

def _should_end(state: ActionReview):
    if "response" in state and len(state["response"]) > 0:
        return END
    else:
        return "execute_graph"

def _init_graph():
    workflow = StateGraph[ActionReview, None, ActionReview, ActionReview](ActionReview)
    workflow.add_node("counter", counter_node)
    workflow.add_node("review", review_node)
    workflow.add_node("execute_graph", execute_zgraph)

    workflow.add_edge(START, "counter")
    workflow.add_conditional_edges("counter", _should_end, ["execute_graph", END])
    workflow.add_edge("execute_graph", "review")
    workflow.add_edge("review", "counter")

    app = workflow.compile()

    return app

app = _init_graph()

async def main(count=0):
    _init_project_structure()

    if not os.path.exists(f"./todo/{config['PROJECT_NAME']}"):
        print("项目需求不存在")
        return 

    recursion_limit = config.get("RECURSION_LIMIT", 50)
    result = await app.ainvoke({
        "count": count,
    }, {
        "recursion_limit": recursion_limit
    })

    print("result: ", result.get("response", "响应为空"))

if __name__ == "__main__":
    asyncio.run(main(count))
