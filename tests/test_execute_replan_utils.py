"""
测试 execute_replan_utils.py 模块
"""

import pytest
import os
from unittest.mock import patch, MagicMock


class TestGetDriveLetter:
    """测试 _get_drive_letter 函数"""

    def test_get_drive_letter_windows(self):
        """测试 Windows 系统获取驱动器字母"""
        with patch("execute_replan_utils.platform.system", return_value="Windows"), patch(
            "os.path.splitdrive", return_value=("C:", "\\path\\to\\file")
        ):

            from execute_replan_utils import _get_drive_letter

            result = _get_drive_letter("C:\\path\\to\\file")
            assert result == "C:"

    def test_get_drive_letter_linux(self):
        """测试 Linux 系统返回空字符串"""
        with patch("execute_replan_utils.platform.system", return_value="Linux"):
            from execute_replan_utils import _get_drive_letter

            result = _get_drive_letter("/path/to/file")
            assert result == ""


class TestExecuteScriptSubprocess:
    """测试 _execute_script_subprocess 函数"""

    @pytest.fixture
    def mock_config(self):
        return {
            "PROJECT_NAME": "test-project",
            "MOCK": False,
            "CURSOR_PATH": "/usr/bin/cursor-agent",
        }

    def test_execute_script_windows_success(self, mock_config):
        """测试 Windows 系统成功执行"""
        with patch("execute_replan_utils.platform.system", return_value="Windows"), patch(
            "execute_replan_utils.config", mock_config
        ), patch("subprocess.run") as mock_run:

            mock_result = MagicMock()
            mock_result.stdout = "执行成功"
            mock_result.returncode = 0
            mock_run.return_value = mock_result

            from execute_replan_utils import _execute_script_subprocess

            result = _execute_script_subprocess("echo test")

            assert "执行成功" in result or result == "执行成功"

    def test_execute_script_linux_success(self, mock_config):
        """测试 Linux 系统成功执行"""
        with patch("execute_replan_utils.platform.system", return_value="Linux"), patch(
            "execute_replan_utils.config", mock_config
        ), patch("subprocess.run") as mock_run:

            mock_result = MagicMock()
            mock_result.stdout = "执行成功"
            mock_result.returncode = 0
            mock_run.return_value = mock_result

            from execute_replan_utils import _execute_script_subprocess

            result = _execute_script_subprocess("echo test")

            assert "执行成功" in result or result == "执行成功"

    def test_execute_script_failure(self, mock_config):
        """测试执行失败的情况"""
        with patch("execute_replan_utils.platform.system", return_value="Linux"), patch(
            "execute_replan_utils.config", mock_config
        ), patch("subprocess.run") as mock_run:

            from subprocess import CalledProcessError

            mock_run.side_effect = CalledProcessError(1, "cmd", stderr="错误信息")

            from execute_replan_utils import _execute_script_subprocess

            result = _execute_script_subprocess("invalid command")

            assert result == "执行失败！"


class TestAnalyzeWhatToDo:
    """测试 analyze_what_to_do 函数"""

    @pytest.fixture
    def mock_config(self):
        return {
            "PROJECT_NAME": "test-project",
            "MOCK": True,
            "SIM_CURSOR_PATH": "./sim_sdk/sim_sdk.py",
            "CURSOR_API_KEY": "test-key",
            "SUMMARY_THRESHOLD": 6000,
        }

    def test_analyze_what_to_do_basic(self, mock_config):
        """测试基本分析功能"""
        with patch("execute_replan_utils.config", mock_config), patch(
            "execute_replan_utils._execute_script_subprocess"
        ) as mock_execute, patch("os.path.exists", return_value=False):

            mock_execute.return_value = "分析完成"

            from execute_replan_utils import analyze_what_to_do

            result = analyze_what_to_do(count=0, past_steps_content="", plan="")

            assert mock_execute.called
            assert "分析完成" in result or result == "分析完成"

    def test_analyze_what_to_do_with_past_steps(self, mock_config):
        """测试包含过去步骤的分析"""
        with patch("execute_replan_utils.config", mock_config), patch(
            "execute_replan_utils._execute_script_subprocess"
        ) as mock_execute, patch("os.path.exists", return_value=False):

            mock_execute.return_value = "分析完成"

            from execute_replan_utils import analyze_what_to_do

            result = analyze_what_to_do(
                count=1, past_steps_content="已完成步骤1", plan="继续执行步骤2"
            )

            assert mock_execute.called

    def test_analyze_what_to_do_with_opinion(self, mock_config):
        """测试包含审核意见的分析"""
        with patch("execute_replan_utils.config", mock_config), patch(
            "execute_replan_utils._execute_script_subprocess"
        ) as mock_execute, patch("os.path.exists") as mock_exists, patch(
            "os.path.abspath", return_value="/path/to/opinion.md"
        ):

            def exists_side_effect(path):
                return "opinion" in path

            mock_exists.side_effect = exists_side_effect
            mock_execute.return_value = "分析完成"

            from execute_replan_utils import analyze_what_to_do

            result = analyze_what_to_do(count=1, past_steps_content="", plan="")

            assert mock_execute.called

    def test_analyze_what_to_do_windows_execute_path(self, mock_config):
        """测试 Windows 下使用 EXECUTE_PATH"""
        mock_config["MOCK"] = False
        mock_config["EXECUTE_PATH"] = "execute-agent.bat"

        with patch("execute_replan_utils.platform.system", return_value="Windows"), patch(
            "execute_replan_utils.config", mock_config
        ), patch("execute_replan_utils._execute_script_subprocess") as mock_execute, patch(
            "execute_replan_utils.tempfile.NamedTemporaryFile"
        ) as mock_temp, patch(
            "os.path.exists", return_value=False
        ):

            mock_temp.return_value.__enter__.return_value.name = "/tmp/test.prompt"
            mock_execute.return_value = "分析完成"

            from execute_replan_utils import analyze_what_to_do

            result = analyze_what_to_do(count=0, past_steps_content="", plan="")

            assert mock_execute.called
