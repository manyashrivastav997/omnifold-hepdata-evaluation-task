# GSoC 2026 CERN HSF Proposal and Evaluation Task  
## Publication of Omnifold Weights

## About
This repository contains my work for the CERN HSF GSoC 2026 project focused on standardizing, storing, and publishing OmniFold weights to improve reproducibility, interoperability, and reuse in High Energy Physics workflows.

---

## Proposal
The complete proposal is included in this repository:

- PROPOSAL_CERN HSF_Publication of Omnifold weights.md

---

## Evaluation Task
This repository also includes my solution to the OmniFold publication tools evaluation task.

The work focuses on analyzing three HDF5 physics datasets and identifying inconsistencies in structure, metadata, and weight representation. Based on this analysis, a unified schema is proposed to enable consistent storage and easier reuse across datasets.

---

## Repository Contents

### gap_analysis.md
Technical comparison of three datasets, including:
- Dataset structure
- Observable categories
- Weight types
- Challenges in cross-dataset reuse

### metadata.yaml
Structured metadata describing:
- Observables
- Weight definitions
- Data types
- Metadata fields  
Designed for programmatic access and validation.

### schema_design.md
Documentation of a unified schema, including:
- Design principles
- Required and optional components
- Validation guidelines

### weighted_histogram.py
Reusable Python utility for computing weighted histograms, featuring:
- Input validation and error handling
- Support for custom bins and normalization
- Statistical uncertainty calculation
- Optional visualization using Matplotlib
- Built-in test cases

---

## Dataset Summary

The analysis covers three datasets:

- **multifold.h5** — 418,014 rows, 200 columns  
- **multifold_sherpa.h5** — 326,430 rows, 51 columns  
- **multifold_nonDY.h5** — 433,397 rows, 26 columns  

These datasets include physics observables, event weights, and metadata fields with varying structures.

---

## Key Highlights

- Comparative analysis of multiple OmniFold datasets  
- Identification of inconsistencies in weights, observables, and metadata  
- Proposal of a standardized schema for interoperability  
- Implementation of a reusable weighted histogram utility  

---

## Tech Stack

Python, NumPy, HDF5, h5py, YAML, JSON

---

## Future Work

This work is extended in my GSoC proposal to include:

- Standardized HDF5 storage format  
- Metadata validation system using schema definitions  
- Python API for applying weights and computing observables  
- Integration with HEPData for real-world data publication  

---

## How to Run

To test the histogram implementation:

```bash
python weighted_histogram.py
