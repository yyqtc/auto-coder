from custom_type import ActionReview
from langgraph.graph import StateGraph, START, END
from count_node import counter_node
from review_node import review_node
from execute_zgraph import execute_zgraph

import os
import asyncio

def _init_project_structure():
    os.makedirs("experiment", exist_ok=True)
    os.makedirs("history", exist_ok=True)
    os.makedirs("opnion", exist_ok=True)
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

async def main():
    _init_project_structure()

    result = await app.ainvoke({
        "count": 0
    })

    print("result: ", result.get("response", "响应为空"))

if __name__ == "__main__":
    asyncio.run(main())
