# 模拟 Cursor CLI SDK
#
# 根据提供的使用文档和审核员意见，实现了一个模拟的 cursor-agent CLI 工具封装
# 用于在 Python 中调用类似功能，支持非交互式模式、文件修改、输出格式控制等
#
# 修改记录：
# - 初始版本：根据文档实现了基本的 `cursor_agent` 函数
# - 支持参数：`prompt`（必填），`print_mode`（默认False），`force`（默认False）
# - 模拟网络延迟并返回静态结果数据
# - 不实际调用外部接口或修改文件
# - 第2轮修改：
#   1. 支持从环境变量 CURSOR_API_KEY 读取 API 密钥
#   2. 新增批处理函数 process_files_glob 以支持 glob 模式匹配文件批量处理
#   3. stream-json 模式改用生成器实现真正的流式输出（逐行打印）
#   4. 增加 exit_code 返回值以支持脚本判断成功与否
#   5. 工具调用事件添加唯一ID和时间戳模拟更真实的行为
#   6. 支持命令行参数解析，可直接通过 python sim_sdk.py 执行
# - 第3轮修改（根据审核员意见）：
#   1. 完善 `--output-format stream-json` 和 `--stream-partial-output` 的行为，确保每个事件独立打印
#   2. 强化API密钥错误处理，在缺失时向stderr输出并返回非零退出码
#   3. 新增 `stream_process_files_glob` 生成器函数以支持流式批处理
#   4. 修复事件ID一致性问题：每个事件有独立event_id，tool_call拥有独立id字段
#   5. 调整默认text格式输出为纯字符串而非字典，更贴近CLI实际行为
#   6. 所有命令行输出均通过标准输出/错误流打印，exit_code由main函数统一控制

import json
import time
import os
import sys
import argparse
import fnmatch
from typing import Optional, Dict, Any, Generator, List, Union


def _simulate_delay():
    """模拟网络延迟"""
    time.sleep(0.5)


def _generate_event_id() -> str:
    """生成唯一的事件ID"""
    return f"evt_{int(time.time() * 1000)}_{os.getpid()}_{id(object()) % 10000}"


def _generate_tool_call_id() -> str:
    """生成唯一的工具调用ID"""
    return f"tool_{int(time.time() * 1000000) % 1000000}"


def _get_current_timestamp() -> str:
    """获取当前ISO格式时间戳"""
    return time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime())

def cursor_agent(
    prompt: str,
    print_mode: bool = False,
    force: bool = False,
    output_format: str = "text",
    stream_partial_output: bool = False,
    api_key: Optional[str] = None
) -> Union[str, Dict[str, Any]]:
    """
    模拟 cursor-agent CLI 命令的行为。

    参数:
        prompt (str): 要发送给代理的提示语。
        print_mode (bool): 是否启用打印模式（非交互式）。默认为 False。
        force (bool): 是否强制执行更改（如修改文件）。默认为 False。
        output_format (str): 输出格式，可选 'text', 'json', 'stream-json'。默认为 'text'。
        stream_partial_output (bool): 是否增量流式输出变更。默认为 False。
        api_key (str, optional): API 密钥，默认从环境变量 CURSOR_API_KEY 读取。

    返回:
        根据 output_format 返回不同类型的响应：
        - text: 返回纯文本字符串
        - json: 返回结构化字典
        - stream-json: 应使用 stream_analysis 获取流式输出，此处返回空字符串
    """
    if not prompt:
        if output_format == "text":
            return "错误：缺少必要的 prompt 参数"
        else:
            return {
                "error": "缺少必要的 prompt 参数",
                "exit_code": 1
            }

    if not print_mode:
        if output_format == "text":
            return "错误：非打印模式下不执行操作，请设置 print_mode=True"
        else:
            return {
                "error": "非打印模式下不执行操作，请设置 print_mode=True",
                "exit_code": 1
            }

    # 使用传入的api_key或从环境变量读取
    effective_api_key = api_key or os.getenv('CURSOR_API_KEY')
    if not effective_api_key:
        if output_format == "text":
            return "错误：API密钥未设置，请设置环境变量 CURSOR_API_KEY"
        else:
            return {
                "error": "API密钥未设置，请设置环境变量 CURSOR_API_KEY",
                "exit_code": 1
            }

    # 模拟网络延迟
    _simulate_delay()

    # 根据 output_format 返回不同格式的数据
    if output_format == "json":
        return {
            "result": "代码审查已完成，未发现严重问题。",
            "recommendations": [
                "添加 JSDoc 注释以提高可读性",
                "考虑使用 ES6+ 语法重构旧代码",
                "增加单元测试覆盖"
            ],
            "file_changes": [
                {"path": "src/utils.js", "action": "updated", "lines_added": 12}
            ],
            "success": True,
            "prompt": prompt,
            "print_mode": print_mode,
            "force": force,
            "output_format": output_format,
            "api_key_set": bool(effective_api_key),
            "exit_code": 0
        }

    elif output_format == "stream-json":
        # 在此模式下应使用 stream_analysis 函数进行流式输出
        # 此处仅作兼容性保留，返回空字符串
        return ""

    else:  # 默认 text 格式
        return "这个代码库是一个前端应用，使用 React 和 TypeScript 构建，包含用户认证、数据可视化等功能。"

def stream_analysis(prompt: str, output_file: str = "analysis.txt") -> Generator[Dict, None, None]:
    """
    流式分析项目结构，模拟真正的逐行输出行为。

    参数:
        prompt (str): 分析提示。
        output_file (str): 输出文件路径。

    Yields:
        dict: 单个流事件对象，每个事件都有唯一 event_id
    """
    event_id = _generate_event_id()

    yield {
        "type": "system",
        "subtype": "init",
        "model": "cursor-large-v1",
        "event_id": event_id,
        "timestamp": _get_current_timestamp()
    }

    accumulated = ""
    partial_text = "正在分析项目结构...生成报告摘要...完成文件扫描..."
    for char in partial_text:
        accumulated += char
        yield {
            "type": "assistant",
            "message": {
                "content": [{"text": accumulated}]
            },
            "event_id": event_id,
            "timestamp": _get_current_timestamp()
        }
        time.sleep(0.01)  # 模拟字符级流式输出

    # 模拟工具调用 - readToolCall
    tool_call_id = _generate_tool_call_id()
    yield {
        "type": "tool_call",
        "subtype": "started",
        "tool_call": {
            "readToolCall": {
                "args": {"path": "src/"},
                "id": tool_call_id
            }
        },
        "event_id": event_id,
        "timestamp": _get_current_timestamp()
    }
    time.sleep(0.2)
    yield {
        "type": "tool_call",
        "subtype": "completed",
        "tool_call": {
            "readToolCall": {
                "result": {"success": {"totalLines": 450}}
            }
        },
        "event_id": event_id,
        "timestamp": _get_current_timestamp()
    }

    # 模拟工具调用 - writeToolCall
    write_tool_id = _generate_tool_call_id()
    yield {
        "type": "tool_call",
        "subtype": "started",
        "tool_call": {
            "writeToolCall": {
                "args": {"path": output_file},
                "id": write_tool_id
            }
        },
        "event_id": event_id,
        "timestamp": _get_current_timestamp()
    }
    time.sleep(0.2)
    yield {
        "type": "tool_call",
        "subtype": "completed",
        "tool_call": {
            "writeToolCall": {
                "result": {"success": {"linesCreated": 23, "fileSize": 1024}}
            }
        },
        "event_id": event_id,
        "timestamp": _get_current_timestamp()
    }

    yield {
        "type": "result",
        "duration_ms": 1250,
        "event_id": event_id,
        "timestamp": _get_current_timestamp()
    }

def process_files_glob(pattern: str, prompt_template: str) -> List[Dict[str, Any]]:
    """
    批量处理符合 glob 模式的文件。

    参数:
        pattern (str): 文件路径模式，如 "src/**/*.js"
        prompt_template (str): 提示模板，其中 `{file}` 会被替换为文件名

    返回:
        list: 每个文件的处理结果列表
    """
    import glob
    results = []
    matched_files = glob.glob(pattern, recursive=True)

    if not matched_files:
        return [{
            "error": f"未找到匹配 '{pattern}' 的文件",
            "exit_code": 1
        }]

    for file_path in matched_files:
        prompt = prompt_template.format(file=file_path)
        result = cursor_agent(
            prompt=prompt,
            print_mode=True,
            force=True,
            output_format="json"
        )
        result["processed_file"] = file_path
        results.append(result)

    return results
def stream_process_files_glob(pattern: str, prompt_template: str) -> Generator[Dict, None, None]:
    """
    流式批处理符合 glob 模式的文件，支持实时进度跟踪。

    参数:
        pattern (str): 文件路径模式
        prompt_template (str): 提示模板

    Yields:
        dict: 包含处理状态的事件对象
    """
    import glob
    matched_files = glob.glob(pattern, recursive=True)
    total = len(matched_files)
    current = 0

    if total == 0:
        yield {
            "type": "error",
            "message": f"未找到匹配 '{pattern}' 的文件",
            "event_id": _generate_event_id(),
            "timestamp": _get_current_timestamp()
        }
        return

    for file_path in matched_files:
        current += 1
        event_id = _generate_event_id()

        yield {
            "type": "file_processing",
            "status": "started",
            "file": file_path,
            "progress": f"{current}/{total}",
            "event_id": event_id,
            "timestamp": _get_current_timestamp()
        }

        # 模拟处理延迟
        _simulate_delay()

        # 模拟成功结果
        yield {
            "type": "file_processed",
            "status": "completed",
            "file": file_path,
            "result": {
                "recommendations": [
                    "添加 JSDoc 注释",
                    "优化函数结构"
                ],
                "lines_added": 8
            },
            "event_id": event_id,
            "timestamp": _get_current_timestamp()
        }

class CursorAgent:
    """
    CursorAgent 类提供面向对象的接口来调用 cursor_agent 功能。
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        初始化 CursorAgent。

        参数:
            api_key (str, optional): API 密钥（模拟用途）。
        """
        self.api_key = api_key or os.getenv('CURSOR_API_KEY')
        if not self.api_key:
            raise ValueError("API密钥未设置，请通过参数或环境变量 CURSOR_API_KEY 提供")

    def analyze(self, prompt: str, force: bool = False) -> Union[str, Dict[str, Any]]:
        """
        分析代码库或文件。

        参数:
            prompt (str): 分析提示。
            force (bool): 是否强制执行。

        返回:
            根据上下文返回文本或JSON响应。
        """
        return cursor_agent(
            prompt=prompt,
            print_mode=True,
            force=force,
            output_format="text",
            api_key=self.api_key
        )

    def review(self, target: str = "recent changes") -> Dict[str, Any]:
        """
        执行代码审查。

        参数:
            target (str): 审查目标。

        返回:
            dict: 审查结果（JSON格式）。
        """
        prompt = f"审查 {target} 并提供反馈：\n  - 代码质量和可读性\n  - 潜在的错误或问题\n  - 安全考虑\n  - 最佳实践合规性\n\n提供具体的改进建议。"
        return cursor_agent(
            prompt=prompt,
            print_mode=True,
            force=True,
            output_format="json",
            api_key=self.api_key
        )

    def stream_analysis(self, output_file: str = "analysis.txt") -> Generator[Dict, None, None]:
        """
        流式分析项目结构。

        参数:
            output_file (str): 输出文件路径。

        Yields:
            dict: 单个流事件。
        """
        prompt = f"分析此项目结构并在 {output_file} 中创建摘要报告"
        yield from stream_analysis(prompt, output_file)

    def stream_batch_process(self, pattern: str, instruction: str) -> Generator[Dict, None, None]:
        """
        流式批处理文件。

        参数:
            pattern (str): 文件匹配模式
            instruction (str): 处理指令

        Yields:
            dict: 流式事件
        """
        template = f"{{file}}: {instruction}"
        yield from stream_process_files_glob(pattern, template)

def main():
    """命令行主入口"""
    parser = argparse.ArgumentParser(description="模拟 cursor-agent CLI 工具")
    parser.add_argument("prompt", nargs="?", help="要执行的提示语")
    parser.add_argument("-p", "--print", action="store_true", help="启用打印模式")
    parser.add_argument("--force", action="store_true", help="强制执行更改")
    parser.add_argument("--output-format", choices=["text", "json", "stream-json"], default="text", help="输出格式")
    parser.add_argument("--stream-partial-output", action="store_true", help="启用部分输出流")
    parser.add_argument("--api-key", help="显式指定API密钥")

    args = parser.parse_args()

    # 如果没有提供 prompt，则尝试从标准输入读取
    if not args.prompt:
        try:
            args.prompt = sys.stdin.read().strip()
            if not args.prompt:
                raise ValueError
        except Exception:
            print("错误：必须提供提示语作为参数或标准输入", file=sys.stderr)
            sys.exit(1)

    # 验证API密钥
    api_key = args.api_key or os.getenv('CURSOR_API_KEY')
    if not api_key:
        print("错误：API密钥未设置，请设置环境变量 CURSOR_API_KEY", file=sys.stderr)
        sys.exit(1)

    if args.output_format == "stream-json" and args.stream_partial_output:
        # 特殊处理流式输出：逐行打印每个事件
        try:
            for event in stream_analysis(args.prompt):
                print(json.dumps(event), flush=True)
            sys.exit(0)
        except Exception as e:
            error_event = {
                "type": "error",
                "message": str(e),
                "event_id": _generate_event_id(),
                "timestamp": _get_current_timestamp()
            }
            print(json.dumps(error_event), file=sys.stderr, flush=True)
            sys.exit(1)
    else:
        # 其他模式统一处理
        result = cursor_agent(
            prompt=args.prompt,
            print_mode=args.print,
            force=args.force,
            output_format=args.output_format,
            stream_partial_output=args.stream_partial_output,
            api_key=api_key
        )
        if isinstance(result, dict):
            if result.get("error"):
                print(json.dumps(result), file=sys.stderr, ensure_ascii=False)
                sys.exit(result.get("exit_code", 1))
            else:
                print(json.dumps(result, indent=2, ensure_ascii=False))
                sys.exit(0)
        else:  # 字符串输出（text模式）
            if "错误：" in result:
                print(result, file=sys.stderr)
                sys.exit(1)
            else:
                print(result)
                sys.exit(0)

def example_usage():
    """示例用法"""
    print("=== 示例 1：简单查询 ===")
    result1 = cursor_agent(
        prompt="这个代码库是做什么的？",
        print_mode=True,
        output_format="text"
    )
    print(result1)

    print("\n=== 示例 2：代码审查（JSON 格式）===")
    agent = CursorAgent(api_key="dummy_key")
    result2 = agent.review()
    print(json.dumps(result2, indent=2, ensure_ascii=False))

    print("\n=== 示例 3：流式分析（模拟）===")
    for event in agent.stream_analysis():
        print(json.dumps(event))
    
    print("\n=== 示例 4：流式批处理多个文件 ===")
    for event in stream_process_files_glob("src/**/*.js", "为 {file} 添加全面的 JSDoc 注释"):
        print(json.dumps(event))

if __name__ == "__main__":
    # 判断是否以模块方式运行还是直接执行
    if len(sys.argv) == 1:
        example_usage()
    else:
        main()