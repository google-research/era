# ERA Notebooks

This directory contains Jupyter notebooks that demonstrate ERA
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


