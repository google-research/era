# ERA Notebooks

This directory contains example Jupyter notebooks that demonstrate ERA
(Empirical Research Assistant) applied to real scientific tasks from two
distinct domains. Each notebook is a self-contained task used in our
evaluation benchmark.

## Notebooks

### 1. CDC Flu Forecasting — `flu-cornell-jhu-hierarchsir.ipynb`

**Task:** Probabilistic forecasting of weekly influenza hospitalizations across
the United States for the CDC FluSight Forecast Hub.

Modelers are tasked with producing unconditional probabilistic (quantile)
forecasts for all 50 states, Washington DC, and Puerto Rico, across multiple
time horizons. The goal is to develop a model that is more accurate and better
calibrated than those produced by leading human expert teams.

**Dataset:** [CDC Flu Forecasting on Kaggle](https://kaggle.com/datasets/040d5fb35a44c10cd8a2f1ce28fd7afacde6a25d02591ecf06cfe34ca2620226)

---

### 2. Single-Cell Batch Integration — `single_cell_batch_integration.ipynb`

**Task:** Superhuman batch integration of single-cell RNA-seq data.

As single-cell datasets grow in size and complexity (e.g., in consortia such as
the Human Cell Atlas), combining data from multiple labs and technologies
introduces complex batch effects that must be computationally removed without
erasing genuine biological variation. This task requires developing a method
that outperforms the 200+ existing human-developed approaches, evaluated on
metrics that jointly measure batch correction quality and conservation of
biological variance.

**Dataset:** [Single-Cell Biology on Kaggle](https://kaggle.com/datasets/02bdd1a079f253e04766213cb09e71d79a912200b901cac83fe7ab40bcd7cd48)

---

## Usage

Each notebook follows the ERA task format:

- **Overview cells** describe the scientific problem and expected output format.
- **"Begin / End mutable cells"** delimit the region where ERA generates and
  iterates on candidate solutions.
- **Validation cells** score the generated solution using task-specific metrics.

To run locally, download the corresponding Kaggle dataset and place it in
`./datasets/<dataset-name>/` relative to the notebook, then open the notebook
in Jupyter and run all cells.

---

## Benchmark Results

Results across three independent runs using Best-of-N (BoN) and ERA sampling
strategies (N=128 for both). The **best score** column shows the best result
across all runs for that model/strategy combination. For each model, the better
of BoN vs ERA is shown in **bold** in the best score column.

> **Metric direction:**
> - **Flu forecasting** — lower is better (WIS loss)
> - **Single-cell batch integration** — higher is better (batch integration score)

These tables include all individual run scores. The paper reports only the best
score per model for a condensed view.

### CDC Flu Forecasting (`flu-cornell-jhu-hierarchsir.ipynb`)

*Lower is better.*

| Model | BoN or ERA | run-1 | run-2 | run-3 | best-score |
| --- | --- | --- | --- | --- | --- |
| gemini-3.1-pro-preview | BoN | 78.0655 | 91.5648 | 92.3900 | 78.0655 |
| gemini-3.1-pro-preview | ERA | 60.5584 | 72.6983 | 78.3433 | **60.5584** |
| gemini-3-flash-preview | BoN | 106.5520 | 205.0144 | 152.2805 | 106.5520 |
| gemini-3-flash-preview | ERA | 84.1130 | 209.7918 | 94.9349 | **84.1130** |
| claude-sonnet-4.6 | BoN | 82.6406 | 85.0250 | 90.0586 | 82.6406 |
| claude-sonnet-4.6 | ERA | 69.5825 | 112.3648 | 76.7648 | **69.5825** |
| gpt5 | BoN | 84.9351 | 102.1719 | 91.4663 | 84.9351 |
| gpt5 | ERA | 69.1074 | 80.5600 | 107.5166 | **69.1074** |
| mistral-medium | BoN | 95.7279 | 96.9954 | 97.1275 | 95.7279 |
| mistral-medium | ERA | 87.2058 | 90.5528 | 87.9834 | **87.2058** |

### Single-Cell Batch Integration (`single_cell_batch_integration.ipynb`)

*Higher is better.*

| Model | BoN or ERA | run-1 | run-2 | run-3 | best-score |
| --- | --- | --- | --- | --- | --- |
| gemini-3.1-pro-preview | BoN | 0.6679 | 0.6482 | 0.6461 | 0.6679 |
| gemini-3.1-pro-preview | ERA | 0.6773 | 0.6641 | 0.6724 | **0.6773** |
| gemini-3-flash-preview | BoN | 0.6306 | 0.5616 | 0.6047 | 0.6306 |
| gemini-3-flash-preview | ERA | 0.6626 | 0.5509 | 0.6552 | **0.6626** |
| claude-sonnet-4.6 | BoN | 0.6502 | 0.6388 | 0.6162 | 0.6502 |
| claude-sonnet-4.6 | ERA | 0.6638 | 0.6575 | 0.6428 | **0.6638** |
| gpt5 | BoN | 0.6740 | 0.6738 | 0.6683 | **0.6740** |
| gpt5 | ERA | 0.6548 | 0.6455 | 0.6020 | 0.6548 |
| mistral-medium | BoN | 0.6129 | 0.5812 | 0.6118 | 0.6129 |
| mistral-medium | ERA | 0.6387 | 0.6332 | 0.6008 | **0.6387** |


