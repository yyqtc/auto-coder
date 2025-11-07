from custom_type import ActionReview

import os
import shutil
import json
import logging

config = json.load(open("./config.json", "r", encoding="utf-8"))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


async def counter_node(state: ActionReview) -> ActionReview:
    count = 0
    if "count" in state:
        count = state["count"]

    logger.info(f"counter_node count: {count}")

    if "response" in state and len(state["response"]) > 0:
        return {"response": state["response"]}

    if count != 0 and os.path.exists(f"./opinion/{config['PROJECT_NAME']}.md"):
        check_input = ""
        while check_input != "pass" and check_input != "reject":
            check_input = input(
                f"请检查审核意见->./opinion/{config['PROJECT_NAME']}.md。如果你认为没有必要继续修改，请输入pass。如果你认为有必要继续修改，请输入reject："
            )

        if check_input == "pass":
            return {"response": "pass"}

    if os.path.exists(f"./dist/{config['PROJECT_NAME']}"):
        if os.path.exists(f"./history/{config['PROJECT_NAME']}"):
            shutil.rmtree(f"./history/{config['PROJECT_NAME']}")

        shutil.copytree(
            f"./dist/{config['PROJECT_NAME']}",
            f"./history/{config['PROJECT_NAME']}",
            dirs_exist_ok=True,
        )

    return {"count": count}
