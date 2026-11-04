"""Deterministic 5 x 8 factorial expansion of the 1,260 base scenarios."""

from __future__ import annotations

import pandas as pd

from .constants import PERSONALITIES, RELATIONSHIPS


def prepare_base(frame: pd.DataFrame) -> pd.DataFrame:
    result = frame.copy().reset_index(drop=True)
    result.insert(0, "base_id", [f"isfallacy-base-{i:06d}" for i in range(1, len(result) + 1)])
    result["language"] = "zh"
    result["source_row"] = range(2, len(result) + 2)
    result["split"] = "test"
    result["record_kind"] = "foundational_scenario"
    return result


def expand_factorial(base: pd.DataFrame) -> pd.DataFrame:
    if "base_id" not in base.columns:
        base = prepare_base(base)

    conditions = pd.DataFrame(
        [
            {
                "role_relationship": relationship,
                "relationship_instruction_zh": relationship_instruction,
                "personality_trait": personality,
                "personality_instruction_zh": personality_instruction,
            }
            for relationship, relationship_instruction in RELATIONSHIPS.items()
            for personality, personality_instruction in PERSONALITIES.items()
        ]
    )
    expanded = base.merge(conditions, how="cross")
    expanded.insert(
        0,
        "id",
        expanded.apply(
            lambda row: (
                f"{row.base_id}__rel-{row.role_relationship}__trait-{row.personality_trait}"
            ),
            axis=1,
        ),
    )
    expanded["conditioning_instruction_zh"] = (
        expanded["relationship_instruction_zh"] + "\n" + expanded["personality_instruction_zh"]
    )
    expanded["record_kind"] = "conditioned_variant"
    return expanded
