"""
测试 custom_type.py 和 execute_custom_type.py 模块
"""
import pytest
from pydantic import ValidationError
from custom_type import ActionReview, Action, Response, Act
from execute_custom_type import PlanExecute, Plan, Act as ExecuteAct


class TestActionReview:
    """测试 ActionReview TypedDict"""

    def test_action_review_is_dict(self):
        """测试 ActionReview 可以像字典一样使用"""
        state = ActionReview(count=0, response="")
        assert isinstance(state, dict)
        assert state["count"] == 0
        assert state["response"] == ""

    def test_action_review_with_values(self):
        """测试 ActionReview 可以包含值"""
        state = ActionReview(count=5, response="测试响应")
        assert state["count"] == 5
        assert state["response"] == "测试响应"


class TestAction:
    """测试 Action 模型"""

    def test_action_creation(self):
        """测试创建 Action 实例"""
        action = Action(count=10)
        assert action.count == 10

    def test_action_default_count(self):
        """测试 Action 默认 count 值"""
        action = Action()
        assert hasattr(action, "count")


class TestResponse:
    """测试 Response 模型"""

    def test_response_creation(self):
        """测试创建 Response 实例"""
        response = Response(response="成功")
        assert response.response == "成功"

    def test_response_required_field(self):
        """测试 Response 的 response 字段是必需的"""
        with pytest.raises(ValidationError):
            Response()


class TestAct:
    """测试 Act 模型"""

    def test_act_with_action(self):
        """测试 Act 包含 Action"""
        action = Action(count=5)
        act = Act(action=action)
        assert isinstance(act.action, Action)
        assert act.action.count == 5

    def test_act_with_response(self):
        """测试 Act 包含 Response"""
        response = Response(response="完成")
        act = Act(action=response)
        assert isinstance(act.action, Response)
        assert act.action.response == "完成"


class TestPlanExecute:
    """测试 PlanExecute TypedDict"""

    def test_plan_execute_creation(self):
        """测试创建 PlanExecute"""
        state = PlanExecute(
            input="测试输入",
            plan=["步骤1", "步骤2"],
            past_steps=[],
            response="",
            mapping_table={},
        )
        assert state["input"] == "测试输入"
        assert len(state["plan"]) == 2
        assert isinstance(state["past_steps"], list)
        assert isinstance(state["mapping_table"], dict)


class TestPlan:
    """测试 Plan 模型"""

    def test_plan_creation(self):
        """测试创建 Plan 实例"""
        plan = Plan(steps=["步骤1", "步骤2", "步骤3"])
        assert len(plan.steps) == 3
        assert plan.steps[0] == "步骤1"

    def test_plan_empty_steps(self):
        """测试 Plan 可以有空步骤列表"""
        plan = Plan(steps=[])
        assert len(plan.steps) == 0


class TestExecuteAct:
    """测试执行工作流的 Act 模型"""

    def test_execute_act_with_plan(self):
        """测试 ExecuteAct 包含 Plan"""
        plan = Plan(steps=["步骤1"])
        act = ExecuteAct(action=plan)
        assert isinstance(act.action, Plan)

    def test_execute_act_with_response(self):
        """测试 ExecuteAct 包含 Response"""
        response = Response(response="完成")
        act = ExecuteAct(action=response)
        assert isinstance(act.action, Response)

