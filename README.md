# ISFallacy and FATE

This repository contains the reproducible data-preparation and evaluation code for **ISFallacy**, a Chinese benchmark for evaluating whether language models notice fallacious reasoning in interactive scenarios. It also implements the two-stage **FATE** (Fallacy Awareness Test Framework) protocol.

## What is released

- `expanded`: 50,400 evaluation configurations created from every base scenario with five role relationships and eight personality traits (`1,260 × 5 × 8`).
- A checkpointed two-stage evaluation runner for any OpenAI-compatible endpoint.

The expanded release combines every foundational scenario with the complete relationship and personality grid. Each expanded record retains its `base_id` and conditioning instructions. The foundational dataset is not included in this repository.

## Repository layout

```text
src/isfallacy/          Python package and CLI
tests/                  Unit tests
data/expanded/          Published 50,400-row evaluation configurations
```

The published repository includes the expanded dataset. The 1,260-row base workbook is not included. To regenerate the expansion from the paper's source data, provide the authorized source workbook locally and follow the preparation commands below.

## Installation

Python 3.10 or later is required.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e .
```

For development:

```bash
python -m pip install -e '.[dev]'
pytest
```

## Prepare or validate the dataset

The public expanded dataset is already available under `data/expanded/`. The preparation commands below require the original source workbook, which is not included in this repository.

Normalize the source workbook into the public schema:

```bash
isfallacy prepare \
  --input dataset_model.xlsx \
  --sheet 总 \
  --output data/processed/isfallacy_base.parquet
```

Create all 50,400 conditioned configurations:

```bash
isfallacy expand \
  --input dataset_model.xlsx \
  --sheet 总 \
  --output data/processed/isfallacy_expanded.parquet
```

Create the JSONL companion file by changing the output suffix:

```bash
isfallacy expand \
  --input dataset_model.xlsx \
  --output data/processed/isfallacy_expanded.jsonl
```

Validate a release file:

```bash
isfallacy validate --input data/processed/isfallacy_expanded.parquet
```

## Run FATE

Set credentials in the environment. Never commit `.env` or an API key.

```bash
export OPENAI_API_KEY='...'
export OPENAI_BASE_URL='https://api.openai.com/v1'
```

Run a small smoke test first:

```bash
isfallacy run \
  --input data/expanded/isfallacy_expanded.jsonl.gz \
  --output outputs/smoke.jsonl \
  --target-model TARGET_MODEL \
  --judge-model JUDGE_MODEL \
  --limit 10
```

Remove `--limit` for a full run. The runner appends one JSON object after each completed record and skips IDs already present in the output, so rerunning the same command resumes from the checkpoint.

For a local vLLM server, point `OPENAI_BASE_URL` at its OpenAI-compatible endpoint, commonly `http://localhost:8000/v1`.

## Two-stage protocol

1. **Direct response:** the target model responds naturally as the fallacy responder. The judge checks three awareness criteria: existence, type, and contextual mechanism.
2. **Behavior test:** only if stage 1 is unaware and determinate, the target answers the binary misguided-behavior question and explains its choice. The judge applies the same criteria to the full history.

A response is aware if any of the three criteria is true. Raw judge output is retained for auditability.

## Data schema

Important fields in the expanded split:

| Field | Meaning |
| --- | --- |
| `id` | Unique conditioned-record ID |
| `base_id` | ID of the foundational scenario |
| `scene` | Original Chinese scene and dialogue |
| `fallacy_type` | One of six annotated fallacy types |
| `fallacy_analysis` | Scene-specific fallacy explanation |
| `fallacy_user` | Character who uses the fallacy |
| `fallacy_responder` | Character played by the evaluated model |
| `misguided_behavior` | Binary behavior tested at stage 2 |
| `role_relationship` | One of five relationship conditions |
| `personality_trait` | One of eight personality conditions |
| `conditioning_instruction_zh` | Runtime relationship and personality instruction |
| `base_fingerprint` | SHA-256 fingerprint for provenance checks |

## Recommended Hugging Face files

Use Parquet as the canonical format because it preserves types, compresses repeated long text well, supports fast column selection, and works with the Hugging Face dataset viewer. Also publish `jsonl.gz` for transparent streaming and debugging. Avoid CSV as the primary format because scenes contain long, multiline Chinese text and commas; CSV is larger and more fragile across tools. In the generated release, expanded Parquet is under 1 MB while uncompressed expanded JSONL is about 100 MB; gzip reduces the JSONL to about 2.2 MB.

Suggested files:

```text
README.md
data/base/test-00000-of-00001.parquet
data/expanded/test-00000-of-00001.parquet
data/expanded/isfallacy_expanded.jsonl.gz
```

## Reproducibility and release notes

- The paper describes “30 contextual variants per instance,” but the stated design and total require **40** (`5 relationships × 8 traits`). This implementation follows the factors and the reported total of 50,400.
- The source workbook contains 29 distinct topic labels, although the paper reports 30 topics. One label, `文化交流`, occurs twice as often as the others and may represent a collapsed or duplicated topic label. Resolve this provenance issue before claiming exact 30-topic coverage in the dataset card.
- The 1,260 base scenes contain no duplicate `scene` values and no missing required source fields.
- Do not describe the conditioned split as 50,400 independently annotated texts. Describe it as 1,260 foundational scenes evaluated under 40 controlled social/personality configurations.

## Security

Legacy scripts previously embedded a credential. It has been removed from the working tree. Treat any credential that ever appeared in source code as compromised: revoke it at the provider, create a replacement, and use environment variables or a secret manager.

## License and citation

Add the dataset license, code license, paper citation, author list, and repository URLs before public release. Do not publish until the authors have confirmed that the selected licenses cover the generated data and code dependencies.

