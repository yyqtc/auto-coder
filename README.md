# Auto-Coder

一个基于 LangGraph 和 LangChain 的智能代码生成系统，通过多智能体协作实现从需求到代码的自动化开发流程。

## 🚀 功能特性

- **多智能体协作架构**：采用计划智能体、执行智能体、审查智能体等多角色协作模式
- **自适应工作流**：基于 LangGraph 的状态机工作流，支持动态规划和重新规划
- **智能需求分析**：自动解析需求文档（支持 DOCX、PDF、Markdown 格式），并转换为统一的 Markdown 格式
- **代码生成与执行**：集成 Cursor Agent API，实现代码的自动生成和修改
- **代码审查机制**：自动审查生成的代码，检查是否符合需求并生成修改意见
- **上下文压缩**：智能压缩历史日志和需求文档，控制 token 消耗
- **结构化输出**：使用 Pydantic 模型确保 LLM 输出的结构化格式
- **错误重试机制**：自动重试失败的操作，提高系统稳定性

## 📋 系统架构

### 主工作流
```
Counter → Execute → Review → Counter (循环迭代)
```

主工作流通过 `main.py` 中的 `StateGraph` 实现，包含三个核心节点：
- **counter**：计数节点，管理开发轮次和项目状态备份
- **execute_graph**：执行子图，负责实际的代码开发工作
- **review**：审查节点，检查代码质量并生成审核意见

### 执行工作流
```
Plan → Execute → Replan → Execute (自适应规划)
```

执行工作流通过 `execute_zgraph.py` 实现，包含三个核心节点：
- **execute_plan**：计划节点，分析需求并生成执行计划
- **execute_execute**：执行节点，执行计划中的任务
- **execute_replan**：重新规划节点，根据执行结果动态调整计划

### 核心组件

- **计划节点（execute_plan_node）**：分析需求文档，转换 DOCX/PDF 为 Markdown，生成执行计划（`todo_list.md`）
- **执行节点（execute_execute_node）**：执行计划中的任务，调用工具进行代码生成、文件操作等
- **重新规划节点（execute_replan_node）**：根据执行结果和项目状态动态调整计划
- **审查节点（review_node）**：审查代码质量，检查是否符合需求并生成审核意见
- **计数节点（counter_node）**：管理工作流迭代次数，备份项目状态，处理用户交互确认

## 🛠️ 技术栈

- **LangGraph**：工作流编排和状态管理
- **LangChain**：LLM 应用框架，提供 Agent 和工具调用能力
- **LangChain OpenAI**：兼容 OpenAI API 格式的 LLM 调用
- **Qwen/DeepSeek**：大语言模型（通义千问 qwen-max/qwen-plus、DeepSeek deepseek-chat）
- **Cursor Agent**：代码生成和执行（支持真实 CLI 和 MOCK 模式）
- **Pydantic**：数据验证和结构化输出
- **Python 3.8+**：编程语言
- **python-docx/PyPDF2**：文档格式转换

## 📦 安装要求

### 系统要求

- Python 3.8 或更高版本
- 已安装 Cursor Agent CLI（或使用 MOCK 模式）
- 支持 bash 命令执行环境

### Python 依赖

安装所有依赖：

```bash
pip install -r requirements.txt
```

或手动安装：

```bash
pip install langchain>=0.1.0 langchain-openai>=0.0.5 langgraph>=0.0.20
pip install pydantic>=2.0.0 typing-extensions>=4.8.0
pip install python-docx>=1.1.0 PyPDF2>=3.0.0
```

### 配置 Cursor Agent

如果使用真实的 Cursor Agent，需要安装并配置：

```bash
# 安装 Cursor Agent CLI
# 具体安装方法请参考 Cursor 官方文档

# 或使用 MOCK 模式（开发测试）
# 设置 MOCK=true 并使用 sim_sdk
```

## ⚙️ 配置说明

### 1. 复制配置文件

```bash
cp config.default.json config.json
```

### 2. 编辑 config.json

```json
{
    "CURSOR_API_KEY": "your-cursor-api-key",
    "SIM_CURSOR_PATH": "/path-to-sim_sdk.py",
    "MOCK": false,
    "CURSOR_PATH": "/root/.local/bin/cursor-agent",
    "PROJECT_NAME": "your-project-name",
    "QWEN_API_KEY": "your-qwen-api-key",
    "QWEN_API_BASE": "https://dashscope.aliyuncs.com/compatible-mode/v1",
    "DEEPSEEK_API_KEY": "your-deepseek-api-key",
    "DEEPSEEK_API_BASE": "https://api.deepseek.com",
    "SUMMARY_MAX_LENGTH": 2000,
    "RECURSION_LIMIT": 100
}
```

### 配置项说明

- `CURSOR_API_KEY`: Cursor Agent API 密钥（必需）
- `SIM_CURSOR_PATH`: 模拟 Cursor SDK 的路径（MOCK 模式使用，如 `./sim_sdk/sim_sdk.py`）
- `MOCK`: 是否使用模拟模式（`true`/`false`，默认 `false`）
- `CURSOR_PATH`: Cursor Agent CLI 路径（非 MOCK 模式使用，如 `/root/.local/bin/cursor-agent`）
- `PROJECT_NAME`: 项目名称（必需，必须与需求文档目录下的项目文件夹名称一致）
- `QWEN_API_KEY`: 通义千问 API 密钥（必需）
- `QWEN_API_BASE`: 通义千问 API 基础地址（默认：`https://dashscope.aliyuncs.com/compatible-mode/v1`）
- `DEEPSEEK_API_KEY`: DeepSeek API 密钥（必需）
- `DEEPSEEK_API_BASE`: DeepSeek API 基础地址（默认：`https://api.deepseek.com`）
- `SUMMARY_MAX_LENGTH`: 总结内容的最大 token 长度（默认：2000，用于压缩上下文）
- `RECURSION_LIMIT`: 工作流递归限制次数（默认：100，防止无限循环）

## 📖 使用方法

### 1. 准备需求文档

在需求文档目录下创建项目文件夹并放置需求文档：

```bash
# 创建项目目录（PROJECT_NAME 需与 config.json 中的配置一致）
mkdir -p <需求文档目录>/<PROJECT_NAME>
# 将需求文档（.md, .docx, .pdf）放入该目录
```

支持的文档格式：
- Markdown (.md)：直接读取
- Word 文档 (.docx)：自动转换为 Markdown，支持图片提取
- PDF 文档 (.pdf)：自动提取文本并转换为 Markdown

系统会自动处理文档转换，DOCX 文件会提取图片到 `img/` 子目录，PDF 文件会提取所有页面的文本内容。

### 2. 创建 .spanignore 文件

在项目根目录创建 `.spanignore` 文件，指定在需求文档分析时需要忽略的目录（每行一个）：

```
node_modules
__pycache__
.git
```

该文件用于在 `execute_plan_node` 中过滤不需要处理的目录。

### 3. 运行系统

```bash
python main.py
```

或指定初始计数：

```bash
python main.py --count 0
```

### 4. 交互流程

系统运行过程中会需要人工确认：

1. **todo.md 确认**：如果 `todo.md` 已存在，系统会询问是否删除（输入 `y` 删除，`n` 保留）
2. **todo_list.md 确认**：如果 `todo_list.md` 已存在，系统会询问是否删除（第一轮开发时）
3. **计划确认**：系统生成执行计划后，检查执行计划文件，输入 `pass` 继续或 `reject` 重新生成
4. **文件转换警告**：如果存在无法解析的文件，系统会生成警告文件，查看后输入 `pass` 继续
5. **审核意见确认**：审核完成后，检查审核意见文件，输入 `pass` 结束或 `reject` 继续修改

## 📁 项目结构

```
auto-coder/
├── main.py                    # 主入口文件，定义主工作流
├── config.default.json        # 配置模板
├── constants.py               # 常量定义（代码扩展名、错误消息等）
├── custom_type.py             # 主工作流类型定义（ActionReview, Action, Response, Act）
│
├── count_node.py              # 计数节点，管理开发轮次和状态备份
│
├── execute_zgraph.py          # 执行工作流图，定义执行子图
├── execute_plan_node.py       # 计划节点，分析需求并生成执行计划
├── execute_plan_utils.py       # 计划工具函数（文档转换、需求分析）
├── execute_execute_node.py    # 执行节点，执行计划任务
├── execute_execute_tool.py    # 执行工具（代码专家、文件操作等）
├── execute_replan_node.py     # 重新规划节点，动态调整计划
├── execute_replan_utils.py    # 重新规划工具函数（项目状态分析）
├── execute_custom_type.py     # 执行工作流类型定义（PlanExecute, Plan, Response, Act）
│
├── review_node.py             # 审查节点，审查代码质量
├── review_tool.py             # 审查工具（读取/写入审核意见、读取需求文档等）
│
├── sim_sdk/                   # 模拟 Cursor SDK（MOCK 模式使用）
│   └── sim_sdk.py
│
├── requirements.txt           # Python 依赖列表
├── setup.py                   # 项目安装配置
├── pyproject.toml             # 项目元数据配置
└── .spanignore                # 需求文档分析时的忽略文件配置
```

## 🔧 核心功能详解

### 需求分析（execute_plan_node）

系统会自动：
1. **文档转换**：将 DOCX/PDF 文档转换为 Markdown 格式
   - DOCX：提取文本、表格和图片（图片保存到 `img/` 子目录）
   - PDF：提取所有页面的文本内容
2. **需求整合**：调用 Cursor Agent 分析所有需求文档，生成统一的需求描述（`todo.md`）
3. **计划生成**：使用 Qwen-max 模型生成详细的执行计划（`todo_list.md`）
4. **计划确认**：支持用户交互确认，可多次改进计划

### 代码执行（execute_execute_node）

通过 LangChain Agent 调用以下工具：
- **code_professional**：代码专家，调用 Cursor Agent 进行代码分析和编写
- **mkdir**：创建目录
- **rm**：删除文件或目录
- **list_files**：列出指定目录下的文件
- **search_todo_dir**：在需求文档目录中搜索并读取文件

### 代码审查（review_node）

审查智能体会：
1. 读取需求文档和开发日志
2. 检查代码是否符合需求文档的所有功能点
3. 检查代码是否修复了之前的审核意见
4. 生成审核意见文件（`opinion/{PROJECT_NAME}.md`）
5. 判断是否需要继续修改（返回 `count` 继续或 `response` 结束）

### 动态重新规划（execute_replan_node）

系统会根据：
- **执行结果**：已完成的步骤和响应
- **项目当前状态**：调用 Cursor Agent 分析项目代码实际状况
- **审核意见**：结合审核员意见调整计划
- **需求文档**：确保计划符合原始需求

动态调整后续执行计划，支持上下文压缩以控制 token 消耗。

### 状态管理（counter_node）

计数节点负责：
1. 管理开发轮次（`count`）
2. 备份项目状态（从 `dist/` 复制到 `history/`）
3. 处理用户交互确认（审核意见确认）
4. 判断工作流是否结束（根据 `response` 字段）

## ⚠️ 注意事项

1. **API 密钥安全**：`config.json` 已配置在 `.gitignore` 中，不要将包含真实 API 密钥的配置文件提交到版本控制系统
2. **递归限制**：合理设置 `RECURSION_LIMIT`，避免无限循环或提前终止。默认值为 100，可根据项目复杂度调整
3. **Token 消耗**：大量 LLM 调用会产生成本，注意监控使用量。系统已实现上下文压缩功能（`SUMMARY_MAX_LENGTH`）来减少 token 消耗
4. **文件权限**：确保系统有足够的文件系统操作权限，特别是对项目目录的读写权限
5. **网络连接**：需要稳定的网络连接访问 LLM API（Qwen、DeepSeek）和 Cursor Agent
6. **Windows 环境**：在 Windows 上使用需要 WSL 或 Git Bash 支持 bash 命令，因为工具执行使用 `subprocess.run(["bash", "-c", ...])`
7. **MOCK 模式**：开发测试时可以使用 MOCK 模式，设置 `MOCK=true` 并使用 `sim_sdk/sim_sdk.py`
8. **结构化输出**：系统使用 Pydantic 模型确保 LLM 输出格式正确，失败时会自动重试（最多 3 次）

## 🐛 故障排除

### 问题：执行失败

- 检查 `config.json` 配置是否正确，特别是 API 密钥和路径配置
- 确认 API 密钥有效且有足够的配额
- 检查 Cursor Agent CLI 是否已正确安装（非 MOCK 模式）
- 检查 `SIM_CURSOR_PATH` 路径是否正确（MOCK 模式）
- 查看日志输出了解具体错误信息

### 问题：无法解析文档

- 查看警告文件（`warning.md` 或 `warning_{n}.md`）了解无法解析的文件
- 手动将文件转换为 Markdown 格式并放入需求文档目录
- 确保文件编码为 UTF-8

### 问题：结构化输出错误

- 系统会自动重试（最多 3 次）
- 如果持续失败，检查 LLM API 是否正常，网络连接是否稳定
- 检查 API 密钥是否有效
- 查看日志中的错误信息

### 问题：递归限制过早终止

- 增加 `RECURSION_LIMIT` 配置值
- 检查是否有无限循环逻辑
- 查看执行日志了解工作流执行情况

### 问题：bash 命令执行失败（Windows）

- 确保已安装 WSL 或 Git Bash
- 检查系统 PATH 中是否包含 bash
- 在 Windows 上可能需要使用 Git Bash 终端运行

### 问题：文件路径错误

- 确保 `PROJECT_NAME` 配置与需求文档目录名称一致
- 检查相对路径是否正确
- 确保项目目录结构正确创建

## 📝 开发说明

### 添加新工具

在 `execute_execute_tool.py` 或 `review_tool.py` 中添加新的 `tool` 装饰的函数，并更新 `tools` 列表。

示例：
```python
tool
def my_new_tool(param: str) -> str:
    """工具描述"""
    # 实现逻辑
    return "执行结果"

tools = [..., my_new_tool]  # 添加到工具列表
```

### 修改工作流

编辑 `main.py` 或 `execute_zgraph.py` 中的 `_init_graph()` 函数，修改节点和边的定义。

### 自定义 Prompt

在各个节点的 Agent 初始化函数中修改 Prompt：
- `execute_plan_node.py`：`plan_prompt` 和 `improve_opinion_prompt`
- `execute_execute_node.py`：`_prompt`（在 `_init_agent()` 中）
- `execute_replan_node.py`：`summary_prompt` 和 `_prompt`
- `review_node.py`：`_prompt`（在 `init_agent()` 中）

### 修改类型定义

- 主工作流类型：`custom_type.py`
- 执行工作流类型：`execute_custom_type.py`
- 常量定义：`constants.py`

### 添加新的文档格式支持

在 `execute_plan_utils.py` 中添加新的转换函数，并在 `check_and_convert_file()` 中调用。

## 📄 许可证

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📧 联系方式

如有问题或建议，请通过 Issue 联系。

---

**注意**：本系统是一个实验性项目，在生产环境中使用前请充分测试。

