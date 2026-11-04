"""Command-line entry point."""

from __future__ import annotations

import argparse
import json

import pandas as pd

from .expand import expand_factorial, prepare_base
from .io import load_table, write_table
from .pipeline import run_fate
from .provider import OpenAICompatibleProvider
from .validate import validate_base, validate_expanded


def _prepare(args: argparse.Namespace) -> None:
    base = prepare_base(load_table(args.input, sheet_name=args.sheet))
    print(json.dumps(validate_base(base), ensure_ascii=False, indent=2))
    write_table(base, args.output)


def _expand(args: argparse.Namespace) -> None:
    base = prepare_base(load_table(args.input, sheet_name=args.sheet))
    expanded = expand_factorial(base)
    print(json.dumps(validate_expanded(expanded, len(base)), ensure_ascii=False, indent=2))
    write_table(expanded, args.output)


def _validate(args: argparse.Namespace) -> None:
    frame = (
        pd.read_parquet(args.input)
        if args.input.endswith(".parquet")
        else pd.read_json(args.input, lines=True)
    )
    report = validate_expanded(frame) if "id" in frame.columns else validate_base(frame)
    print(json.dumps(report, ensure_ascii=False, indent=2))


def _run(args: argparse.Namespace) -> None:
    target = OpenAICompatibleProvider(args.target_model, args.base_url)
    judge = OpenAICompatibleProvider(args.judge_model, args.judge_base_url or args.base_url)
    run_fate(args.input, args.output, target, judge, args.limit)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="isfallacy")
    subparsers = parser.add_subparsers(dest="command", required=True)

    for name, handler, help_text in (
        ("prepare", _prepare, "Normalize the 1,260-row base dataset"),
        ("expand", _expand, "Create the 5 x 8 conditioned dataset"),
    ):
        command = subparsers.add_parser(name, help=help_text)
        command.add_argument("--input", required=True)
        command.add_argument("--output", required=True)
        command.add_argument("--sheet", default="总")
        command.set_defaults(func=handler)

    validate = subparsers.add_parser("validate", help="Validate a prepared release file")
    validate.add_argument("--input", required=True)
    validate.set_defaults(func=_validate)

    run = subparsers.add_parser("run", help="Run checkpointed two-stage FATE evaluation")
    run.add_argument("--input", required=True)
    run.add_argument("--output", required=True)
    run.add_argument("--target-model", required=True)
    run.add_argument("--judge-model", required=True)
    run.add_argument("--base-url")
    run.add_argument("--judge-base-url")
    run.add_argument("--limit", type=int)
    run.set_defaults(func=_run)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
