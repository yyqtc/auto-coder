import json
import os
import logging
import shlex
import subprocess
import platform
import tempfile

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

config = json.load(open("config.json", "r", encoding="utf-8"))

project_path = os.path.abspath(os.path.dirname(__file__))


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
        dist_dir = os.path.join(project_path, "dist", config["PROJECT_NAME"])

        if is_windows:
            # Windows 使用 cmd /c
            # 获取目标目录所在的卷
            drive = _get_drive_letter(dist_dir)

            if drive:
                # 如果目标目录在不同卷，需要先切换到该卷
                base_command = rf"{drive} && cd {dist_dir}"
            else:
                base_command = rf"cd {dist_dir}"

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


def analyze_what_to_do(count=0, past_steps_content="", plan=""):
    env_vars = {"CURSOR_API_KEY": config["CURSOR_API_KEY"]}

    prompt = f"""
        不要等待任何提示！直接开始分析！
        我们的开发团队已经完成了以下步骤并取得了一些成果：
        {past_steps_content}

        我们的计划是：
        {plan}

        结合以上信息，检查现在项目中的代码，是否开发团队已经实现了他们描述的功能以及开发的代码是否存在问题。

        注意！
        1. 你不允许对所在目录的父目录进行写入操作！
        2. 重点回复存在的问题！不要遗漏任何问题！
        3. 请把你的分析结果写入到development_log.md文件中！
        4. 如果你发现development_log.md字数超过{config["SUMMARY_THRESHOLD"]}个token，请适当总结development_log.md文件中的内容，并用总结后的内容覆盖development_log.md文件中的内容！
        5. 记住！这是为了让其他智能体修改准备的！你不需要真的按照整理出来的问题执行任何改进计划！你只需要告诉其他智能体需要修改什么！
    """
    if count > 0:
        opinion = ""
        opinion_file = os.path.join(".", "opinion", f"{config['PROJECT_NAME']}.md")
        if os.path.exists(opinion_file):
            opinion_file = os.path.abspath(opinion_file)
            prompt += f"""

            @{opinion_file} 分析中你必须考虑审核员意见，并根据审核员意见调整分析结果。
            """

    if config["MOCK"]:
        execute_result = _execute_script_subprocess(
            f'python {config["SIM_CURSOR_PATH"]} -p "{prompt}"', env_vars=env_vars
        )
    elif platform.system() == "Windows" and "EXECUTE_PATH" in config:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", delete=False, suffix=".prompt", dir="."
        ) as temp_file:
            temp_file.write(prompt)
            temp_file_path = os.path.abspath(os.path.join(".", temp_file.name))
        execute_result = _execute_script_subprocess(
            f'{config["EXECUTE_PATH"]} -p --force --prompt-file {temp_file_path}', env_vars=env_vars
        )
    else:
        execute_result = _execute_script_subprocess(
            f'{config["CURSOR_PATH"]} -p "{prompt}"', env_vars=env_vars
        )

    return execute_result
