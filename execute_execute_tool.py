from langchain.tools import tool

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

def write_code_or_file(prompt: str) -> str:
    """
        让代码专家根据prompt编写代码或文件

        Args:
            prompt: 编写代码或文件的prompt

        Returns:
            如果执行成功，返回代码专家的应答信息
            如果执行失败，返回“执行失败”
    """
    env_vars = {
        "CURSOR_API_KEY": config["CURSOR_API_KEY"]
    }

    if config["MOCK"]:
        execute_result = _execute_script_subprocess(f"python {config['SIM_CURSOR_PATH']} -p --force '{prompt}'", env_vars=env_vars)
    else:
        execute_result = _execute_script_subprocess(f"{config['CURSOR_PATH']} -p --force '{prompt}'", env_vars=env_vars)
    
    return f"执行结果: {execute_result}"


if __name__ == "__main__":
    print(write_code_or_file("请在当前目录下创建一个hello.txt文件"))
