# Auto-Coder

一个基于 LangGraph 和 LangChain 的智能代码生成系统，通过多智能体协作实现从需求到代码的自动化开发流程。

## 🚀 功能特性

- **多智能体协作架构**：采用计划智能体、执行智能体、审查智能体等多角色协作模式
- **自适应工作流**：基于 LangGraph 的状态机工作流，支持动态规划和重新规划
- **智能需求分析**：自动解析需求文档（支持 DOCX、PDF、Markdown 格式）
- **代码生成与执行**：集成 Cursor Agent API，实现代码的自动生成和修改
- **代码审查机制**：自动审查生成的代码，检查是否符合需求并生成修改意见
- **版本管理**：自动追踪文件变更，支持历史版本对比
- **异步并发处理**：高效的异步文件处理，提升系统性能
- **上下文压缩**：智能压缩历史日志，控制 token 消耗

## 📋 系统架构

### 主工作流
```
Counter → Execute → Review → Counter (循环迭代)
```

### 执行工作流
```
Plan → Execute → Replan → Execute (自适应规划)
```

### 核心组件

- **计划节点（execute_plan_node）**：分析需求文档，生成执行计划
- **执行节点（execute_execute_node）**：执行计划中的任务，调用工具进行代码生成
- **重新规划节点（execute_replan_node）**：根据执行结果动态调整计划
- **审查节点（review_node）**：审查代码质量，检查是否符合需求
- **计数节点（counter_node）**：管理工作流迭代次数和项目状态

## 🛠️ 技术栈

- **LangGraph**：工作流编排和状态管理
- **LangChain**：LLM 应用框架
- **Qwen/DeepSeek**：大语言模型（通义千问、DeepSeek）
- **Cursor Agent**：代码生成和执行
- **Python 3.8+**：编程语言

## 📦 安装要求

### 系统要求

- Python 3.8 或更高版本
- 已安装 Cursor Agent CLI（或使用 MOCK 模式）
- 支持 bash 命令执行环境

### Python 依赖

```bash
pip install langchain langchain-openai langgraph
pip install pydantic typing-extensions
pip install python-docx PyPDF2
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

- `CURSOR_API_KEY`: Cursor Agent API 密钥
- `SIM_CURSOR_PATH`: 模拟 Cursor SDK 的路径（MOCK 模式使用）
- `MOCK`: 是否使用模拟模式（true/false）
- `CURSOR_PATH`: Cursor Agent CLI 路径
- `PROJECT_NAME`: 项目名称（必须与 todo 目录下的项目文件夹名称一致）
- `QWEN_API_KEY`: 通义千问 API 密钥
- `QWEN_API_BASE`: 通义千问 API 基础地址
- `DEEPSEEK_API_KEY`: DeepSeek API 密钥
- `DEEPSEEK_API_BASE`: DeepSeek API 基础地址
- `SUMMARY_MAX_LENGTH`: 总结内容的最大 token 长度
- `RECURSION_LIMIT`: 工作流递归限制次数

## 📖 使用方法

### 1. 准备需求文档

在 `todo/{PROJECT_NAME}/` 目录下放置需求文档：

```bash
mkdir -p todo/your-project-name
# 将需求文档（.md, .docx, .pdf）放入该目录
```

支持的文档格式：
- Markdown (.md)
- Word 文档 (.docx)
- PDF 文档 (.pdf)

### 2. 创建 .spanignore 文件

在项目根目录创建 `.spanignore` 文件，指定需要忽略的目录（每行一个）：

```
node_modules
__pycache__
.git
dist
```

### 3. 运行系统

```bash
python main.py
```

### 4. 交互流程

系统运行过程中会需要人工确认：

1. **计划确认**：系统生成执行计划后，检查 `todo/{PROJECT_NAME}/todo_list.md`，输入 `pass` 继续或 `reject` 重新生成
2. **文件转换警告**：如果存在无法解析的文件，查看警告文件后输入 `pass` 继续
3. **审核意见确认**：审核完成后，检查 `opinion/{PROJECT_NAME}.md`，输入 `pass` 结束或 `reject` 继续修改

## 📁 项目结构

```
auto-coder/
├── main.py                 # 主入口文件
├── config.json             # 配置文件（需要创建）
├── config.default.json     # 配置模板
├── constants.py            # 常量定义
├── custom_type.py          # 自定义类型定义
│
├── count_node.py          # 计数节点
├── count_utils.py          # 计数工具函数
│
├── execute_zgraph.py      # 执行工作流图
├── execute_plan_node.py    # 计划节点
├── execute_plan_utils.py   # 计划工具函数
├── execute_execute_node.py # 执行节点
├── execute_execute_tool.py # 执行工具
├── execute_replan_node.py  # 重新规划节点
├── execute_replan_utils.py # 重新规划工具函数
├── execute_custom_type.py  # 执行相关类型定义
│
├── review_node.py         # 审查节点
├── review_tool.py         # 审查工具
│
├── sim_sdk/               # 模拟 Cursor SDK
│   └── sim_sdk.py
│
├── todo/                  # 需求文档目录
│   └── {PROJECT_NAME}/
│       └── todo.md        # 需求文档
│
├── dist/                  # 生成的项目目录
│   └── {PROJECT_NAME}/
│
├── history/               # 历史版本目录
│   └── {PROJECT_NAME}/
│
├── opinion/               # 审核意见目录
│   └── {PROJECT_NAME}.md
│
├── experiment/            # 实验目录
└── .spanignore           # 忽略文件配置
```

## 🔧 核心功能详解

### 需求分析

系统会自动：
1. 转换 DOCX/PDF 文档为 Markdown
2. 分析所有需求文档，生成统一的需求描述（`todo.md`）
3. 生成详细的执行计划（`todo_list.md`）

### 代码生成

通过 Cursor Agent API 执行：
- 创建/修改代码文件
- 创建/删除目录
- 列出文件目录
- 删除文件

### 代码审查

审查智能体会：
1. 检查代码是否符合需求文档
2. 检查代码语法和逻辑错误
3. 生成审核意见文件
4. 判断是否需要继续修改

### 动态重新规划

系统会根据：
- 执行结果
- 项目当前状态
- 审核意见

动态调整后续执行计划。

## ⚠️ 注意事项

1. **API 密钥安全**：不要将包含真实 API 密钥的 `config.json` 提交到版本控制系统
2. **递归限制**：合理设置 `RECURSION_LIMIT`，避免无限循环或提前终止
3. **Token 消耗**：大量 LLM 调用会产生成本，注意监控使用量
4. **文件权限**：确保系统有足够的文件系统操作权限
5. **网络连接**：需要稳定的网络连接访问 LLM API 和 Cursor Agent
6. **Windows 环境**：在 Windows 上使用需要 WSL 或 Git Bash 支持 bash 命令

## 🐛 故障排除

### 问题：执行失败

- 检查 `config.json` 配置是否正确
- 确认 API 密钥有效
- 检查 Cursor Agent CLI 是否已正确安装

### 问题：无法解析文档

- 查看 `todo/{PROJECT_NAME}/warning.md` 了解无法解析的文件
- 手动将文件转换为 Markdown 格式

### 问题：结构化输出错误

- 系统会自动重试（最多 3 次）
- 如果持续失败，检查 LLM API 是否正常

### 问题：递归限制过早终止

- 增加 `RECURSION_LIMIT` 配置值
- 检查是否有无限循环逻辑

## 📝 开发说明

### 添加新工具

在 `execute_execute_tool.py` 中添加新的 `@tool` 装饰的函数。

### 修改工作流

编辑 `main.py` 或 `execute_zgraph.py` 中的 `_init_graph()` 函数。

### 自定义 Prompt

在各个节点的 `_init_agent()` 或 `_prompt` 变量中修改。

## 📄 许可证

本项目采用 MIT 许可证。详见 [LICENSE](LICENSE) 文件。

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📧 联系方式

如有问题或建议，请通过 Issue 联系。

---

**注意**：本系统是一个实验性项目，在生产环境中使用前请充分测试。

