import json
import os
import logging
import shlex
import subprocess

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

config = json.load(open("config.json", 'r', encoding="utf-8"))

project_path = os.path.abspath(os.path.dirname(__file__))

def _execute_script_subprocess(script_command, env_vars=None) -> str:
    """
    使用 subprocess 模块执行脚本（推荐）
    
    Args:
        script_command: 要执行的命令字符串
        env_vars: 要传递的环境变量字典，例如 {"CURSOR_API_KEY": "..."}
    """
    try:
        # 如果需要在命令前设置环境变量，可以在命令中导出
        base_command = f"cd {project_path}/todo/{config['PROJECT_NAME']}"
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

def analyze_what_to_do(count=0, past_steps_content="", todo="", plan=""):
    env_vars = {
        "CURSOR_API_KEY": config["CURSOR_API_KEY"]
    }

    prompt = """
        我们已经完成了以下步骤并取得了一些成果：
        {past_steps_content}

        我们的计划是：
        {plan}

        根据以上信息分析这个项目现在的完成情况，并以markdown格式输出
    """
    if count > 0:
        opinion = ""
        opinion_file = f"./opinion/{config['PROJECT_NAME']}.md"
        if os.path.exists(opinion_file):
            with open(opinion_file, "r", encoding="utf-8") as f:
                opinion = f.read()

        if len(opinion) > 0:
            prompt += f"""

            注意！
            分析中你必须考虑审核员意见，并根据审核员意见调整分析结果。
            审核员意见如下：
            {opinion}
            """

    if config["MOCK"]:
        return _execute_script_subprocess(f"python {config['SIM_CURSOR_PATH']} -p --force --output-format text '{prompt}'", env_vars=env_vars)
    else:
        return _execute_script_subprocess(f"{config['CURSOR_PATH']} -p --output-format text '{prompt}'", env_vars=env_vars)