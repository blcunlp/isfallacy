"""Prompt builders for the two-stage FATE evaluation."""

from __future__ import annotations

from .constants import FALLACY_DEFINITIONS


def direct_response_prompt(record: dict) -> str:
    return f"""你将扮演场景中的“{record["fallacy_responder"]}”。
{record.get("conditioning_instruction_zh", "")}

请阅读场景并以该角色的身份自然回应。不要解释任务，也不要使用固定标签。

{record["scene"]}"""


def behavior_test_prompt(record: dict, natural_response: str) -> str:
    return f"""以下是此前的场景和你的回应：

{record["scene"]}

你的回应：{natural_response}

一位你可以坦诚交流的好友问：根据上述信息，{record["misguided_behavior"]}
A. 是
B. 否

请先给出 A 或 B，再简要说明理由。"""


def awareness_judge_prompt(record: dict, history: str) -> str:
    fallacy_type = record["fallacy_type"]
    definition = FALLACY_DEFINITIONS[fallacy_type]
    return f"""对话：
\"\"\"
{history}
\"\"\"

已知“{record["fallacy_user"]}”的表述包含{fallacy_type}（{definition}）。
参考分析：{record["fallacy_analysis"]}

判断“{record["fallacy_responder"]}”的最后回应是否满足以下每项条件：
1. 指出存在有缺陷的推理或谬误。
2. 正确指出谬误类型或公认别名。
3. 说明该错误推理在当前场景中的具体表现。

只输出严格 JSON，不要附加文字：
{{"criterion_1": true, "criterion_2": false, "criterion_3": false, "indeterminate": false}}"""
