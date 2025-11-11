from langchain.agents import create_agent
from langchain_openai import ChatOpenAI
from custom_type import ActionReview, Action, Response, Act
from review_tool import tools

import json
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

config = json.load(open("./config.json", "r", encoding="utf-8"))


def init_agent():

    _model = ChatOpenAI(
        model="qwen-plus",
        openai_api_key=config["QWEN_API_KEY"],
        openai_api_base=config["QWEN_API_BASE"],
        temperature=0.7,
    )

    _prompt = f"""
        你是一位非常负责的审核员，我需要你根据需求文档和项目开发日志，检查项目是否实现了需求文档中的所有功能。
    """

    agent = create_agent(model=_model, system_prompt=_prompt, tools=tools, response_format=Act)

    return agent


agent = init_agent()


async def review_node(state: ActionReview) -> ActionReview:
    count = 0
    if "count" in state:
        count = state["count"]

    logger.info("正在审核项目代码是否符合使用文档的说明...")

    if count == 0:
        user_prompt = f"""
        当前你正在进行第{count}轮审核。
        如果你认为项目符合需求文档的说明，就审核通过，并结束修改迭代修改项目。
        如果你认为项目不符合需求文档的说明，就需要你将你的检查结果以审核员意见文件的形式保存，并让开发团队继续修改项目。
        如果你认为项目不需要进一步修改，请以JSON格式输出，包含action字段，action字段应该包含response字段，response字段的值为“审核通过”。
        如果你认为项目需要进一步修改，请以JSON格式输出，包含action字段，action字段应该包含count字段，count字段的数据类型为整数，count字段的值为当前审核轮数加1。
        注意！
        1. 需求中描述的需求必须被实现，不能遗漏。
        2. 适当根据项目开发日志和需求文档，提出改进意见。
        3. 你输出的意见中不要包括图片文件或是图片的base64编码，不要包括任何与项目无关的内容。
        """
        response = await agent.ainvoke({"messages": [("user", user_prompt)]})

        response = response.get("structured_response", None)

        if response is None:
            logger.warning("retry review_node - structured_response is None")
            # 避免无限递归，最多重试3次
            retry_count = state.get("_retry_count", 0)
            if retry_count >= 3:
                logger.error("review_node 重试次数过多，返回错误响应")
                return {"response": "审核失败：无法获取结构化响应"}
            new_state = {**state, "_retry_count": retry_count + 1}
            return await review_node(new_state)

        if isinstance(response.action, Action):
            return {"count": response.action.count}

        elif isinstance(response.action, Response):
            return {"response": response.action.response}
        else:
            logger.error(f"未知的action类型: {type(response.action)}")
            return {"response": "审核失败：未知的响应类型"}

    else:
        user_prompt = f"""
        当前你正在进行第{count}轮审核。
        请结合当前已有的审核意见，检查项目是否实现了需求文档中的所有功能，并检查项目是否已经修复了已有的审核意见中提出的问题。
        如果你认为项目符合需求文档的说明且具备交付条件，就审核通过，并结束修改迭代修改项目。
        如果你认为项目不符合需求文档的说明或不具备交付条件，就需要你将你的检查结果以审核员意见文件的形式保存，并让开发团队继续修改模拟sdk。
        如果你认为项目不需要进一步修改，请以JSON格式输出，包含action字段，action字段应该包含response字段，response字段的值为“审核通过”。
        如果你认为项目需要进一步修改，请以JSON格式输出，包含action字段，action字段应该包含count字段，count字段的数据类型为整数，count字段的值为当前审核轮数加1。
        注意！
        1. 需求中描述的需求必须被实现，不能遗漏。
        2. 适当根据项目开发日志和需求文档，提出改进意见。
。      3. 可以容忍优先级低的改进建议不被实现，但是中高优先级的改进建议必须被实现。
        4. 你输出的意见中不要包括图片文件或是图片的base64编码，不要包括任何与项目无关的内容。
        """
        response = await agent.ainvoke({"messages": [("user", user_prompt)]})

        response = response.get("structured_response", None)
        if response is None:
            logger.warning("retry review_node - structured_response is None")
            # 避免无限递归，最多重试3次
            retry_count = state.get("_retry_count", 0)
            if retry_count >= 3:
                logger.error("review_node 重试次数过多，返回错误响应")
                return {"response": "审核失败：无法获取结构化响应"}
            new_state = {**state, "_retry_count": retry_count + 1}
            return await review_node(new_state)

        if isinstance(response.action, Action):
            return {"count": response.action.count}

        elif isinstance(response.action, Response):
            return {"response": response.action.response}
        else:
            logger.error(f"未知的action类型: {type(response.action)}")
            return {"response": "审核失败：未知的响应类型"}
