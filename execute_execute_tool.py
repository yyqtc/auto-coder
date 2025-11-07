from langchain.tools import tool
from typing import List

import os
import json
import shlex
import subprocess
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

project_path = os.path.abspath(os.path.dirname(__file__))

config = json.load(open(os.path.join("./config.json"), "r", encoding="utf-8"))

def _execute_script_subprocess(script_command, env_vars=None) -> str:
    """
    使用 subprocess 模块执行脚本（推荐）
    
    Args:
        script_command: 要执行的命令字符串
        env_vars: 要传递的环境变量字典，例如 {"CURSOR_API_KEY": "..."}
    """
    try:
        # 如果需要在命令前设置环境变量，可以在命令中导出
        base_command = f"cd {project_path}/dist/{config['PROJECT_NAME']}"
        full_command = ""
        if env_vars:
            env_exports = ' '.join([f"export {k}={shlex.quote(str(v))}" for k, v in env_vars.items()])
            full_command = f"{base_command} && {env_exports} && {script_command}"
        else:
            full_command = f"{base_command} && {script_command}"
        
        result = subprocess.run(
            ["bash", "-c", full_command],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',  # 如果遇到无法解码的字符，用替换字符代替而不是抛出异常
            check=True
        )
        logger.info("执行成功！")
        logger.info(f"输出: {result.stdout}")
        return result.stdout
    except subprocess.CalledProcessError as e:
        logger.error("执行失败！")
        logger.error(f"错误: {e.stderr}")
        return "执行失败！"
    except Exception as e:
        logger.error(f"详细信息: {e}")
        return "执行失败！"

@tool
def rm(path: str) -> str:
    """
        删除项目目录下指定相对路径的文件或目录的助手

        Args:
            path: 要删除的文件或目录的相对路径

        Returns:
            如果执行成功，返回"删除文件成功"
            如果文件不存在，返回"文件不存在"
    """
    import shutil

    logger.info("use rm tool")

    file_or_dir_path = os.path.join(project_path, "dist", config["PROJECT_NAME"], path)
    if not os.path.exists(file_or_dir_path):
        return "文件或目录不存在"

    if os.path.isfile(file_or_dir_path):
        os.remove(file_or_dir_path)
    elif os.path.isdir(file_or_dir_path):
        shutil.rmtree(file_or_dir_path)

    return f"删除文件成功"

@tool
def code_professional(prompt: str) -> str:
    """
        可以分析项目代码、编写代码和文档的代码专家

        Args:
            prompt: 分析项目代码、编写代码或文件的prompt

        Returns:
            如果执行成功，返回代码专家的应答信息
            如果执行失败，返回“执行失败”
    """
    env_vars = {
        "CURSOR_API_KEY": config["CURSOR_API_KEY"]
    }

    logger.info("use code_professional tool")
    logger.info(f"我收到的命令是: {prompt}")

    if config["MOCK"]:
        execute_result = _execute_script_subprocess(f"python {config['SIM_CURSOR_PATH']} -p --force '{prompt}'", env_vars=env_vars)
    else:
        execute_result = _execute_script_subprocess(f"{config['CURSOR_PATH']} -p --force '{prompt}'", env_vars=env_vars)
    
    return f"执行结果: {execute_result}"

@tool
def mkdir(path: str) -> str:
    """
        在项目目录下创建指定相对路径的目录的助手

        Args:
            path: 要创建的目录路径

        Returns:
            如果执行成功，返回创建目录的应答信息
            如果执行失败，返回“执行失败”
    """
    logger.info("use mkdir tool")

    dir_path = os.path.join(project_path, "dist", config["PROJECT_NAME"], path)
    try:
        os.makedirs(dir_path, exist_ok=True)
        return f"创建目录 {path} 成功"
    except Exception as e:
        logger.error(f"创建目录 {path} 失败: {e}")
        return "执行失败！"

@tool
def list_files(path: str) -> List[str] | str:
    """
        列出工作目录下指定相对路径下的所有文件的助手

        Args:
            path: 要列出文件的目录的相对路径

        Returns:
            如果目录不存在，返回“目录不存在”
            如果执行成功，返回文件列表
    """
    logger.info("use list_files tool")

    if not os.path.exists(f"{project_path}/dist/{config['PROJECT_NAME']}/{path}"):
        return "目录不存在"

    dir_path = os.path.join(project_path, "dist", config["PROJECT_NAME"], path)
    return os.listdir(dir_path)

@tool
def search_todo_dir(file_name: str) -> List[str]:
    """
        可以浏览需求目录下所有文件的助手，告诉他文件名，他会在todo目录下搜索文件，如果文件存在，返回文件内容，否则返回文件不存在。
        Args:
            file_name: 要搜索的文件名

        Returns:
            如果文件存在，返回文件内容
            如果文件不存在，返回“文件不存在”
    """
    logger.info("use search_todo_dir tool")
    if not os.path.exists(f"{project_path}/todo/{config['PROJECT_NAME']}/{file_name}"):
        return "文件不存在"
    
    with open(f"{project_path}/todo/{config['PROJECT_NAME']}/{file_name}", "r", encoding="utf-8") as f:
        return f.read()


tools = [code_professional, mkdir, list_files, rm, search_todo_dir]
