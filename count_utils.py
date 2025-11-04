from pathlib import Path
from constants import CODE_EXTENSIONS
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

import os
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

config = json.load(open("./config.json", "r", encoding="utf-8"))

qwen_model = ChatOpenAI(
    model="qwen-plus",
    openai_api_key=config["QWEN_API_KEY"],
    openai_api_base=config["QWEN_API_BASE"],
    temperature=0.7
)

dp_model = ChatOpenAI(
    model="deepseek-chat",
    openai_api_key=config["DEEPSEEK_API_KEY"],
    openai_api_base=config["DEEPSEEK_API_BASE"],
    temperature=0.4
)

summary_prompt = ChatPromptTemplate.from_template([
    (
        "system",
        f"""
        你是一位非常专业的总结专家，善于抓住项目更新日志中的重点内容。请把项目更新日志的字数控制在{config["SUMMARY_MAX_LENGTH"]}个token以内。
        注意！
        你必须重点保留更新了内容的文件、新增的文件、删除的文件以及有语法错误或逻辑错误的文件的描述。
        其他文件的描述可以适当简化。
        """
    ),
    ("user", "{input}")
])

summary_pro = summary_prompt | qwen_model

markdown_prompt = ChatPromptTemplate.from_template([
    (
        "system",
        """
        你是一位非常专业的markdown专家，善于将文本转换为markdown格式。
        注意！
        美化规则是：
            1. 你不允许修改内容，只能美化文档的结构。
            2. 你必须按照markdown的语法进行美化。
            3. 你不能改变段落的前后顺序。
        
        你返回的文档内容必须符合markdown格式，但内容不要带上```markdown！
        你只返回美化后的markdown文档内容，不要返回任何多余的内容！
        """
    ),
    ("user", "{input}")
])

markdown_pro = markdown_prompt | dp_model

def summarize_project() -> str:
    if not os.path.exists(f"./dist/{config["PROJECT_NAME"]}"):
        return "项目不存在"
    
    dist_path = Path(f"./dist/{config["PROJECT_NAME"]}")

    skip_dirs = []
    with open(f".spanignore", "r", encoding="utf-8") as f:
        skip_dirs = f.read().splitlines()

    skip_dirs = [dir.strip() for dir in skip_dirs if len(dir.strip()) > 0]

    content = ""

    for file in dist_path.glob("**/*"):
        if any(part in skip_dirs for part in file.parts):
            continue

        if file.is_file():
            if len(content) > config["SUMMARY_MAX_LENGTH"]:
                content = summary_pro.invoke(f"当前项目更新日志内容如下所示：\n{content}").content.strip()

            try:
                file_content = file.read_text(encoding="utf-8")
                summary_result = summary_pro.invoke(f"请总结文件内容，文件内容如下所示：\n{file_content}").content.strip()
                content += f"文件{file.name}的内容总结：\n{summary_result}\n\n"
            except Exception as e:
                continue

    prompt = f"请根据markdown文档内容{content}，美化markdown文档的结构。"
    md_pretty_content = markdown_pro.invoke(prompt).content.strip()
    if md_pretty_content.startswith("```markdown"):
        md_pretty_content = md_pretty_content.replace("```markdown", "")
    if md_pretty_content.endswith("```"):
        md_pretty_content = md_pretty_content.replace("```", "")

    with open(f"./dist/{config["PROJECT_NAME"]}/summary.md", "w+", encoding="utf-8") as f:
        f.write(md_pretty_content)

    return md_pretty_content