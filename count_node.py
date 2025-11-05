from custom_type import ActionReview
from count_utils import summarize_project
from langgraph.graph import END

import os
import shutil
import json
import logging

config = json.load(open("./config.json", "r", encoding="utf-8"))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

async def counter_node(state: ActionReview) -> ActionReview:
    count = 0
    if "count" in state:
        count = state["count"]
    
    logger.info(f"counter_node count: {count}")

    if os.path.exists(f"./dist/{config['PROJECT_NAME']}"):
        summarize_project()
    
    if "response" in state and len(state["response"]) > 0:
        return {
            "response": state["response"]
        }

    
    if count != 0:
        check_input = ""
        while check_input != "pass" and check_input != "reject":
            check_input = input(f"请检查审核意见->./opnion/opinion.txt。如果你认为没有必要继续修改，请输入“pass”。如果你认为有必要继续修改，请输入“reject”：")
        
        if check_input == "pass":

            return {
                "response": "pass"
            }

    if os.path.exists(f"./dist/{config['PROJECT_NAME']}"):
        shutil.copytree(f"./dist/{config['PROJECT_NAME']}", f"./history/{config['PROJECT_NAME']}")

    return {
        "count": count
    }
