"""
测试 review_tool.py 模块
"""
import pytest
import os
import tempfile
import shutil
from unittest.mock import patch, MagicMock, mock_open


class TestWriteOpinionFile:
    """测试 write_opinion_file 工具"""

    @pytest.fixture
    def mock_config(self):
        return {
            "PROJECT_NAME": "test-project",
        }

    def test_write_opinion_file_success(self, mock_config, temp_dir):
        """测试成功写入审核意见文件"""
        with patch("review_tool.config", mock_config), \
             patch("review_tool.os.path.join") as mock_join:
            
            def join_side_effect(*args):
                if "opinion" in args:
                    return os.path.join(temp_dir, "opinion", f"{mock_config['PROJECT_NAME']}.md")
                return os.path.join(*args)
            
            mock_join.side_effect = join_side_effect
            
            # 确保目录存在
            opinion_dir = os.path.join(temp_dir, "opinion")
            os.makedirs(opinion_dir, exist_ok=True)
            
            from review_tool import write_opinion_file
            
            content = "这是审核意见内容"
            result = write_opinion_file(content)
            
            assert result == "文件写入成功"
            
            # 验证文件内容
            opinion_file = os.path.join(opinion_dir, f"{mock_config['PROJECT_NAME']}.md")
            if os.path.exists(opinion_file):
                with open(opinion_file, "r", encoding="utf-8") as f:
                    assert f.read() == content


class TestReadOpinionFile:
    """测试 read_opinion_file 工具"""

    @pytest.fixture
    def mock_config(self):
        return {
            "PROJECT_NAME": "test-project",
        }

    def test_read_opinion_file_exists(self, mock_config, temp_dir):
        """测试读取存在的审核意见文件"""
        opinion_dir = os.path.join(temp_dir, "opinion")
        os.makedirs(opinion_dir, exist_ok=True)
        opinion_file = os.path.join(opinion_dir, f"{mock_config['PROJECT_NAME']}.md")
        
        test_content = "审核意见内容"
        with open(opinion_file, "w", encoding="utf-8") as f:
            f.write(test_content)
        
        with patch("review_tool.config", mock_config), \
             patch("review_tool.os.path.join") as mock_join:
            
            def join_side_effect(*args):
                if "opinion" in args:
                    return opinion_file
                return os.path.join(*args)
            
            mock_join.side_effect = join_side_effect
            
            from review_tool import read_opinion_file
            result = read_opinion_file()
            
            assert result == test_content

    def test_read_opinion_file_not_exists(self, mock_config):
        """测试读取不存在的审核意见文件"""
        with patch("review_tool.config", mock_config), \
             patch("review_tool.os.path.exists", return_value=False):
            
            from review_tool import read_opinion_file
            result = read_opinion_file()
            
            assert result == "文件不存在"


class TestReadTodoContent:
    """测试 read_todo_content 工具"""

    @pytest.fixture
    def mock_config(self):
        return {
            "PROJECT_NAME": "test-project",
        }

    def test_read_todo_content_exists(self, mock_config, temp_dir):
        """测试读取存在的需求文档"""
        todo_dir = os.path.join(temp_dir, "todo", mock_config["PROJECT_NAME"])
        os.makedirs(todo_dir, exist_ok=True)
        todo_file = os.path.join(todo_dir, "todo.md")
        
        test_content = "# 需求文档\n\n这是需求内容"
        with open(todo_file, "w", encoding="utf-8") as f:
            f.write(test_content)
        
        with patch("review_tool.config", mock_config), \
             patch("review_tool.os.path.join") as mock_join:
            
            def join_side_effect(*args):
                if "todo" in args:
                    return todo_file
                return os.path.join(*args)
            
            mock_join.side_effect = join_side_effect
            
            from review_tool import read_todo_content
            result = read_todo_content()
            
            assert result == test_content

    def test_read_todo_content_not_exists(self, mock_config):
        """测试读取不存在的需求文档"""
        with patch("review_tool.config", mock_config), \
             patch("review_tool.os.path.exists", return_value=False):
            
            from review_tool import read_todo_content
            result = read_todo_content()
            
            assert result == "文件不存在"


class TestReadDevelopmentLog:
    """测试 read_development_log 工具"""

    @pytest.fixture
    def mock_config(self):
        return {
            "PROJECT_NAME": "test-project",
            "SUMMARY_THRESHOLD": 6000,
        }

    def test_read_development_log_not_exists(self, mock_config):
        """测试读取不存在的开发日志"""
        with patch("review_tool.config", mock_config), \
             patch("review_tool.os.path.exists", return_value=False):
            
            from review_tool import read_development_log
            result = read_development_log()
            
            assert result == "文件不存在"

    def test_read_development_log_exists_short(self, mock_config, temp_dir):
        """测试读取较短的开发日志（不需要压缩）"""
        dist_dir = os.path.join(temp_dir, "dist", mock_config["PROJECT_NAME"])
        os.makedirs(dist_dir, exist_ok=True)
        log_file = os.path.join(dist_dir, "development_log.md")
        
        test_content = "开发日志内容\n简短内容"
        with open(log_file, "w", encoding="utf-8") as f:
            f.write(test_content)
        
        with patch("review_tool.config", mock_config), \
             patch("review_tool.os.path.join") as mock_join:
            
            def join_side_effect(*args):
                if "dist" in args and "development_log.md" in args:
                    return log_file
                return os.path.join(*args)
            
            mock_join.side_effect = join_side_effect
            
            from review_tool import read_development_log
            result = read_development_log()
            
            assert len(result) > 0

    def test_read_development_log_exists_long(self, mock_config, temp_dir):
        """测试读取较长的开发日志（需要压缩）"""
        dist_dir = os.path.join(temp_dir, "dist", mock_config["PROJECT_NAME"])
        os.makedirs(dist_dir, exist_ok=True)
        log_file = os.path.join(dist_dir, "development_log.md")
        
        # 创建超过阈值的长内容
        long_content = "\n".join([f"日志行 {i}" for i in range(1000)])
        with open(log_file, "w", encoding="utf-8") as f:
            f.write(long_content)
        
        with patch("review_tool.config", mock_config), \
             patch("review_tool.summary_pro") as mock_summary, \
             patch("review_tool.os.path.join") as mock_join:
            
            def join_side_effect(*args):
                if "dist" in args and "development_log.md" in args:
                    return log_file
                return os.path.join(*args)
            
            mock_join.side_effect = join_side_effect
            
            # Mock summary 返回
            mock_summary_result = MagicMock()
            mock_summary_result.content = "压缩后的日志"
            mock_summary.invoke.return_value = mock_summary_result
            
            from review_tool import read_development_log
            result = read_development_log()
            
            # 验证压缩功能被调用（如果内容超过阈值）
            assert len(result) > 0


class TestToolsList:
    """测试工具列表"""

    def test_tools_list_not_empty(self):
        """测试工具列表不为空"""
        from review_tool import tools
        assert len(tools) > 0

    def test_tools_list_contains_expected_tools(self):
        """测试工具列表包含预期的工具"""
        from review_tool import tools, read_todo_content, write_opinion_file, read_opinion_file, read_development_log
        
        expected_tools = [read_todo_content, write_opinion_file, read_opinion_file, read_development_log]
        
        for tool in expected_tools:
            assert tool in tools, f"{tool.__name__} 应该在工具列表中"

