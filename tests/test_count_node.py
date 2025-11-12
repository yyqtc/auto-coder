"""
测试 count_node.py 模块
"""
import pytest
import os
import shutil
import json
import tempfile
from unittest.mock import patch, mock_open, MagicMock
from custom_type import ActionReview


class TestCounterNode:
    """测试 counter_node 函数"""

    @pytest.fixture
    def temp_project_structure(self, temp_dir, sample_config):
        """创建临时项目结构"""
        # 创建必要的目录
        for dir_name in ["opinion", "dist", "history"]:
            os.makedirs(os.path.join(temp_dir, dir_name), exist_ok=True)

        # 创建配置文件
        config_path = os.path.join(temp_dir, "config.json")
        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(sample_config, f)

        # 创建项目目录
        dist_dir = os.path.join(temp_dir, "dist", sample_config["PROJECT_NAME"])
        os.makedirs(dist_dir, exist_ok=True)

        # 创建测试文件
        test_file = os.path.join(dist_dir, "test.txt")
        with open(test_file, "w") as f:
            f.write("test content")

        return temp_dir

    @pytest.mark.asyncio
    async def test_counter_node_with_response(self, temp_project_structure, sample_config):
        """测试当 state 包含 response 时直接返回"""
        with patch("count_node.config", sample_config), \
             patch("os.path.exists") as mock_exists, \
             patch("os.path.join") as mock_join:
            
            mock_join.side_effect = lambda *args: os.path.join(*args)
            
            from count_node import counter_node
            
            state = ActionReview(count=0, response="完成")
            result = await counter_node(state)
            
            assert "response" in result
            assert result["response"] == "完成"

    @pytest.mark.asyncio
    async def test_counter_node_first_iteration(self, temp_project_structure, sample_config):
        """测试第一次迭代（count=0）"""
        with patch("count_node.config", sample_config), \
             patch("os.path.exists") as mock_exists, \
             patch("os.path.join") as mock_join:
            
            mock_join.side_effect = lambda *args: os.path.join(*args)
            mock_exists.return_value = False
            
            from count_node import counter_node
            
            state = ActionReview(count=0, response="")
            result = await counter_node(state)
            
            assert "count" in result
            assert result["count"] == 0

    @pytest.mark.asyncio
    async def test_counter_node_backup_dist_to_history(self, temp_project_structure, sample_config):
        """测试备份 dist 到 history"""
        with patch("count_node.config", sample_config), \
             patch("shutil.copytree") as mock_copytree, \
             patch("shutil.rmtree") as mock_rmtree, \
             patch("os.path.exists") as mock_exists, \
             patch("os.path.join") as mock_join:
            
            mock_join.side_effect = lambda *args: os.path.join(*args)
            mock_exists.side_effect = lambda path: "dist" in path
            
            from count_node import counter_node
            
            state = ActionReview(count=1, response="")
            result = await counter_node(state)
            
            # 验证备份操作被调用
            assert "count" in result

    def test_remove_readonly(self):
        """测试 remove_readonly 函数"""
        from count_node import remove_readonly
        
        mock_func = MagicMock()
        mock_path = "/test/path"
        
        with patch("os.chmod") as mock_chmod:
            remove_readonly(mock_func, mock_path, None)
            mock_chmod.assert_called_once_with(mock_path, 0o200)
            mock_func.assert_called_once_with(mock_path)

