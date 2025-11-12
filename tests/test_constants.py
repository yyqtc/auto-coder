"""
测试 constants.py 模块
"""
import pytest
from constants import (
    CODE_EXTENSIONS,
    REQUIREMENT_FAIL_MESSAGE,
    REQUIREMENT_READ_FAIL_MESSAGE,
    UNKNOWN_ERROR_MESSAGE,
    DEVELOPMENT_LOG_NOT_EXISTS,
)


class TestCodeExtensions:
    """测试代码扩展名常量"""

    def test_code_extensions_is_list(self):
        """测试 CODE_EXTENSIONS 是列表类型"""
        assert isinstance(CODE_EXTENSIONS, list)

    def test_code_extensions_not_empty(self):
        """测试 CODE_EXTENSIONS 不为空"""
        assert len(CODE_EXTENSIONS) > 0

    def test_common_extensions_present(self):
        """测试常见扩展名存在"""
        common_extensions = [".py", ".js", ".ts", ".java", ".cpp", ".c"]
        for ext in common_extensions:
            assert ext in CODE_EXTENSIONS, f"{ext} 应该在 CODE_EXTENSIONS 中"

    def test_all_extensions_start_with_dot(self):
        """测试所有扩展名都以点开头"""
        for ext in CODE_EXTENSIONS:
            assert ext.startswith("."), f"{ext} 应该以点开头"

    def test_no_duplicates(self):
        """测试没有重复的扩展名"""
        assert len(CODE_EXTENSIONS) == len(set(CODE_EXTENSIONS))


class TestErrorMessages:
    """测试错误消息常量"""

    def test_requirement_fail_message(self):
        """测试需求分析失败消息"""
        assert isinstance(REQUIREMENT_FAIL_MESSAGE, str)
        assert REQUIREMENT_FAIL_MESSAGE == "需求分析失败！"

    def test_requirement_read_fail_message(self):
        """测试需求读取失败消息"""
        assert isinstance(REQUIREMENT_READ_FAIL_MESSAGE, str)
        assert REQUIREMENT_READ_FAIL_MESSAGE == "需求读取失败！"

    def test_unknown_error_message(self):
        """测试未知错误消息"""
        assert isinstance(UNKNOWN_ERROR_MESSAGE, str)
        assert UNKNOWN_ERROR_MESSAGE == "未知错误！"

    def test_development_log_not_exists(self):
        """测试开发日志不存在消息"""
        assert isinstance(DEVELOPMENT_LOG_NOT_EXISTS, str)
        assert DEVELOPMENT_LOG_NOT_EXISTS == "读取开发日志失败！"

    def test_all_messages_are_strings(self):
        """测试所有消息都是字符串类型"""
        messages = [
            REQUIREMENT_FAIL_MESSAGE,
            REQUIREMENT_READ_FAIL_MESSAGE,
            UNKNOWN_ERROR_MESSAGE,
            DEVELOPMENT_LOG_NOT_EXISTS,
        ]
        for msg in messages:
            assert isinstance(msg, str)
            assert len(msg) > 0

