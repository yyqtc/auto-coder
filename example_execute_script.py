"""
Python 执行脚本的多种方法示例
"""

import subprocess
import os
import json
import shlex

config = json.load(open("./config.json", "r", encoding="utf-8"))

def _set_env(key):
    if not os.environ.get(key):
        os.environ[key] = config[key]

_set_env("CURSOR_API_KEY")

def execute_script_subprocess(script_command, env_vars=None):
    """
    使用 subprocess 模块执行脚本（推荐）
    
    Args:
        script_command: 要执行的命令字符串
        env_vars: 要传递的环境变量字典，例如 {"CURSOR_API_KEY": "..."}
    """
    try:
        # 如果需要在命令前设置环境变量，可以在命令中导出
        if env_vars:
            env_exports = ' '.join([f"export {k}={shlex.quote(str(v))}" for k, v in env_vars.items()])
            full_command = f"{env_exports} && {script_command}"
        else:
            full_command = script_command
        
        result = subprocess.run(
            ["bash", "-c", full_command],
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace',  # 如果遇到无法解码的字符，用替换字符代替而不是抛出异常
            check=True
        )
        print("执行成功！")
        print("输出:", result.stdout)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print("执行失败！")
        print("错误:", e.stderr)
        return None
    except FileNotFoundError as e:
        print("错误: 找不到 WSL 命令")
        print(f"详细信息: {e}")
        return None




if __name__ == "__main__":

    # 准备环境变量
    env_vars = {
        "CURSOR_API_KEY": config["CURSOR_API_KEY"]
    }
    
    # script_command = "/root/.local/bin/cursor-agent -p '在这个目录下创建一个hello.txt文件'"
    script_command = f"python {config['SIM_SDK_PATH']} -p '在这个目录下创建一个hello.txt文件'"

    print("=" * 50)
    print("方法1: 通过 WSL 执行 shell 脚本（以 root 用户）")
    print("=" * 50)
    execute_script_subprocess(script_command, env_vars=env_vars)
    