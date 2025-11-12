from custom_type import ActionReview

import os
import stat
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


def remove_readonly(func, path, _):
    """用于处理只读文件的错误回调函数"""
    os.chmod(path, stat.S_IWRITE)
    func(path)


async def counter_node(state: ActionReview) -> ActionReview:
    count = 0
    if "count" in state:
        count = state["count"]

    logger.info(f"counter_node count: {count}")

    if "response" in state and len(state["response"]) > 0:
        return {"response": state["response"]}

    opinion_file_path = os.path.join(".", "opinion", f"{config['PROJECT_NAME']}.md")
    if count != 0 and os.path.exists(opinion_file_path):
        check_input = ""
        while check_input != "pass" and check_input != "reject":
            check_input = input(
                f"请检查审核意见->{opinion_file_path}。如果你认为没有必要继续修改，请输入pass。如果你认为有必要继续修改，请输入reject："
            )

        if check_input == "pass":
            return {"response": "pass"}

    dist_dir = os.path.join(".", "dist", config["PROJECT_NAME"])
    if os.path.exists(dist_dir):
        history_dir = os.path.join(".", "history", config["PROJECT_NAME"])
        if os.path.exists(history_dir):
            shutil.rmtree(history_dir, onerror=remove_readonly)

        shutil.copytree(dist_dir, history_dir, dirs_exist_ok=True)

    return {"count": count}
