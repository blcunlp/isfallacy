"""Checkpointed implementation of the two-stage FATE protocol."""

from __future__ import annotations

import json
from pathlib import Path

from tqdm import tqdm

from .io import read_jsonl
from .prompts import awareness_judge_prompt, behavior_test_prompt, direct_response_prompt
from .provider import OpenAICompatibleProvider


def _parse_judgment(text: str) -> dict:
    start, end = text.find("{"), text.rfind("}")
    if start < 0 or end < start:
        raise ValueError(f"Judge did not return JSON: {text[:200]}")
    result = json.loads(text[start : end + 1])
    required = {"criterion_1", "criterion_2", "criterion_3", "indeterminate"}
    if set(result) != required or any(not isinstance(result[key], bool) for key in required):
        raise ValueError(f"Invalid judgment schema: {result}")
    result["aware"] = any(result[key] for key in ("criterion_1", "criterion_2", "criterion_3"))
    return result


def _completed_ids(path: Path) -> set[str]:
    if not path.exists():
        return set()
    return {row["id"] for row in read_jsonl(path)}


def run_fate(
    input_path: str,
    output_path: str,
    target: OpenAICompatibleProvider,
    judge: OpenAICompatibleProvider,
    limit: int | None = None,
) -> None:
    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    done = _completed_ids(output)
    records = (record for record in read_jsonl(input_path) if record["id"] not in done)
    if limit is not None:
        from itertools import islice

        records = islice(records, limit)

    with output.open("a", encoding="utf-8") as handle:
        for record in tqdm(records, desc="FATE evaluation"):
            natural_response = target.generate(direct_response_prompt(record), temperature=0.7)
            stage1_history = f"{record['scene']}\n{record['fallacy_responder']}：{natural_response}"
            stage1_raw = judge.generate(awareness_judge_prompt(record, stage1_history))
            stage1 = _parse_judgment(stage1_raw)

            behavior_response = None
            stage2 = None
            stage2_raw = None
            if not stage1["aware"] and not stage1["indeterminate"]:
                behavior_response = target.generate(
                    behavior_test_prompt(record, natural_response), temperature=0.7
                )
                stage2_history = f"{stage1_history}\n好友提问后的回应：{behavior_response}"
                stage2_raw = judge.generate(awareness_judge_prompt(record, stage2_history))
                stage2 = _parse_judgment(stage2_raw)

            result = {
                "id": record["id"],
                "base_id": record["base_id"],
                "target_model": target.model,
                "judge_model": judge.model,
                "natural_response": natural_response,
                "stage1_judgment": stage1,
                "stage1_judge_raw": stage1_raw,
                "behavior_response": behavior_response,
                "stage2_judgment": stage2,
                "stage2_judge_raw": stage2_raw,
                "final_aware": stage1["aware"] or bool(stage2 and stage2["aware"]),
                "indeterminate": stage1["indeterminate"]
                or bool(stage2 and stage2["indeterminate"]),
            }
            handle.write(json.dumps(result, ensure_ascii=False) + "\n")
            handle.flush()
