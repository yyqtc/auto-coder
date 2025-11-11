# 常见的代码文件扩展名（可根据需要增减）
CODE_EXTENSIONS = [
    ".py",  # Python
    ".js",  # JavaScript
    ".ts",  # TypeScript
    ".jsx",  # React JSX
    ".tsx",  # TypeScript JSX
    ".java",  # Java
    ".cpp",
    ".cc",
    ".cxx",  # C++
    ".c",  # C
    ".h",
    ".hpp",  # C/C++ 头文件
    ".cs",  # C#
    ".go",  # Go
    ".rs",  # Rust
    ".rb",  # Ruby
    ".php",  # PHP
    ".swift",  # Swift
    ".kt",
    ".kts",  # Kotlin
    ".scala",  # Scala
    ".sh",  # Shell 脚本
    ".bash",  # Bash 脚本
    ".pl",  # Perl
    ".lua",  # Lua
    ".sql",  # SQL
    ".html",
    ".htm",  # HTML（有时视为代码）
    ".css",  # CSS
    ".scss",
    ".sass",
    ".less",
    ".json",  # 配置/数据，但常被当作代码处理
    ".yaml",
    ".yml",
    ".toml",
    ".xml",
]

# execute_plan_node 分析需求失败时的返回值
REQUIREMENT_FAIL_MESSAGE = "需求分析失败！"

# execute_replan_node 读取需求失败时的返回值
REQUIREMENT_READ_FAIL_MESSAGE = "需求读取失败！"

# 未知错误时的返回值
UNKNOWN_ERROR_MESSAGE = "未知错误！"

# 读取开发日志失败的信息
DEVELOPMENT_LOG_NOT_EXISTS = "读取开发日志失败！"
