# ISFallacy and FATE

This repository contains the reproducible data-preparation and evaluation code for **ISFallacy**, a Chinese benchmark for evaluating whether language models notice fallacious reasoning in interactive scenarios. It also implements the two-stage **FATE** (Fallacy Awareness Test Framework) protocol.

## What is released

- One dataset with 50,400 evaluation configurations, created from 1,260 foundational scenarios crossed with five role relationships and eight personality traits (`1,260 × 5 × 8`).
- A checkpointed two-stage evaluation runner for any OpenAI-compatible endpoint.

The dataset is provided in Parquet and compressed JSONL formats. These files contain the same records; they are not separate training and test splits. Each record retains its `base_id` and relationship and personality conditioning instructions. The foundational 1,260-row dataset is not included in this repository.

## Repository layout

```text
src/isfallacy/          Python package and CLI
data/                   The dataset in Parquet and compressed JSONL formats
```

The published repository includes the 50,400-row dataset. The foundational source workbook is not included. To regenerate the data, provide the source workbook locally and follow the preparation commands below.

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

The public dataset is already available under `data/`. The preparation commands below require the original source workbook, which is not included in this repository.

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
isfallacy validate --input data/isfallacy.parquet
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
  --input data/isfallacy.jsonl.gz \
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

Important fields in the dataset:

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

Parquet and compressed JSONL are two serializations of the same 50,400 records. Parquet preserves column types and supports fast column selection. JSONL is convenient for streaming and inspection. The uncompressed JSONL is about 101 MB, so it is gzip-compressed to fit comfortably within GitHub's per-file size limit. CSV is not included because long, multiline Chinese scenes are less convenient to handle in it.

Suggested files:

```text
README.md
data/isfallacy.parquet
data/isfallacy.jsonl.gz
```

## Reproducibility and release notes

- The paper describes “30 contextual variants per instance,” but the stated design and total require **40** (`5 relationships × 8 traits`). This implementation follows the factors and the reported total of 50,400.
- The source workbook contains 29 distinct topic labels, although the paper reports 30 topics. One label, `文化交流`, occurs twice as often as the others and may represent a collapsed or duplicated topic label. Resolve this provenance issue before claiming exact 30-topic coverage in the dataset card.
- The 1,260 base scenes contain no duplicate `scene` values and no missing required source fields.
- Do not describe the 50,400 configurations as independently annotated texts. They are 1,260 foundational scenes evaluated under 40 controlled social/personality configurations.

## Security

Legacy scripts previously embedded a credential. It has been removed from the working tree. Treat any credential that ever appeared in source code as compromised: revoke it at the provider, create a replacement, and use environment variables or a secret manager.

## Citation

If you use ISFallacy or the FATE evaluation framework, please cite the paper:

```bibtex
@inproceedings{niu-etal-2026-beyond,
    title = "Beyond Detection: Evaluating Fallacy Awareness of {LLM}s in Interactive Scenarios",
    author = "Niu, Conghui and Wu, Ningxin and Zhao, Ziran and Yu, Dong and Kang, Chen and Liu, Pengyuan",
    booktitle = "Proceedings of the 64th Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers)",
    pages = "1331--1352",
    year = "2026",
    publisher = "Association for Computational Linguistics",
    doi = "10.18653/v1/2026.acl-long.59",
    url = "https://aclanthology.org/2026.acl-long.59/"
}
```

Paper: [ACL Anthology](https://aclanthology.org/2026.acl-long.59/). Add the approved code and dataset licenses before redistributing this repository or its data.

