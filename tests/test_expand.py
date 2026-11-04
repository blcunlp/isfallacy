import pandas as pd

from isfallacy.expand import expand_factorial, prepare_base
from isfallacy.validate import validate_expanded


def test_factorial_expansion_has_40_variants_per_base():
    base = pd.DataFrame(
        [
            {
                "social_interaction_type": "Exchange",
                "topic": "测试",
                "fallacy_type": "诉诸情感",
                "scene": "测试场景",
                "fallacy_analysis": "测试分析",
                "fallacy_user": "甲",
                "fallacy_responder": "乙",
                "misguided_behavior": "你是否同意？",
            }
        ]
    )
    expanded = expand_factorial(prepare_base(base))
    report = validate_expanded(expanded, 1)
    assert report["rows"] == 40
    assert report["unique_ids"] == 40
