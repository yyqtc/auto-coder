"""
Pytest 配置文件和共享 fixtures
"""

import pytest
import json
import os
import tempfile
import shutil
from pathlib import Path


@pytest.fixture
def temp_dir():
    """创建临时目录用于测试"""
    temp_path = tempfile.mkdtemp()
    yield temp_path
    shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture
def sample_config():
    """示例配置字典"""
    return {
        "PROJECT_NAME": "test-project",
        "MOCK": True,
        "SIM_CURSOR_PATH": "./sim_sdk/sim_sdk.py",
        "CURSOR_PATH": "/root/.local/bin/cursor-agent",
        "EXECUTE_PATH": "execute-agent.bat",
        "CURSOR_API_KEY": "test-api-key",
        "QWEN_API_KEY": "test-qwen-key",
        "QWEN_API_BASE": "https://dashscope.aliyuncs.com/compatible-mode/v1",
        "DEEPSEEK_API_KEY": "test-deepseek-key",
        "DEEPSEEK_API_BASE": "https://api.deepseek.com",
        "SUMMARY_MAX_LENGTH": 2000,
        "SUMMARY_THRESHOLD": 6000,
        "RECURSION_LIMIT": 100,
    }


@pytest.fixture
def temp_config_file(sample_config, temp_dir):
    """创建临时配置文件"""
    config_path = os.path.join(temp_dir, "config.json")
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(sample_config, f, ensure_ascii=False, indent=4)
    return config_path


@pytest.fixture
def sample_markdown_content():
    """示例 Markdown 内容"""
    return """# 测试需求文档

## 功能需求

1. 创建用户登录功能
2. 实现数据展示页面
3. 添加文件上传功能

## 技术要求

- 使用 Python Flask 框架
- 数据库使用 SQLite
- 前端使用 Bootstrap
"""


@pytest.fixture
def sample_todo_list():
    """示例待办列表"""
    return [
        "步骤1: 创建项目基础结构",
        "步骤2: 实现用户认证功能",
        "步骤3: 创建数据库模型",
        "步骤4: 实现API接口",
        "步骤5: 创建前端页面",
    ]


@pytest.fixture
def mock_file_structure(temp_dir):
    """创建模拟的文件结构"""
    project_dir = os.path.join(temp_dir, "test-project")
    os.makedirs(project_dir, exist_ok=True)

    # 创建子目录
    os.makedirs(os.path.join(project_dir, "src"), exist_ok=True)
    os.makedirs(os.path.join(project_dir, "tests"), exist_ok=True)

    # 创建测试文件
    test_file = os.path.join(project_dir, "test.py")
    with open(test_file, "w", encoding="utf-8") as f:
        f.write("print('Hello, World!')")

    return project_dir
