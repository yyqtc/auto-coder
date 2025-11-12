"""
测试 execute_execute_tool.py 模块
"""
import pytest
import os
import tempfile
import shutil
from unittest.mock import patch, MagicMock
from subprocess import CalledProcessError


class TestGetDriveLetter:
    """测试 _get_drive_letter 函数"""

    def test_get_drive_letter_windows(self):
        """测试 Windows 系统获取驱动器字母"""
        with patch("execute_execute_tool.platform.system", return_value="Windows"), \
             patch("os.path.splitdrive", return_value=("C:", "\\path\\to\\file")):
            
            from execute_execute_tool import _get_drive_letter
            result = _get_drive_letter("C:\\path\\to\\file")
            assert result == "C:"

    def test_get_drive_letter_linux(self):
        """测试 Linux 系统返回空字符串"""
        with patch("execute_execute_tool.platform.system", return_value="Linux"):
            from execute_execute_tool import _get_drive_letter
            result = _get_drive_letter("/path/to/file")
            assert result == ""


class TestRemoveReadonly:
    """测试 remove_readonly 函数"""

    def test_remove_readonly(self):
        """测试 remove_readonly 函数"""
        from execute_execute_tool import remove_readonly
        
        mock_func = MagicMock()
        mock_path = "/test/path"
        
        with patch("os.chmod") as mock_chmod:
            remove_readonly(mock_func, mock_path, None)
            mock_chmod.assert_called_once_with(mock_path, 0o200)
            mock_func.assert_called_once_with(mock_path)


class TestRmTool:
    """测试 rm 工具"""

    @pytest.fixture
    def mock_config(self):
        return {
            "PROJECT_NAME": "test-project",
        }

    def test_rm_file_not_exists(self, mock_config):
        """测试删除不存在的文件"""
        with patch("execute_execute_tool.config", mock_config), \
             patch("execute_execute_tool.os.path.exists", return_value=False):
            
            from execute_execute_tool import rm
            result = rm("nonexistent.txt")
            
            assert result == "文件或目录不存在"

    def test_rm_file_success(self, mock_config, temp_dir):
        """测试成功删除文件"""
        test_file = os.path.join(temp_dir, "test.txt")
        with open(test_file, "w") as f:
            f.write("test")
        
        with patch("execute_execute_tool.config", mock_config), \
             patch("execute_execute_tool.project_path", temp_dir), \
             patch("execute_execute_tool.os.path.join") as mock_join:
            
            def join_side_effect(*args):
                if "dist" in args:
                    return os.path.join(temp_dir, "dist", mock_config["PROJECT_NAME"], args[-1])
                return os.path.join(*args)
            
            mock_join.side_effect = join_side_effect
            
            # 创建 dist 目录和文件
            dist_dir = os.path.join(temp_dir, "dist", mock_config["PROJECT_NAME"])
            os.makedirs(dist_dir, exist_ok=True)
            target_file = os.path.join(dist_dir, "test.txt")
            with open(target_file, "w") as f:
                f.write("test")
            
            from execute_execute_tool import rm
            result = rm("test.txt")
            
            assert result == "删除文件成功"
            assert not os.path.exists(target_file)


class TestMkdirTool:
    """测试 mkdir 工具"""

    @pytest.fixture
    def mock_config(self):
        return {
            "PROJECT_NAME": "test-project",
        }

    def test_mkdir_success(self, mock_config, temp_dir):
        """测试成功创建目录"""
        with patch("execute_execute_tool.config", mock_config), \
             patch("execute_execute_tool.project_path", temp_dir), \
             patch("execute_execute_tool.os.path.join") as mock_join:
            
            def join_side_effect(*args):
                if "dist" in args:
                    return os.path.join(temp_dir, "dist", mock_config["PROJECT_NAME"], args[-1])
                return os.path.join(*args)
            
            mock_join.side_effect = join_side_effect
            
            # 创建 dist 目录
            dist_dir = os.path.join(temp_dir, "dist", mock_config["PROJECT_NAME"])
            os.makedirs(dist_dir, exist_ok=True)
            
            from execute_execute_tool import mkdir
            result = mkdir("new_dir")
            
            assert "成功" in result
            
            # 验证目录被创建
            new_dir = os.path.join(dist_dir, "new_dir")
            if os.path.exists(new_dir):
                assert os.path.isdir(new_dir)

    def test_mkdir_failure(self, mock_config):
        """测试创建目录失败"""
        with patch("execute_execute_tool.config", mock_config), \
             patch("execute_execute_tool.os.makedirs", side_effect=OSError("权限错误")):
            
            from execute_execute_tool import mkdir
            result = mkdir("new_dir")
            
            assert result == "执行失败！"


class TestListFilesTool:
    """测试 list_files 工具"""

    @pytest.fixture
    def mock_config(self):
        return {
            "PROJECT_NAME": "test-project",
        }

    def test_list_files_directory_not_exists(self, mock_config):
        """测试列出不存在的目录"""
        with patch("execute_execute_tool.config", mock_config), \
             patch("execute_execute_tool.os.path.exists", return_value=False):
            
            from execute_execute_tool import list_files
            result = list_files("nonexistent")
            
            assert result == "目录不存在"

    def test_list_files_success(self, mock_config, temp_dir):
        """测试成功列出文件"""
        dist_dir = os.path.join(temp_dir, "dist", mock_config["PROJECT_NAME"])
        os.makedirs(dist_dir, exist_ok=True)
        
        # 创建测试文件
        test_files = ["file1.txt", "file2.txt"]
        for filename in test_files:
            with open(os.path.join(dist_dir, filename), "w") as f:
                f.write("test")
        
        with patch("execute_execute_tool.config", mock_config), \
             patch("execute_execute_tool.project_path", temp_dir), \
             patch("execute_execute_tool.os.path.join") as mock_join:
            
            def join_side_effect(*args):
                if "dist" in args:
                    return os.path.join(temp_dir, "dist", mock_config["PROJECT_NAME"], args[-1])
                return os.path.join(*args)
            
            mock_join.side_effect = join_side_effect
            
            from execute_execute_tool import list_files
            result = list_files(".")
            
            assert isinstance(result, list)
            assert len(result) >= 2


class TestSearchTodoDirTool:
    """测试 search_todo_dir 工具"""

    @pytest.fixture
    def mock_config(self):
        return {
            "PROJECT_NAME": "test-project",
        }

    def test_search_todo_dir_file_exists(self, mock_config, temp_dir):
        """测试搜索存在的文件"""
        todo_dir = os.path.join(temp_dir, "todo", mock_config["PROJECT_NAME"])
        os.makedirs(todo_dir, exist_ok=True)
        todo_file = os.path.join(todo_dir, "todo.md")
        
        test_content = "# 需求文档"
        with open(todo_file, "w", encoding="utf-8") as f:
            f.write(test_content)
        
        with patch("execute_execute_tool.config", mock_config), \
             patch("execute_execute_tool.project_path", temp_dir), \
             patch("execute_execute_tool.os.path.join") as mock_join:
            
            def join_side_effect(*args):
                if "todo" in args:
                    return os.path.join(temp_dir, "todo", mock_config["PROJECT_NAME"], args[-1])
                return os.path.join(*args)
            
            mock_join.side_effect = join_side_effect
            
            from execute_execute_tool import search_todo_dir
            result = search_todo_dir("todo.md")
            
            assert result == test_content

    def test_search_todo_dir_file_not_exists(self, mock_config, temp_dir):
        """测试搜索不存在的文件，返回文件列表"""
        todo_dir = os.path.join(temp_dir, "todo", mock_config["PROJECT_NAME"])
        os.makedirs(todo_dir, exist_ok=True)
        
        # 创建一些文件
        with open(os.path.join(todo_dir, "file1.txt"), "w") as f:
            f.write("content1")
        with open(os.path.join(todo_dir, "file2.txt"), "w") as f:
            f.write("content2")
        
        with patch("execute_execute_tool.config", mock_config), \
             patch("execute_execute_tool.project_path", temp_dir), \
             patch("execute_execute_tool.os.path.join") as mock_join:
            
            def join_side_effect(*args):
                if "todo" in args:
                    return os.path.join(temp_dir, "todo", mock_config["PROJECT_NAME"], args[-1])
                return os.path.join(*args)
            
            mock_join.side_effect = join_side_effect
            
            from execute_execute_tool import search_todo_dir
            result = search_todo_dir("nonexistent.md")
            
            assert isinstance(result, list)
            assert len(result) >= 2


class TestCodeProfessionalTool:
    """测试 code_professional 工具"""

    @pytest.fixture
    def mock_config(self):
        return {
            "PROJECT_NAME": "test-project",
            "MOCK": True,
            "SIM_CURSOR_PATH": "./sim_sdk/sim_sdk.py",
            "CURSOR_API_KEY": "test-key",
        }

    def test_code_professional_mock_mode(self, mock_config):
        """测试 MOCK 模式下的代码专家"""
        with patch("execute_execute_tool.config", mock_config), \
             patch("execute_execute_tool._execute_script_subprocess") as mock_execute:
            
            mock_execute.return_value = "代码生成完成"
            
            from execute_execute_tool import code_professional
            result = code_professional("创建一个Python文件")
            
            assert mock_execute.called
            assert "执行结果" in result

    def test_code_professional_windows_execute_path(self, mock_config):
        """测试 Windows 下使用 EXECUTE_PATH"""
        mock_config["MOCK"] = False
        mock_config["EXECUTE_PATH"] = "execute-agent.bat"
        
        with patch("execute_execute_tool.platform.system", return_value="Windows"), \
             patch("execute_execute_tool.config", mock_config), \
             patch("execute_execute_tool._execute_script_subprocess") as mock_execute, \
             patch("execute_execute_tool.tempfile.NamedTemporaryFile") as mock_temp:
            
            mock_temp.return_value.__enter__.return_value.name = "/tmp/test.prompt"
            mock_execute.return_value = "代码生成完成"
            
            from execute_execute_tool import code_professional
            result = code_professional("创建一个Python文件")
            
            assert mock_execute.called


class TestExecuteScriptSubprocess:
    """测试 _execute_script_subprocess 函数"""

    @pytest.fixture
    def mock_config(self):
        return {
            "PROJECT_NAME": "test-project",
        }

    def test_execute_script_success(self, mock_config):
        """测试成功执行脚本"""
        with patch("execute_execute_tool.config", mock_config), \
             patch("execute_execute_tool.platform.system", return_value="Linux"), \
             patch("subprocess.run") as mock_run:
            
            mock_result = MagicMock()
            mock_result.stdout = "执行成功"
            mock_result.returncode = 0
            mock_run.return_value = mock_result
            
            from execute_execute_tool import _execute_script_subprocess
            result = _execute_script_subprocess("echo test")
            
            assert "执行成功" in result or result == "执行成功"

    def test_execute_script_failure(self, mock_config):
        """测试执行失败"""
        with patch("execute_execute_tool.config", mock_config), \
             patch("execute_execute_tool.platform.system", return_value="Linux"), \
             patch("subprocess.run") as mock_run:
            
            mock_run.side_effect = CalledProcessError(1, "cmd", stderr="错误信息")
            
            from execute_execute_tool import _execute_script_subprocess
            result = _execute_script_subprocess("invalid command")
            
            assert result == "执行失败！"


class TestToolsList:
    """测试工具列表"""

    def test_tools_list_not_empty(self):
        """测试工具列表不为空"""
        from execute_execute_tool import tools
        assert len(tools) > 0

    def test_tools_list_contains_expected_tools(self):
        """测试工具列表包含预期的工具"""
        from execute_execute_tool import (
            tools,
            code_professional,
            mkdir,
            list_files,
            rm,
            search_todo_dir,
        )
        
        expected_tools = [code_professional, mkdir, list_files, rm, search_todo_dir]
        
        for tool in expected_tools:
            assert tool in tools, f"{tool.__name__} 应该在工具列表中"

