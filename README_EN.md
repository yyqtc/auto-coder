# Auto-Coder

An intelligent code generation system based on LangGraph and LangChain that automates the development process from requirements to code through multi-agent collaboration.

## 🚀 Features

- **Multi-Agent Collaboration Architecture**: Adopts a multi-role collaboration model including planning agents, execution agents, and review agents
- **Adaptive Workflow**: State machine workflow based on LangGraph, supporting dynamic planning and replanning
- **Intelligent Requirements Analysis**: Automatically parses requirement documents (supports DOCX, PDF, Markdown formats) and converts them to unified Markdown format
- **Code Generation and Execution**: Integrates Cursor Agent API for automatic code generation and modification
- **Code Review Mechanism**: Automatically reviews generated code, checks compliance with requirements, and generates modification suggestions
- **Context Compression**: Intelligently compresses history logs and requirement documents to control token consumption
- **Structured Output**: Uses Pydantic models to ensure structured LLM output format
- **Error Retry Mechanism**: Automatically retries failed operations to improve system stability

## 📋 System Architecture

### Main Workflow
```
Counter → Execute → Review → Counter (iterative loop)
```

The main workflow is implemented through `StateGraph` in `main.py`, containing three core nodes:
- **counter**: Count node that manages development rounds and project state backup
- **execute_graph**: Execution subgraph responsible for actual code development work
- **review**: Review node that checks code quality and generates review opinions

### Execution Workflow
```
Plan → Execute → Replan → Execute (adaptive planning)
```

The execution workflow is implemented through `execute_zgraph.py`, containing three core nodes:
- **execute_plan**: Planning node that analyzes requirements and generates execution plans
- **execute_execute**: Execution node that executes tasks in the plan
- **execute_replan**: Replanning node that dynamically adjusts plans based on execution results

### Core Components

- **Planning Node (execute_plan_node)**: Analyzes requirement documents, converts DOCX/PDF to Markdown, generates execution plans (`todo_list.md`)
- **Execution Node (execute_execute_node)**: Executes tasks in the plan, calls tools for code generation, file operations, etc.
- **Replanning Node (execute_replan_node)**: Dynamically adjusts plans based on execution results and project status
- **Review Node (review_node)**: Reviews code quality, checks compliance with requirements, and generates review opinions
- **Counter Node (counter_node)**: Manages workflow iteration count, backs up project state, handles user interaction confirmations

## 🛠️ Tech Stack

- **LangGraph**: Workflow orchestration and state management
- **LangChain**: LLM application framework providing Agent and tool calling capabilities
- **LangChain OpenAI**: LLM calls compatible with OpenAI API format
- **Qwen/DeepSeek**: Large language models (Qwen qwen-max/qwen-plus, DeepSeek deepseek-chat)
- **Cursor Agent**: Code generation and execution (supports real CLI and MOCK mode)
- **Pydantic**: Data validation and structured output
- **Python 3.8+**: Programming language
- **python-docx/PyPDF2**: Document format conversion

## 📦 Installation Requirements

### System Requirements

- Python 3.8 or higher
- Cursor Agent CLI installed (or use MOCK mode)
- Bash command execution environment support

### Python Dependencies

Install all dependencies:

```bash
pip install -r requirements.txt
```

Or install manually:

```bash
pip install langchain>=0.1.0 langchain-openai>=0.0.5 langgraph>=0.0.20
pip install pydantic>=2.0.0 typing-extensions>=4.8.0
pip install python-docx>=1.1.0 PyPDF2>=3.0.0
```

### Configure Cursor Agent

If using the real Cursor Agent, you need to install and configure it:

```bash
# Install Cursor Agent CLI
# Please refer to Cursor official documentation for specific installation methods

# Or use MOCK mode (for development and testing)
# Set MOCK=true and use sim_sdk
```

## ⚙️ Configuration

### 1. Copy Configuration File

```bash
cp config.default.json config.json
```

### 2. Edit config.json

```json
{
    "CURSOR_API_KEY": "your-cursor-api-key",
    "SIM_CURSOR_PATH": "/path-to-sim_sdk.py",
    "MOCK": false,
    "CURSOR_PATH": "/root/.local/bin/cursor-agent",
    "EXECUTE_PATH": "execute-agent.bat",
    "PROJECT_NAME": "your-project-name",
    "QWEN_API_KEY": "your-qwen-api-key",
    "QWEN_API_BASE": "https://dashscope.aliyuncs.com/compatible-mode/v1",
    "DEEPSEEK_API_KEY": "your-deepseek-api-key",
    "DEEPSEEK_API_BASE": "https://api.deepseek.com",
    "SUMMARY_MAX_LENGTH": 2000,
    "SUMMARY_THRESHOLD": 6000,
    "RECURSION_LIMIT": 100
}
```

### Configuration Items

- `CURSOR_API_KEY`: Cursor Agent API key (required)
- `SIM_CURSOR_PATH`: Path to simulated Cursor SDK (used in MOCK mode, e.g., `./sim_sdk/sim_sdk.py`)
- `MOCK`: Whether to use mock mode (`true`/`false`, default `false`)
- `CURSOR_PATH`: Cursor Agent CLI path (used in non-MOCK mode, e.g., `/root/.local/bin/cursor-agent`)
- `EXECUTE_PATH`: Execution path (e.g., `execute-agent.bat`)
- `PROJECT_NAME`: Project name (required, must match the project folder name under the requirement document directory)
- `QWEN_API_KEY`: Qwen API key (required)
- `QWEN_API_BASE`: Qwen API base URL (default: `https://dashscope.aliyuncs.com/compatible-mode/v1`)
- `DEEPSEEK_API_KEY`: DeepSeek API key (required)
- `DEEPSEEK_API_BASE`: DeepSeek API base URL (default: `https://api.deepseek.com`)
- `SUMMARY_MAX_LENGTH`: Maximum token length for summary content (default: 2000, used for context compression)
- `SUMMARY_THRESHOLD`: Summary threshold (default: 6000, triggers compression when exceeded)
- `RECURSION_LIMIT`: Workflow recursion limit (default: 100, prevents infinite loops)

## 📖 Usage

### 1. Prepare Requirement Documents

Create a project folder under the requirement document directory and place requirement documents:

```bash
# Create project directory (PROJECT_NAME must match the configuration in config.json)
mkdir -p <requirement-document-directory>/<PROJECT_NAME>
# Place requirement documents (.md, .docx, .pdf) in this directory
```

Supported document formats:
- Markdown (.md): Read directly
- Word documents (.docx): Automatically converted to Markdown with image extraction support
- PDF documents (.pdf): Automatically extracts text and converts to Markdown

The system automatically handles document conversion. DOCX files extract images to the `img/` subdirectory, and PDF files extract text content from all pages.

### 2. Create .spanignore File

Create a `.spanignore` file in the project root directory, specifying directories to ignore during requirement document analysis (one per line):

```
node_modules
__pycache__
.git
```

This file is used to filter out directories that don't need processing in `execute_plan_node`.

### 3. Run the System

```bash
python main.py
```

Or specify initial count:

```bash
python main.py --count 0
```

### 4. Interactive Flow

The system will require manual confirmation during execution:

1. **todo.md Confirmation**: If `todo.md` already exists, the system will ask whether to delete it (enter `y` to delete, `n` to keep)
2. **todo_list.md Confirmation**: If `todo_list.md` already exists, the system will ask whether to delete it (first development round)
3. **Plan Confirmation**: After the system generates an execution plan, check the execution plan file, enter `pass` to continue or `reject` to regenerate
4. **File Conversion Warning**: If there are files that cannot be parsed, the system will generate a warning file. After reviewing, enter `pass` to continue
5. **Review Opinion Confirmation**: After review is complete, check the review opinion file, enter `pass` to finish or `reject` to continue modifications

## 📁 Project Structure

```
auto-coder/
├── main.py                    # Main entry file, defines main workflow
├── config.default.json        # Configuration template
├── constants.py               # Constant definitions (code extensions, error messages, etc.)
├── custom_type.py             # Main workflow type definitions (ActionReview, Action, Response, Act)
│
├── count_node.py              # Counter node, manages development rounds and state backup
│
├── execute_zgraph.py          # Execution workflow graph, defines execution subgraph
├── execute_plan_node.py        # Planning node, analyzes requirements and generates execution plans
├── execute_plan_utils.py       # Planning utility functions (document conversion, requirement analysis)
├── execute_execute_node.py     # Execution node, executes plan tasks
├── execute_execute_tool.py     # Execution tools (code expert, file operations, etc.)
├── execute_replan_node.py      # Replanning node, dynamically adjusts plans
├── execute_replan_utils.py     # Replanning utility functions (project status analysis)
├── execute_custom_type.py      # Execution workflow type definitions (PlanExecute, Plan, Response, Act)
│
├── review_node.py             # Review node, reviews code quality
├── review_tool.py             # Review tools (read/write review opinions, read requirement documents, etc.)
│
├── sim_sdk/                   # Simulated Cursor SDK (used in MOCK mode)
│   └── sim_sdk.py
│
├── examples/                  # Usage examples
│   └── README.md              # Example documentation
│
├── tests/                     # Test suite
│   ├── __init__.py
│   ├── conftest.py            # Pytest configuration and fixtures
│   ├── test_constants.py      # Tests for constants module
│   ├── test_custom_type.py    # Tests for type definitions
│   ├── test_count_node.py     # Tests for counter node
│   ├── test_execute_plan_utils.py      # Tests for planning utilities
│   ├── test_execute_replan_utils.py    # Tests for replanning utilities
│   ├── test_review_tool.py    # Tests for review tools
│   ├── test_execute_execute_tool.py    # Tests for execution tools
│   └── README.md              # Test documentation
│
├── .github/                   # GitHub configuration
│   ├── workflows/             # CI/CD workflows
│   │   ├── ci.yml             # Main CI workflow
│   │   ├── test.yml           # Comprehensive test suite
│   │   ├── lint.yml           # Code quality checks
│   │   ├── release.yml        # Release automation
│   │   └── dependency-review.yml  # Dependency security review
│   ├── ISSUE_TEMPLATE/        # Issue templates
│   │   ├── bug_report.md
│   │   └── feature_request.md
│   └── PULL_REQUEST_TEMPLATE.md
│
├── requirements.txt           # Python dependency list
├── setup.py                   # Project installation configuration
├── pyproject.toml              # Project metadata configuration
├── .pre-commit-config.yaml    # Pre-commit hooks configuration
├── LICENSE                     # MIT License
├── CONTRIBUTING.md             # Contribution guidelines
├── CHANGELOG.md                # Changelog
├── README.md                   # Project documentation (Chinese)
└── README_EN.md                # Project documentation (English, this file)
```

**Note**: The following directories and files are in `.gitignore` and will not appear in version control:
- `config.json` - User configuration file (contains API keys)
- `experiment/` - Experiment directory
- `history/` - History backup directory
- `opinion/` - Review opinion directory
- `todo/` - Requirement document directory
- `dist/` - Distribution directory
- `__pycache__/` - Python cache directory
- `*.pyc`, `*.pyo`, `*.pyd` - Python compiled files
- `*.log` - Log files
- Other build and temporary files

## 🔧 Core Features Explained

### Requirements Analysis (execute_plan_node)

The system automatically:
1. **Document Conversion**: Converts DOCX/PDF documents to Markdown format
   - DOCX: Extracts text, tables, and images (images saved to `img/` subdirectory)
   - PDF: Extracts text content from all pages
2. **Requirements Integration**: Calls Cursor Agent to analyze all requirement documents and generate a unified requirement description (`todo.md`)
3. **Plan Generation**: Uses Qwen-max model to generate detailed execution plans (`todo_list.md`)
4. **Plan Confirmation**: Supports user interactive confirmation, can improve plans multiple times

### Code Execution (execute_execute_node)

Calls the following tools through LangChain Agent:
- **code_professional**: Code expert that calls Cursor Agent for code analysis and writing
- **mkdir**: Create directories
- **rm**: Delete files or directories
- **list_files**: List files in specified directory
- **search_todo_dir**: Search and read files in requirement document directory

### Code Review (review_node)

The review agent will:
1. Read requirement documents and development logs
2. Check if code complies with all functional points in the requirement documents
3. Check if code has fixed previous review opinions
4. Generate review opinion file (`opinion/{PROJECT_NAME}.md`)
5. Determine whether further modifications are needed (returns `count` to continue or `response` to end)

### Dynamic Replanning (execute_replan_node)

The system will dynamically adjust subsequent execution plans based on:
- **Execution Results**: Completed steps and responses
- **Current Project Status**: Calls Cursor Agent to analyze actual project code status
- **Review Opinions**: Adjusts plans based on reviewer opinions
- **Requirement Documents**: Ensures plans comply with original requirements

Supports context compression to control token consumption.

### State Management (counter_node)

The counter node is responsible for:
1. Managing development rounds (`count`)
2. Backing up project state (copying from `dist/` to `history/`)
3. Handling user interaction confirmations (review opinion confirmation)
4. Determining whether the workflow should end (based on `response` field)

## ⚠️ Important Notes

1. **API Key Security**: `config.json` is configured in `.gitignore`. Do not commit configuration files containing real API keys to version control systems
2. **Recursion Limit**: Set `RECURSION_LIMIT` appropriately to avoid infinite loops or premature termination. Default value is 100, can be adjusted based on project complexity
3. **Token Consumption**: Large numbers of LLM calls will incur costs. Monitor usage carefully. The system has implemented context compression functionality (`SUMMARY_MAX_LENGTH` and `SUMMARY_THRESHOLD`) to reduce token consumption
4. **File Permissions**: Ensure the system has sufficient file system operation permissions, especially read/write permissions for project directories
5. **Network Connection**: Requires stable network connection to access LLM APIs (Qwen, DeepSeek) and Cursor Agent
6. **Windows Environment**: Using on Windows requires WSL or Git Bash support for bash commands, as tool execution uses `subprocess.run(["bash", "-c", ...])`
7. **MOCK Mode**: Can use MOCK mode for development and testing by setting `MOCK=true` and using `sim_sdk/sim_sdk.py`
8. **Structured Output**: The system uses Pydantic models to ensure correct LLM output format. Will automatically retry on failure (up to 3 times)

## 🐛 Troubleshooting

### Issue: Execution Failure

- Check if `config.json` configuration is correct, especially API keys and path configurations
- Confirm API keys are valid and have sufficient quota
- Check if Cursor Agent CLI is correctly installed (non-MOCK mode)
- Check if `SIM_CURSOR_PATH` path is correct (MOCK mode)
- Check log output to understand specific error information

### Issue: Unable to Parse Documents

- Check warning files (`warning.md` or `warning_{n}.md`) to see which files cannot be parsed
- Manually convert files to Markdown format and place them in the requirement document directory
- Ensure file encoding is UTF-8

### Issue: Structured Output Errors

- The system will automatically retry (up to 3 times)
- If failures persist, check if LLM API is normal and network connection is stable
- Check if API keys are valid
- Check error information in logs

### Issue: Recursion Limit Premature Termination

- Increase `RECURSION_LIMIT` configuration value
- Check if there is infinite loop logic
- Check execution logs to understand workflow execution status

### Issue: Bash Command Execution Failure (Windows)

- Ensure WSL or Git Bash is installed
- Check if bash is included in system PATH
- May need to use Git Bash terminal to run on Windows

### Issue: File Path Errors

- Ensure `PROJECT_NAME` configuration matches the requirement document directory name
- Check if relative paths are correct
- Ensure project directory structure is correctly created

## 🧪 Testing

### Running Tests

The project includes a comprehensive test suite using pytest. To run tests:

```bash
# Install test dependencies
pip install pytest pytest-cov pytest-asyncio

# Run all tests
pytest tests/ -v

# Run tests with coverage
pytest tests/ --cov=. --cov-report=html --cov-report=term-missing

# Run specific test file
pytest tests/test_constants.py -v

# Run specific test class or function
pytest tests/test_constants.py::TestCodeExtensions -v
```

### Test Coverage

The test suite covers:
- Constants and type definitions
- Core node functions (counter, plan, execute, replan, review)
- Utility functions (document conversion, script execution)
- Tool functions (file operations, code generation)

### CI/CD

The project uses GitHub Actions for continuous integration:

- **Automated Testing**: Tests run on multiple Python versions (3.8-3.11) and platforms (Ubuntu, Windows, macOS)
- **Code Quality**: Automated linting with Black, Flake8, and pre-commit hooks
- **Coverage Reports**: Automatic coverage reporting to Codecov
- **Dependency Review**: Automatic security review of dependencies

See `.github/workflows/README.md` for detailed workflow documentation.

## 📝 Development Guide

### Adding New Tools

Add new `@tool` decorated functions in `execute_execute_tool.py` or `review_tool.py`, and update the `tools` list.

Example:
```python
@tool
def my_new_tool(param: str) -> str:
    """Tool description"""
    # Implementation logic
    return "Execution result"

tools = [..., my_new_tool]  # Add to tools list
```

**Important**: When adding new tools, also add corresponding test cases in the `tests/` directory.

### Modifying Workflow

Edit the `_init_graph()` function in `main.py` or `execute_zgraph.py` to modify node and edge definitions.

### Customizing Prompts

Modify prompts in Agent initialization functions of each node:
- `execute_plan_node.py`: `plan_prompt` and `improve_opinion_prompt`
- `execute_execute_node.py`: `_prompt` (in `_init_agent()`)
- `execute_replan_node.py`: `summary_prompt` and `_prompt`
- `review_node.py`: `_prompt` (in `init_agent()`)

### Modifying Type Definitions

- Main workflow types: `custom_type.py`
- Execution workflow types: `execute_custom_type.py`
- Constant definitions: `constants.py`

### Adding New Document Format Support

Add new conversion functions in `execute_plan_utils.py` and call them in `check_and_convert_file()`.

### Code Quality

Before submitting code:

1. **Run tests**: `pytest tests/ -v`
2. **Format code**: `black .`
3. **Check style**: `flake8 .`
4. **Run pre-commit**: `pre-commit run --all-files`

The CI/CD pipeline will automatically check these on every push and pull request.

## 📄 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## 🤝 Contributing

Issues and Pull Requests are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

### Before Contributing

1. **Fork the repository** and create a feature branch
2. **Write tests** for new features or bug fixes
3. **Ensure all tests pass**: `pytest tests/ -v`
4. **Follow code style**: Run `black .` and `flake8 .`
5. **Update documentation** if needed
6. **Submit a Pull Request** with a clear description

The project uses:
- **Conventional Commits** for commit messages
- **Pre-commit hooks** for code quality
- **GitHub Actions** for CI/CD
- **Codecov** for coverage tracking

See `.github/PULL_REQUEST_TEMPLATE.md` for PR guidelines.

## 📧 Contact

For questions or suggestions, please contact via Issues.

---

**Note**: This system is an experimental project. Please test thoroughly before using in production environments.

