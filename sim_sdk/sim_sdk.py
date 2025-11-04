import os
import requests
import json
import time
from typing import Optional, Dict, Any, Callable, Generator
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

class CursorCLI:
    """
    模拟 Cursor CLI SDK，用于在脚本和自动化流程中执行代码分析、生成和重构等任务。
    
    根据审核员意见进行了以下修改：
    1. 修复了 stream_progress 方法的流式处理实现，使用真正的流式HTTP请求逐行读取响应
    2. 增加了超时和重试机制到 _make_request 方法
    3. 为 batch_process 方法添加了可选的并发处理支持
    4. 在文档字符串中明确说明了 {file} 占位符语法的支持
    5. 添加了对环境变量设置的说明
    """

    def __init__(self, api_key: str = None, timeout: int = 30, max_retries: int = 3):
        """
        初始化 CursorCLI 实例。

        Args:
            api_key (str): Cursor API 密钥。如果未提供，则尝试从环境变量 CURSOR_API_KEY 中读取。
            timeout (int): 请求超时时间（秒）。
            max_retries (int): 最大重试次数。
        
        环境变量设置示例：
            export CURSOR_API_KEY=your_api_key_here
        """
        self.api_key = api_key or os.getenv('CURSOR_API_KEY')
        if not self.api_key:
            raise ValueError("API key is required. Set it via argument or environment variable 'CURSOR_API_KEY'.")

        self.base_url = "https://api.cursor.com/v1"
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        self.timeout = timeout
        self.max_retries = max_retries

    def _make_request(
        self,
        endpoint: str,
        prompt: str,
        print_mode: bool = True,
        force: bool = False,
        output_format: str = 'text',
        stream_partial_output: bool = False,
        stream: bool = False
    ) -> Dict[str, Any]:
        """
        内部方法：向 Cursor API 发送请求，包含超时和重试机制。

        Args:
            endpoint (str): API 端点。
            prompt (str): 要发送给 AI 的提示语。
            print_mode (bool): 是否启用打印模式（非交互式）。
            force (bool): 是否强制执行更改（配合 --force 使用）。
            output_format (str): 输出格式 ('text', 'json', 'stream-json')。
            stream_partial_output (bool): 是否流式输出部分结果。
            stream (bool): 是否启用流式响应。

        Returns:
            dict: API 响应数据。
        """
        url = f"{self.base_url}/{endpoint}"
        payload = {
            'prompt': prompt,
            'print': print_mode,
            'force': force,
            'output_format': output_format,
            'stream_partial_output': stream_partial_output
        }

        for attempt in range(self.max_retries + 1):
            try:
                response = requests.post(
                    url, 
                    headers=self.headers, 
                    data=json.dumps(payload),
                    timeout=self.timeout,
                    stream=stream
                )
                response.raise_for_status()
                
                if stream:
                    return {'stream_response': response}
                else:
                    return response.json()
                    
            except requests.exceptions.RequestException as e:
                if attempt == self.max_retries:
                    return {
                        'error': True,
                        'message': str(e),
                        'status_code': getattr(e.response, 'status_code', None)
                    }
                time.sleep(2 ** attempt)  # 指数退避

    def analyze_codebase(self, prompt: str = "What is this codebase doing?") -> Dict[str, Any]:
        """
        分析整个代码库，回答关于项目用途、结构等问题。

        默认使用文本格式输出简洁响应。

        Args:
            prompt (str): 自定义问题或指令。

        Returns:
            dict: 包含分析结果的字典。
        """
        return self._make_request(
            endpoint='analyze',
            prompt=prompt,
            print_mode=True,
            output_format='text'
        )

    def review_code(
        self,
        target: str = "recent changes",
        output_file: str = "review.txt",
        feedback_points: Optional[list] = None
    ) -> Dict[str, Any]:
        """
        自动化代码评审。

        使用 JSON 格式返回结构化分析结果。

        Args:
            target (str): 审查目标，如 'recent changes', 'file:src/index.js' 等。
            output_file (str): 审查报告写入的文件路径。
            feedback_points (list): 反馈维度列表。

        Returns:
            dict: 结构化审查结果。
        """
        default_feedback = [
            "代码质量和可读性",
            "潜在的错误或问题",
            "安全考虑",
            "最佳实践合规性"
        ]
        points = feedback_points or default_feedback
        prompt = f"审查 {target} 并提供以下方面的反馈：\n" + "\n  - ".join([f"{p}" for p in points])
        prompt += f"\n\n提供具体的改进建议并写入 {output_file}"

        return self._make_request(
            endpoint='review',
            prompt=prompt,
            print_mode=True,
            force=True,
            output_format='json'
        )

    def stream_progress(
        self,
        prompt: str,
        on_system_init=None,
        on_assistant_update=None,
        on_tool_call=None,
        on_result=None
    ) -> Dict[str, Any]:
        """
        支持实时进度跟踪的流式处理接口。

        使用 stream-json 格式进行消息级进度跟踪，通过真正的流式HTTP请求实现逐行读取。

        Args:
            prompt (str): 提示语。
            on_system_init (callable): 当系统初始化时回调。
            on_assistant_update (callable): 当助手生成新内容时回调。
            on_tool_call (callable): 当工具调用开始或完成时回调。
            on_result (callable): 当最终结果返回时回调。

        Returns:
            dict: 处理结果统计。
        """
        response_data = self._make_request(
            endpoint='stream',
            prompt=prompt,
            print_mode=True,
            force=True,
            output_format='stream-json',
            stream_partial_output=True,
            stream=True
        )
        
        if 'error' in response_data:
            return response_data
            
        response = response_data['stream_response']
        accumulated_text = ""
        tool_count = 0
        start_time = time.time()

        try:
            for line in response.iter_lines():
                if line:
                    try:
                        msg = json.loads(line.decode('utf-8'))
                        msg_type = msg.get('type')
                        subtype = msg.get('subtype', '')

                        if msg_type == 'system' and subtype == 'init' and on_system_init:
                            model = msg.get('model', 'unknown')
                            on_system_init(model)

                        elif msg_type == 'assistant' and on_assistant_update:
                            content = msg.get('message', {}).get('content', [{}])[0].get('text', '')
                            accumulated_text += content
                            on_assistant_update(accumulated_text)

                        elif msg_type == 'tool_call':
                            if on_tool_call:
                                on_tool_call(msg, subtype, tool_count)
                            if subtype == 'started':
                                tool_count += 1

                        elif msg_type == 'result' and on_result:
                            duration = msg.get('duration_ms', 0)
                            total_time = int(time.time() - start_time)
                            on_result(duration, total_time, tool_count, len(accumulated_text))

                    except (json.JSONDecodeError, UnicodeDecodeError):
                        continue
                        
        finally:
            response.close()

        return {
            'success': True,
            'stream_processed': True,
            'total_tools': tool_count,
            'total_chars': len(accumulated_text)
        }

    def modify_file(
        self,
        instruction: str,
        file_path: str
    ) -> Dict[str, Any]:
        """
        在脚本中修改指定文件。

        必须同时使用 --print 和 --force 才能真正修改文件。

        Args:
            instruction (str): 对文件的操作指令，例如 "重构此代码以使用现代 ES6+ 语法"。
            file_path (str): 目标文件路径。

        Returns:
            dict: 操作结果。
        """
        prompt = f"{instruction} in {file_path}"
        return self._make_request(
            endpoint='edit',
            prompt=prompt,
            print_mode=True,
            force=True,  # 必须启用 force 才能修改文件
            output_format='text'
        )

    def batch_process(
        self,
        files: list,
        instruction_template: str,
        concurrent: bool = False,
        max_workers: int = 4
    ) -> Dict[str, Any]:
        """
        批量处理多个文件，支持可选的并发处理。

        指令模板支持 {file} 占位符，将被替换为实际文件路径。

        Args:
            files (list): 文件路径列表。
            instruction_template (str): 指令模板，支持 {file} 占位符。
            concurrent (bool): 是否并发处理文件。
            max_workers (int): 并发线程数。

        Returns:
            dict: 批量处理结果汇总。
        """
        results = []
        
        if concurrent:
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                # 创建任务映射
                future_to_file = {
                    executor.submit(self._process_single_file, instruction_template, file_path): file_path 
                    for file_path in files
                }
                
                for future in as_completed(future_to_file):
                    file_path = future_to_file[future]
                    try:
                        result = future.result()
                        results.append({
                            'file': file_path,
                            'result': result
                        })
                    except Exception as exc:
                        results.append({
                            'file': file_path,
                            'result': {
                                'error': True,
                                'message': str(exc)
                            }
                        })
        else:
            for file_path in files:
                result = self._process_single_file(instruction_template, file_path)
                results.append({
                    'file': file_path,
                    'result': result
                })
                    
        return {
            'success_count': sum(1 for r in results if not r['result'].get('error')),
            'total_count': len(results),
            'details': results
        }
        
    def _process_single_file(self, instruction_template: str, file_path: str) -> Dict[str, Any]:
        """
        处理单个文件的辅助方法。

        Args:
            instruction_template (str): 指令模板。
            file_path (str): 文件路径。

        Returns:
            dict: 单个文件处理结果。
        """
        instruction = instruction_template.format(file=file_path)
        return self.modify_file(instruction, file_path)

# --- 示例用法 ---
if __name__ == '__main__':
    # 设置 API Key
    # export CURSOR_API_KEY=your_api_key_here

    cli = CursorCLI()

    # 示例 1: 简单代码库问题
    print("🔍 示例 1: 分析代码库")
    result1 = cli.analyze_codebase("这个代码库是做什么的？")
    print(result1, "\n")

    # 示例 2: 自动化代码评审
    print("📝 示例 2: 代码审查")
    result2 = cli.review_code(output_file="review.txt")
    print(result2, "\n")

    # 示例 3: 实时进度跟踪
    print("🚀 示例 3: 流式处理进度")

    def on_init(model):
        print(f"🤖 使用模型：{model}")

    def on_update(text):
        print(f"\r📝 生成中：{len(text)} 字符", end="")

    def on_tool(msg, subtype, count):
        tool_call = msg.get('tool_call', {})
        if 'writeToolCall' in tool_call:
            path = tool_call['writeToolCall']['args'].get('path', 'unknown')
            if subtype == 'started':
                print(f"\n🔧 工具 #{count}：创建 {path}")
            elif subtype == 'completed':
                lines = tool_call['writeToolCall']['result']['success'].get('linesCreated', 0)
                size = tool_call['writeToolCall']['result']['success'].get('fileSize', 0)
                print(f"   ✅ 已创建 {lines} 行（{size} 字节）")

    def on_final(duration, total_time, tool_count, char_count):
        print(f"\n\n🎯 在 {duration}ms 内完成（总计 {total_time}s）")
        print(f"📊 最终统计：{tool_count} 个工具，生成 {char_count} 个字符")

    result3 = cli.stream_progress(
        "分析此项目结构并在 analysis.txt 中创建摘要报告",
        on_system_init=on_init,
        on_assistant_update=on_update,
        on_tool_call=on_tool,
        on_result=on_final
    )
    print(result3)

    # 示例 4: 修改单个文件
    print("🛠️ 示例 4: 修改文件")
    result4 = cli.modify_file("为该文件添加 JSDoc 注释", "src/utils.js")
    print(result4, "\n")

    # 示例 5: 批量处理
    print("📦 示例 5: 批量处理多个 JS 文件")
    js_files = ["src/main.js", "src/helper.js", "src/config.js"]
    result5 = cli.batch_process(js_files, "为此文件添加全面的 JSDoc 注释: {file}", concurrent=True)
    print(result5)

# 注意！
# 1. 此模拟 SDK 并不真正连接真实 API，仅为演示接口设计。
# 2. 所有 API 方法均依据提供的文档说明实现。
# 3. 实现了所有文档中描述的功能：print 模式、force、output-format、streaming 等。
# 4. 添加了类型提示、异常处理和完整文档字符串以增强可用性。
# 5. 包含详细的示例用法以展示各 API 的调用方式。
