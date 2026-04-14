# Reproducibility Guide

## Runtime assumptions

- Python 3.11+
- provider credentials exported in `.env`
- optional heavy dependencies installed when corresponding tools are used

## Determinism and variability

- Carbon, Open-Meteo, and Tavily tools are deterministic for a given upstream response.
- GPT-5 backed tools remain non-deterministic unless you pin provider-side parameters and prompts.
- Earth Engine composites depend on the selected time window and cloud filtering.

## Artifact logging

Satellite and analysis tools write intermediate artifacts into `GCA_ARTIFACTS_DIR`. This makes it possible to:

- inspect exact index arrays,
- reproduce plotted maps,
- re-run change analysis without calling Earth Engine again.

## Regression testing

Use the benchmark harness and the tests together:

```bash
pytest
python -m gulf_climate_agent.cli.benchmark --cases src/gulf_climate_agent/benchmarks/cases/sample_cases.jsonl
```

## Recommended research workflow

1. freeze `.env` and provider versions,
2. capture benchmark case files under version control,
3. store generated artifacts for each run,
4. log agent traces,
5. compare tool-selection and argument-level regressions before prompt changes.
