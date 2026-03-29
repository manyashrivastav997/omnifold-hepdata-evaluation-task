# GSoC 2026 Project Proposal
## Publication of OmniFold Weights – Standardizing ML-based Unfolding Results
**Duration:** 175 hours | **Organization:** CERN-HSF

**Manya Shrivastav** | SRM University, Andhra Pradesh
📧 ma7754011460@outlook.com | 🐙 [manyashrivastav997](https://github.com/manyashrivastav997) | 💼 [LinkedIn](https://linkedin.com/in/manya-121237377)

---

## Abstract

OmniFold is a machine learning–based unfolding method that produces per-event weights rather than traditional histograms, enabling flexible, high-dimensional particle physics analyses. Despite its advantages, there is no standardized format for storing and publishing these outputs — a gap that directly undermines reproducibility, reuse, and cross-experiment collaboration.

This project proposes a practical, modular framework to close that gap: a well-defined metadata schema, efficient HDF5-based storage, a lightweight Python API, and a validation pipeline — culminating in a smooth integration pathway with HEPData. The goal is not just technical correctness, but a system that fits naturally into existing HEP workflows and gets adopted by the community.

---

## 1. Introduction

Unfolding is a fundamental step in high-energy physics (HEP) analyses, where detector-level measurements are translated back to underlying particle-level distributions. Traditional binned methods — Iterative Bayesian Unfolding, SVD, TUnfold — are well-established but constrain analyses to fixed histogram bins and limit the dimensionality of what can be measured.

OmniFold [Andreassen et al., 2020] changes this: by using neural networks to iteratively reweight Monte Carlo simulation to match data, it produces per-event weights that carry the full information of the unfolded distribution. This enables unbinned, multidimensional measurements that were previously impossible.

However, this expressiveness comes with a practical problem. Unlike traditional unfolding outputs — which map naturally onto existing HEPData formats — OmniFold weights are raw, per-event numerical arrays with no standardized schema, no metadata conventions, and no defined reuse interface. The result is that every analysis reinvents its own storage format, making results difficult to verify, impossible to reuse programmatically, and incompatible with HEPData submission.

This project directly addresses this gap.

---

## 2. Problem Statement

Through hands-on analysis of three real OmniFold datasets during the evaluation task, I identified the following concrete problems:

**Structural inconsistency across datasets:**

| Dataset | Events | Columns | Weight Columns |
|---|---|---|---|
| `multifold.h5` | 418,014 | 200 | 175 |
| `multifold_sherpa.h5` | 326,430 | 51 | 27 |
| `multifold_nonDY.h5` | 433,397 | 26 | 2 |

The datasets share 22 common physics observables but differ dramatically in weight structure — with no metadata explaining why, or how the datasets relate to each other.

**Missing normalization metadata:** Integrated luminosity, generator cross-sections, and the relationship between `weight_mc` and `weights_nominal` are entirely absent. Without this, converting weights to physical cross-sections is impossible without the original analysis code.

**Precision inconsistencies:** `weights_nominal` is stored as `float32` in `multifold.h5` and `multifold_nonDY.h5`, but as `float64` in `multifold_sherpa.h5` — suggesting different production pipelines with no coordination.

**Naming convention ambiguity:** The mixing of `weight_` and `weights_` prefixes, undocumented ensemble weight semantics, and ambiguous names like `weights_muEffReco` create real risk of misinterpretation in automated processing.

**Undocumented OmniFold training configuration:** Neural network architecture, hyperparameters, number of iterations, random seeds, and training features are entirely absent — making it impossible to reproduce or validate the unfolding.

**No HEPData integration pathway:** OmniFold per-event weights have no established route to HEPData submission, which is where the broader community accesses published results.

These are not hypothetical concerns — they are documented in detail in my [gap analysis](https://github.com/manyashrivastav997/omnifold-hepdata-evaluation-task/blob/main/gap_analysis.md).

---

## 3. Proposed Approach

The proposed solution is a modular, four-component system built around one principle: **standardization that actually gets used**.

```
OmniFold Output → Standardized HDF5 Storage → Validation → HEPData → Reuse
```

### 3.1 Metadata Schema

A structured YAML/JSON schema describing OmniFold outputs in a self-contained, machine-readable way.

**Why YAML/JSON over embedded HDF5 attributes alone?**
HDF5 attributes are limited in size and not easily version-controlled. A sidecar YAML file is human-readable, diff-able, and composable with existing HEP tooling like `hepdata-lib`.

**Schema structure (required vs optional fields):**

```yaml
# Required
dataset:
  origin: "MC"                        # MC | data | pseudodata
  generator: "Pythia8"
  generator_version: "8.306"
  experiment: "ATLAS"
  production_date: "2025-01-15"

normalization:
  integrated_luminosity_fb: 140.1
  cross_section_pb: 1837.0
  filter_efficiency: 0.45
  weight_mc_definition: "generator cross-section weight"
  weights_nominal_definition: "weight_mc × pileup × lepton_eff × luminosity"

observables:
  pT_ll: { units: "GeV", level: "particle", description: "Dilepton transverse momentum" }
  eta_l1: { units: "dimensionless", coordinate_convention: "ATLAS standard" }

weights:
  nominal: "weights_nominal"
  ensemble: { columns: "weights_ensemble_0:99", method: "bootstrap", n_samples: 100 }
  systematics:
    pileup: "weights_pileup"
    muon_eff_reco: "weights_muEffReco"

omnifold_config:
  iterations: 5
  architecture: "3 layers, [256, 128, 64], ReLU"
  optimizer: "Adam"
  learning_rate: 0.001
  random_seed: 42
  training_features: ["pT_ll", "eta_l1", "phi_l1", "y_ll"]

# Optional
event_selection:
  pT_l1_min_GeV: 27
  eta_l1_max: 2.5
  trigger: "HLT_mu26_ivarmedium"
```

### 3.2 Storage Format

HDF5 will be the primary storage format.

**Why HDF5 over alternatives?**

| Format | Pros | Cons | Verdict |
|---|---|---|---|
| HDF5 | Hierarchical, compression, fast columnar access, h5py support | Complex | ✅ Best fit |
| Parquet | Fast, columnar, pandas native | No hierarchy, poor for metadata | ❌ |
| ROOT | HEP standard | Heavy dependency, Python friction | ❌ for new tools |
| CSV | Human-readable | Huge files, no metadata, no compression | ❌ |

HDF5 supports chunked storage and compression (gzip/lz4), which is essential for datasets with 400k+ events and 200 columns. It also stores metadata attributes alongside data, keeping everything in one file.

**Proposed HDF5 structure:**

```
omnifold_output.h5
├── /dataset/
│   ├── observables/          # physics columns (float32)
│   └── metadata/             # Ntracks etc. (int32)
├── /weights/
│   ├── nominal               # weights_nominal (float64)
│   ├── mc_base               # weight_mc (float32)
│   ├── ensemble/             # ensemble_000 ... ensemble_099
│   ├── bootstrap_mc/         # bootstrap_mc_00 ... bootstrap_mc_24
│   ├── bootstrap_data/       # bootstrap_data_00 ... bootstrap_data_24
│   └── systematics/          # pileup, muon_eff, theory_pdf, ...
└── /omnifold_config/         # training metadata as HDF5 attributes
```

Key design decisions:
- Consistent `float64` for all weight columns (precision for uncertainty propagation)
- Consistent naming: `weights_` prefix everywhere, no mixing with `weight_`
- Systematic weights grouped under `/weights/systematics/` for programmatic access
- OmniFold training config stored as HDF5 group attributes

### 3.3 Python API

A lightweight, dependency-minimal Python package (`omnifold_io`) for loading, applying, and validating OmniFold weights.

**Design principles:**
- Simple, flat API surface — researchers shouldn't need to understand HDF5 internals
- Integration with NumPy and Awkward Arrays (standard in CMS/ATLAS Python workflows)
- Explicit error messages that guide users toward correct usage

```python
from omnifold_io import load_weights, apply_weights, compute_observable

# Load
weights = load_weights("omnifold_output.h5")
print(weights.metadata)          # normalization, generator, etc.
print(weights.systematic_sources)  # lists available systematics

# Apply to new observable
pT_ll = events["pT_ll"]
hist, edges = apply_weights(pT_ll, weights.nominal, bins=30, range=(0, 500))

# With uncertainty from bootstrap
hist, edges, unc = apply_weights(
    pT_ll, weights.nominal,
    bootstrap=weights.bootstrap_mc,
    return_uncertainty=True
)

# Systematic variation
hist_up = apply_weights(pT_ll, weights.systematics["pileup"])
```

**Internal structure:**
- `OmniFoldWeights` dataclass: holds all weight arrays + metadata
- `load_weights()`: reads HDF5, validates schema, returns dataclass
- `apply_weights()`: wraps `np.histogram` with weight support + bootstrap uncertainty
- `validate()`: runs all checks before publishing

### 3.4 Validation Pipeline

Before publication, outputs pass through automated checks:

**Closure test:** Apply OmniFold weights to the same dataset used for training — the reweighted distribution should match the target. A chi-squared test flags failures.

**Normalization check:** `sum(weights_nominal)` should equal expected luminosity × cross-section × filter_efficiency within tolerance.

**Stability across iterations:** Compare ensemble spread across the last N iterations — if it's still decreasing significantly, the unfolding hasn't converged.

**Schema completeness:** All required YAML fields are present and have correct types (using `jsonschema` validation).

**Weight sanity:** Check for NaN, Inf, and unexpectedly large weights that may indicate numerical issues.

```python
from omnifold_io import validate

report = validate("omnifold_output.h5", "metadata.yaml")
report.summary()
# ✓ Schema complete (all 24 required fields present)
# ✓ Normalization check passed (within 0.3%)
# ✓ Closure test passed (χ²/ndf = 1.12)
# ✗ WARNING: 3 ensemble iterations show >5% spread — check convergence
```

### 3.5 HEPData Integration

HEPData accepts submissions in a specific YAML format via `hepdata-lib`. The integration module will:
- Convert the standardized HDF5 + metadata YAML into a HEPData-compatible submission package
- Generate weighted histograms in HEPData table format for key observables
- Include systematic uncertainty bands derived from ensemble weights
- Validate submission format before upload using `hepdata-lib`'s built-in checker

### 3.6 Challenges and Mitigation

**Large file sizes (400k+ events × 200 columns):** HDF5 chunking with gzip compression keeps files manageable without sacrificing read speed.

**Schema flexibility vs. strictness:** Required/optional field separation allows schema adoption by analyses with incomplete metadata, without breaking validation.

**HEPData format evolution:** I will test against the current HEPData API early (Week 11) and maintain compatibility with `hepdata-lib` versioning.

**Backward compatibility:** The schema will include a `schema_version` field from day one, so future changes can be handled gracefully.

---

## 4. Deliverables

1. **Metadata schema** — YAML/JSON schema with required/optional field separation, `jsonschema` validator, and documentation of all fields with examples
2. **Standardized HDF5 storage module** — consistent structure, naming conventions, compression, and sidecar metadata support
3. **`omnifold_io` Python package** — load, apply, validate API with NumPy/Awkward Arrays integration
4. **Validation pipeline** — closure tests, normalization checks, stability checks, schema completeness
5. **HEPData integration** — conversion from standardized format to HEPData submission package
6. **End-to-end example notebook** — demonstrating full workflow from raw OmniFold output to HEPData submission using realistic datasets
7. **Documentation** — API reference, usage guide, schema specification, contributor notes

---

## 5. Timeline

| Week | Focus | Concrete Deliverable |
|---|---|---|
| Community Bonding | Setup + deep dive into HEPData YAML format and `hepdata-lib` API; finalize schema field list with mentor input | Environment ready; schema v0.1 draft |
| 2–3 | Schema design + HDF5 structure | `metadata.yaml` schema with `jsonschema` validator; HDF5 group/dataset structure finalized |
| 4–5 | HDF5 storage implementation | `write_omnifold_h5()` function handling all weight types; unit tests for 3 dataset types; compression benchmarks |
| 6 | Reader utilities | `load_weights()` function; all 3 evaluation task datasets readable with new API |
| **7 — Midterm** | **Midterm evaluation** | **Working: schema validator + HDF5 reader/writer + basic API. Demo on real datasets.** |
| 8–9 | `omnifold_io` API + uncertainty | `apply_weights()`, `compute_observable()`, bootstrap uncertainty estimation; integration tests |
| 10 | Validation pipeline | Closure test, normalization check, stability check, schema completeness check |
| 11 | HEPData integration | `hepdata-lib` conversion; HEPData submission YAML generated from standardized output |
| 12 | End-to-end pipeline + example notebook | Full workflow demo: raw OmniFold → standardized → validated → HEPData |
| 13 | Documentation + final evaluation | API docs, usage guide, schema spec; final testing and submission |

---

## 6. Expected Results

By the end of the project:

- A standardized, reusable format for publishing OmniFold outputs that addresses the specific gaps identified in the evaluation task
- A Python package (`omnifold_io`) that researchers can install and immediately use with existing datasets
- A validation pipeline that catches common errors before publication
- A defined integration pathway between OmniFold outputs and HEPData
- An end-to-end example notebook demonstrating the full workflow on real datasets
- Documentation sufficient for community adoption and future contributors

---

## 7. Why Me

I am a first-year B.Tech student in Computer Science (AI & ML) at SRM University, with a strong interest in applying machine learning to real-world and scientific problems. I came into this project with no prior background in high-energy physics — just curiosity and a willingness to dig in.

During the evaluation task, I analyzed three real OmniFold datasets and found something that stuck with me: without proper metadata, even an experienced physicist cannot reproduce results, combine datasets correctly, or propagate uncertainties — the data essentially becomes a black box. That realization is what this entire project is trying to fix, and working through it firsthand made me genuinely invested in solving it.
My evaluation task repository can be found here:  
https://github.com/manyashrivastav997/omnifold-hepdata-evaluation-task

Concretely, what I did: I mapped the structural differences across multifold.h5 (200 columns), multifold_sherpa.h5 (51 columns), and multifold_nonDY.h5 (26 columns), identified weight naming inconsistencies, precision mismatches, and missing normalization metadata, designed a unified schema to address these gaps, and implemented a weighted_histogram module with uncertainty estimation and validation tests.

My technical stack for this project :Python, NumPy, h5py, pandas — I have used hands-on, not just in theory. I'm also building my ML foundations through PyTorch-based projects in parallel.

I am eager to learn, consistent in my commitment, and genuinely motivated by the intersection of machine learning and physics that this project represents.

---

## 8. Post GSoC

The 175-hour timeline covers the core framework. Beyond GSoC, I plan to:

- Add support for **Awkward Arrays** as a first-class input/output format (standard in coffea-based CMS workflows)
- Extend the schema to handle **multi-dimensional unfolded distributions** (not just per-event weights)
- Work with the HEP community to get the schema adopted as a community standard — similar to how `hepdata-lib` became the de facto HEPData submission tool
- Stay active as a maintainer and respond to issues from early adopters

This is the kind of infrastructure project that compounds in value as more analyses use it — and I want to be around to see that happen.

---

## 9. References

1. Andreassen, A. et al. — *OmniFold: A Method to Simultaneously Unfold All Observables* (2020). [arXiv:1911.09107](https://arxiv.org/abs/1911.09107)
2. Andreassen, A. & Nachman, B. — *Neural Networks for Full Phase-space Reweighting and Parameter Extraction* (2020). [arXiv:1907.08209](https://arxiv.org/abs/1907.08209)
3. HEPData Repository — [hepdata.net](https://www.hepdata.net)
4. `hepdata-lib` — Python library for HEPData submissions. [github.com/HEPData/hepdata-lib](https://github.com/HEPData/hepdata-lib)
5. HDF5 Documentation — [hdfgroup.org](https://www.hdfgroup.org)
6. Scikit-HEP Ecosystem — [scikit-hep.org](https://scikit-hep.org)
7. Cranmer, K. et al. — *Publishing statistical models in HEP* (2021). [arXiv:2109.04981](https://arxiv.org/abs/2109.04981)
8. ATLAS Collaboration — *Multidimensional unfolding with OmniFold* — internal note referenced in evaluation task datasets
