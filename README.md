# OmniFold HEPData Evaluation Task

This repository contains my solution for the OmniFold publication tools evaluation task.  
The work focuses on analyzing three HDF5 physics datasets and proposing a unified schema for improved compatibility and reuse.

## Repository Contents

### gap_analysis.md
Technical analysis comparing the three datasets.  
Includes dataset structure, observable categories, weight types, and challenges for cross-dataset reuse.

### metadata.yaml
Structured metadata describing dataset contents, including observables, weights, metadata fields, and data types.  
Designed to support automated validation and programmatic access.

### schema_design.md
Documentation of a unified schema for the datasets, including design principles, required and optional components, and validation guidelines.

### weighted_histogram.py
Reusable Python function for computing weighted histograms.  
Features include:
- Input validation and error handling
- Support for custom bins and density normalization
- Optional visualization using Matplotlib
- Statistical uncertainty calculation
- Built-in test cases

## Dataset Summary

The analysis covers three datasets:

- **multifold.h5** – 418,014 rows, 200 columns  
- **multifold_sherpa.h5** – 326,430 rows, 51 columns  
- **multifold_nonDY.h5** – 433,397 rows, 26 columns  

Columns include physics observables, event weights, and metadata fields.

## How to Run

To test the histogram implementation:

```bash
python weighted_histogram.py
