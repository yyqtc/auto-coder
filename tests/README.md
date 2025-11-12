# Auto-Coder 测试套件

本目录包含 Auto-Coder 项目的完整测试用例。

## 📁 测试文件结构

```
tests/
├── __init__.py                    # 测试包初始化文件
├── conftest.py                    # Pytest 配置和共享 fixtures
├── test_constants.py              # 测试常量定义模块
├── test_custom_type.py            # 测试类型定义模块
├── test_count_node.py             # 测试计数节点模块
├── test_execute_plan_utils.py     # 测试文档转换工具模块
├── test_execute_replan_utils.py   # 测试重新规划工具模块
├── test_review_tool.py            # 测试审查工具模块
└── test_execute_execute_tool.py   # 测试执行工具模块
```

## 🚀 运行测试

### 安装测试依赖

确保已安装 pytest 和相关依赖：

```bash
pip install pytest pytest-cov pytest-asyncio
```

或者安装项目的开发依赖：

```bash
pip install -e ".[dev]"
```

### 运行所有测试

```bash
# 从项目根目录运行
pytest tests/

# 或使用详细输出
pytest tests/ -v

# 显示覆盖率
pytest tests/ --cov=. --cov-report=html
```

### 运行特定测试文件

```bash
# 运行单个测试文件
pytest tests/test_constants.py

# 运行特定测试类
pytest tests/test_constants.py::TestCodeExtensions

# 运行特定测试函数
pytest tests/test_constants.py::TestCodeExtensions::test_code_extensions_is_list
```

### 运行测试并查看覆盖率

```bash
pytest tests/ --cov=. --cov-report=term-missing
```

## 📋 测试覆盖范围

### 已测试的模块

1. **constants.py** - 常量定义
   - 代码扩展名列表
   - 错误消息常量

2. **custom_type.py** - 主工作流类型定义
   - ActionReview TypedDict
   - Action, Response, Act 模型

3. **execute_custom_type.py** - 执行工作流类型定义
   - PlanExecute TypedDict
   - Plan, Response, Act 模型

4. **count_node.py** - 计数节点
   - counter_node 函数
   - remove_readonly 函数

5. **execute_plan_utils.py** - 文档转换工具
   - _get_drive_letter 函数
   - convert_docx_to_markdown 函数
   - convert_pdf_to_markdown 函数
   - _execute_script_subprocess 函数
   - analyze_what_to_do 函数

6. **execute_replan_utils.py** - 重新规划工具
   - _get_drive_letter 函数
   - _execute_script_subprocess 函数
   - analyze_what_to_do 函数

7. **review_tool.py** - 审查工具
   - write_opinion_file 工具
   - read_opinion_file 工具
   - read_todo_content 工具
   - read_development_log 工具

8. **execute_execute_tool.py** - 执行工具
   - rm 工具
   - mkdir 工具
   - list_files 工具
   - search_todo_dir 工具
   - code_professional 工具
   - _execute_script_subprocess 函数

## 🧪 测试策略

### Mock 使用

测试中大量使用了 `unittest.mock` 来模拟：
- 文件系统操作
- 外部 API 调用
- 子进程执行
- 配置读取

### Fixtures

`conftest.py` 提供了以下共享 fixtures：
- `temp_dir`: 临时目录
- `sample_config`: 示例配置
- `temp_config_file`: 临时配置文件
- `sample_markdown_content`: 示例 Markdown 内容
- `sample_todo_list`: 示例待办列表
- `mock_file_structure`: 模拟文件结构

### 异步测试

对于异步函数（如 `counter_node`），使用 `pytest.mark.asyncio` 装饰器。

## ⚠️ 注意事项

1. **配置文件依赖**: 某些测试需要 `config.json` 文件，测试中使用 mock 来避免依赖实际配置。

2. **文件系统操作**: 测试使用临时目录来避免污染实际文件系统。

3. **外部依赖**: 测试不依赖实际的 Cursor Agent 或 LLM API，所有外部调用都被 mock。

4. **平台差异**: 某些测试针对 Windows 和 Linux 平台有不同的行为，使用 mock 来模拟不同平台。

## 🔧 添加新测试

添加新测试时，请遵循以下规范：

1. 测试文件命名：`test_<module_name>.py`
2. 测试类命名：`Test<ClassName>`
3. 测试函数命名：`test_<function_name>`
4. 使用描述性的测试名称
5. 为每个测试添加文档字符串说明测试目的
6. 使用 fixtures 来共享测试数据
7. Mock 外部依赖

示例：

```python
class TestNewFeature:
    """测试新功能"""

    def test_new_feature_basic(self):
        """测试新功能的基本用例"""
        # 测试代码
        pass
```

## 📊 测试报告

运行测试后，可以生成 HTML 覆盖率报告：

```bash
pytest tests/ --cov=. --cov-report=html
```

报告将生成在 `htmlcov/index.html`。

## 🤝 贡献

添加新功能时，请同时添加相应的测试用例。确保：
- 新测试通过
- 测试覆盖率不降低
- 遵循现有的测试风格和规范

