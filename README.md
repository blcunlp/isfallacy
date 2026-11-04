# Beyond Detection: Evaluating Fallacy Awareness of LLMs in Interactive Scenarios

## Abstract

Large language models can identify fallacies when asked directly, yet may fail to recognize or resist them in natural interactions. **ISFallacy** is a Chinese benchmark for evaluating fallacy awareness across six fallacy types, five social interaction settings, five relationship conditions, and eight personality traits. **FATE** evaluates models in two stages: a natural response to an interactive scenario, followed by a behavior question when the first response does not show awareness. The framework assesses whether responses identify the fallacy, classify its type, or explain how its faulty reasoning appears in context.

This repository contains the ISFallacy dataset and code for running the two-stage FATE evaluation.

## What is released

- The complete ISFallacy dataset with 50,400 records across six fallacy types, five social interaction settings, five role relationships, and eight personality traits.
- A checkpointed two-stage evaluation runner for any OpenAI-compatible endpoint.

The dataset is provided in Parquet and compressed JSONL formats. These files contain the same complete dataset; they are not separate training and test splits. Each record includes relationship and personality conditioning information.

## Repository layout

```text
src/isfallacy/          Python package and CLI
data/                   The dataset in Parquet and compressed JSONL formats
```

The repository contains the complete 50,400-row dataset.

## Installation

Python 3.10 or later is required.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e .
```

## Validate the dataset

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
| `base_id` | Identifier linking records from the same scenario group |
| `scene` | Original Chinese scene and dialogue |
| `fallacy_type` | One of six annotated fallacy types |
| `fallacy_analysis` | Scene-specific fallacy explanation |
| `fallacy_user` | Character who uses the fallacy |
| `fallacy_responder` | Character played by the evaluated model |
| `misguided_behavior` | Binary behavior tested at stage 2 |
| `role_relationship` | One of five relationship conditions |
| `personality_trait` | One of eight personality conditions |
| `conditioning_instruction_zh` | Runtime relationship and personality instruction |

## Data formats

Parquet and compressed JSONL are two serializations of the same 50,400 records. Parquet preserves column types and supports fast column selection. JSONL is convenient for streaming and inspection. The uncompressed JSONL is about 101 MB, so it is gzip-compressed to fit comfortably within GitHub's per-file size limit.

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

