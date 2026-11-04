"""Dataset checks that fail loudly on release-blocking problems."""

from __future__ import annotations

import pandas as pd

from .constants import PERSONALITIES, RELATIONSHIPS


def validate_base(frame: pd.DataFrame) -> dict:
    counts = frame["fallacy_type"].value_counts().to_dict()
    report = {
        "rows": len(frame),
        "duplicate_scenes": int(frame["scene"].duplicated().sum()),
        "fallacy_counts": counts,
        "interaction_counts": frame["social_interaction_type"].value_counts().to_dict(),
        "topic_count": int(frame["topic"].nunique()),
    }
    if report["duplicate_scenes"]:
        raise ValueError(f"Duplicate base scenes: {report['duplicate_scenes']}")
    return report


def validate_expanded(frame: pd.DataFrame, base_count: int | None = None) -> dict:
    expected = (base_count or frame["base_id"].nunique()) * len(RELATIONSHIPS) * len(PERSONALITIES)
    report = {
        "rows": len(frame),
        "expected_rows": expected,
        "unique_ids": int(frame["id"].nunique()),
        "base_count": int(frame["base_id"].nunique()),
        "relationship_count": int(frame["role_relationship"].nunique()),
        "personality_count": int(frame["personality_trait"].nunique()),
    }
    if len(frame) != expected or report["unique_ids"] != expected:
        raise ValueError(f"Invalid factorial expansion: {report}")
    return report
