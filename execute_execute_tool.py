from langchain.tools import tool
from typing import List

import os
import stat
import json
import shlex
import subprocess
import logging
import platform
import tempfile

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

project_path = os.path.abspath(os.path.dirname(__file__))

config = json.load(open(os.path.join("./config.json"), "r", encoding="utf-8"))

def remove_readonly(func, path, exc_info):
    """用于处理只读文件的错误回调函数"""
    os.chmod(path, stat.S_IWRITE)
    func(path)


def _get_drive_letter(path):
    """
    获取路径所在的卷（驱动器字母）
    
    Args:
        path: 文件或目录路径
        
    Returns:
        在Windows上返回驱动器字母（如 'C:'），在Linux/Mac上返回空字符串
    """
    if platform.system() == "Windows":
        drive, _ = os.path.splitdrive(os.path.abspath(path))
        return drive
    return ""


def _execute_script_subprocess(script_command, env_vars=None) -> str:
    """
    使用 subprocess 模块执行脚本（推荐）

    Args:
        script_command: 要执行的命令字符串
        env_vars: 要传递的环境变量字典，例如 {"CURSOR_API_KEY": "..."}
    """
    try:
        # 检测操作系统
        is_windows = platform.system() == "Windows"
        
        # 如果需要在命令前设置环境变量，可以在命令中导出
        dist_dir = os.path.join(project_path, "dist", config['PROJECT_NAME'])
        
        if is_windows:
            # Windows 使用 cmd /c
            # 获取目标目录所在的卷
            drive = _get_drive_letter(dist_dir)
            
            if drive:
                # 如果目标目录在不同卷，需要先切换到该卷
                base_command = rf"{drive} && cd {dist_dir}"
            else:
                base_command = rf"cd {dist_dir}"


            full_command = ""
            if env_vars:
                env_exports = " && ".join(
                    [f"set {k}={shlex.quote(str(v))}" for k, v in env_vars.items()]
                )
                full_command = f"{base_command} && {env_exports} && {script_command}"
            else:
                full_command = f"{base_command} && {script_command}"
            
            result = subprocess.run(
                ["cmd", "/c", full_command],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                check=True,
            )
        else:
            # Linux/Unix 使用 bash -c
            base_command = f"cd {shlex.quote(dist_dir.replace(os.sep, '/'))}"
            full_command = ""
            if env_vars:
                env_exports = " ".join(
                    [f"export {k}={shlex.quote(str(v))}" for k, v in env_vars.items()]
                )
                full_command = f"{base_command} && {env_exports} && {script_command}"
            else:
                full_command = f"{base_command} && {script_command}"
            
            result = subprocess.run(
                ["bash", "-c", full_command],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                check=True,
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
        shutil.rmtree(file_or_dir_path, onerror=remove_readonly)

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
    env_vars = {"CURSOR_API_KEY": config["CURSOR_API_KEY"]}

    logger.info("use code_professional tool")
    logger.info(f"我收到的命令是: {prompt}")

    prompt += """
    
    注意！
    1. 你编写的文档、代码中不准使用emoji！
    2. 你编写的代码中必须抑制除了打印错误信息和结果信息以外的其他打印信息！
    """

    prompt = "不要等待任何提示！直接开始编写代码！\n\n" + prompt

    if " " in config["PROJECT_NAME"]:
        project_name = f"\"{config['PROJECT_NAME']}\""
    else:
        project_name = config['PROJECT_NAME']

    if config["MOCK"]:
        execute_result = _execute_script_subprocess(
            f'python {config["SIM_CURSOR_PATH"]} -p --force "{prompt}"', env_vars=env_vars
        )
    elif platform.system() == "Windows" and "EXECUTE_PATH" in config:
        with tempfile.NamedTemporaryFile(
            mode='w', 
            encoding='utf-8',
            delete=False, 
            suffix=".prompt",
            dir="."
        ) as temp_file:
            temp_file.write(f"@../../todo/{project_name} \n{prompt}")
            temp_file_path = os.path.abspath(os.path.join(".", temp_file.name))

        logger.info(f"临时提示词文件路径: {temp_file_path}")

        execute_result = _execute_script_subprocess(
            f'{config["EXECUTE_PATH"]} -p --force --prompt-file {temp_file_path}',
            env_vars=env_vars,
        )
    else:
        execute_result = _execute_script_subprocess(
            f'{config["CURSOR_PATH"]} -p --force "@../../todo/{project_name} {prompt}"',
            env_vars=env_vars,
        )

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

    dir_path = os.path.join(project_path, "dist", config["PROJECT_NAME"], path)
    if not os.path.exists(dir_path):
        return "目录不存在"
    return os.listdir(dir_path)


@tool
def search_todo_dir(file_name: str) -> List[str] | str:
    """
    可以浏览需求目录下所有文件的助手，告诉他文件名，他会在todo目录下搜索文件，如果文件存在，返回文件内容，否则返回文件不存在。
    Args:
        file_name: 要搜索的文件名

    Returns:
        如果文件存在，返回文件内容
        如果文件不存在，返回需求目录下所有文件名的列表
    """
    logger.info("use search_todo_dir tool")
    todo_file_path = os.path.join(project_path, "todo", config['PROJECT_NAME'], file_name)
    if not os.path.exists(todo_file_path):
        todo_dir = os.path.join(project_path, "todo", config['PROJECT_NAME'])
        return os.listdir(todo_dir)

    with open(todo_file_path, "r", encoding="utf-8") as f:
        return f.read()


tools = [code_professional, mkdir, list_files, rm, search_todo_dir]
