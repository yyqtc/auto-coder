from langchain.tools import tool
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from constants import CODE_EXTENSIONS

import json
import os
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

summary_prompt = ChatPromptTemplate.from_messages([
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

lint_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        f"""
        你是一位非常专业的代码检查专家，善于检查代码是否存在语法错误或逻辑错误。
        注意！
        """
    ),
    ("user", "{input}")
])

lint_pro = lint_prompt | qwen_model

code_prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """
        你是一位非常专业的代码检查专家，善于总结代码实现了哪些功能。
        注意！
        你不能遗漏代码实现的功能。
        对于每个函数你都应该采用结构化输出，主要包含函数名、函数参数、函数返回值、函数实现的功能的详细描述。
        """
    ),
    ("user", "{input}")
])

code_pro = code_prompt | qwen_model

markdown_prompt = ChatPromptTemplate.from_messages([
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
    with open(f"./opinion/{config['PROJECT_NAME']}.md", "w+", encoding="utf-8") as f:
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
    if not os.path.exists(f"./opinion/{config['PROJECT_NAME']}.md"):
        return "文件不存在"
    
    with open(f"./opinion/{config['PROJECT_NAME']}.md", "r", encoding="utf-8") as f:
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
    if not os.path.exists(f"./todo/{config['PROJECT_NAME']}/todo.md"):
        return "文件不存在"
    
    with open(f"./todo/{config['PROJECT_NAME']}/todo.md", "r", encoding="utf-8") as f:
        return f.read()

@tool
def check_project_code() -> str:
    """
    根据上一轮的项目代码，总结项目当前的做了哪些修改，判断项目的代码是否存在语法错误或逻辑错误。

    Args:
        无
    
    Returns:
        如果项目不存在，返回“项目不存在”
        如果项目存在，返回项目当前的做了哪些修改，判断项目的代码是否存在语法错误或逻辑错误。
    """
    logger.info("use check_project_code tool")
    if not os.path.exists(f"./dist/{config['PROJECT_NAME']}"):
        return "项目不存在"
    
    from pathlib import Path
    import filecmp
    import difflib

    history_path = Path(f"./history/{config['PROJECT_NAME']}")
    dist_path = Path(f"./dist/{config['PROJECT_NAME']}")

    skip_dirs = []
    with open(f".spanignore", "r", encoding="utf-8") as f:
        skip_dirs = f.read().splitlines()

    skip_dirs = [dir.strip() for dir in skip_dirs if len(dir.strip()) > 0]

    history_check_flag = True
    if not history_path.exists():
        history_check_flag = False

    content = ""

    for file in dist_path.glob("**/*"):
        if any(part in skip_dirs for part in file.parts):
            continue

        if file.is_file():
            if len(content) > config["SUMMARY_MAX_LENGTH"]:
                content = summary_pro.invoke(f"当前项目更新日志内容如下所示：\n{content}").content.strip()
                
            history_file = history_path / file.name
            if history_check_flag and history_file.exists():
                if not filecmp.cmp(file, history_file, shallow=False):
                    content += f"文件{file.name}没有发生变化\n\n"

                elif file.suffix.lower() in CODE_EXTENSIONS:
                    file_content = file.read_text(encoding="utf-8")
                    diff_result = code_pro.invoke(f"请总结代码的功能,代码内容如下所示：\n{file_content}").content.strip()
                    content += f"修改后文件{file.name}实现的功能：\n{diff_result}\n\n"

                else:
                    try:
                        history_file_content = history_file.read_text(encoding="utf-8")
                        history_file_content = history_file_content.splitlines()
                        file_content = file.read_text(encoding="utf-8")
                        file_content = file_content.splitlines()
                        diff_result = difflib.unified_diff(
                            history_file_content, file_content,
                            fromfile=f"history/{config['PROJECT_NAME']}/{file.name}",
                            tofile=f"dist/{config['PROJECT_NAME']}/{file.name}",
                            lineterm=''
                        )
                        diff_result = "\n".join(diff_result)
                        content += f"文件{file.name}修改前后的内容差异：\n{diff_result}\n\n"

                    except Exception as e:
                        continue
            elif file.suffix.lower() in CODE_EXTENSIONS:
                file_content = file.read_text(encoding="utf-8")
                diff_result = code_pro.invoke(f"请总结代码的功能,代码内容如下所示：\n{file_content}").content.strip()
                content += f"新建文件{file.name}实现的功能：\n{diff_result}\n\n"
            else:
                try:
                    file_content = file.read_text(encoding="utf-8")
                    summary_result = summary_pro.invoke(f"请总结文件内容，文件内容如下所示：\n{file_content}").content.strip()
                    content += f"文件{file.name}的内容总结：\n{summary_result}\n\n"
                except Exception as e:
                    continue
    
    for file in history_path.glob("**/*"):
        if any(part in skip_dirs for part in file.parts):
            continue

        if file.is_file():
            dist_path = dist_path / file.name
            if not dist_path.exists():
                content += f"文件{file.name}被删除了\n\n"

    prompt = f"请根据markdown文档内容{content}，美化markdown文档的结构。"
    md_pretty_content = markdown_pro.invoke(prompt).content.strip()
    if md_pretty_content.startswith("```markdown"):
        md_pretty_content = md_pretty_content.replace("```markdown", "")
    if md_pretty_content.endswith("```"):
        md_pretty_content = md_pretty_content.replace("```", "")

    with open(f"./dist/{config['PROJECT_NAME']}/summary.md", "w+", encoding="utf-8") as f:
        f.write(md_pretty_content)

    return md_pretty_content


tools = [read_todo_content, check_project_code, write_opinion_file, read_opinion_file]
