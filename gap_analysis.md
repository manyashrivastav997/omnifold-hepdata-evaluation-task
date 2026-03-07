# Dataset Gap Analysis

## Executive Summary

This analysis examines three HDF5 datasets from an OmniFold unfolding analysis containing dilepton and track jet events: multifold.h5 (418,014 events, 200 columns), multifold_sherpa.h5 (326,430 events, 51 columns), and multifold_nonDY.h5 (433,397 events, 26 columns). The datasets exhibit significant structural differences in weight coverage and systematic uncertainty treatment, reflecting different intended roles in the analysis workflow.

**Column Classification:** All three datasets share 22 common physics observables describing dilepton kinematics (transverse momentum, pseudorapidity, azimuthal angle, rapidity) and track jet properties (kinematics and N-subjettiness variables). The primary dataset (multifold.h5) contains 23 observables including a unique `target_dd` column, likely serving as the OmniFold training target. Weight structures vary dramatically: multifold.h5 includes 175 weight columns comprising base weights (`weight_mc`, `weights_nominal`), 100 ensemble variations for systematic uncertainties, 23 individual systematic uncertainty sources (detector, theory, and background systematics), and 50 bootstrap samples (25 MC, 25 data) for statistical uncertainty propagation. In contrast, multifold_sherpa.h5 contains only 27 weights (base weights plus 25 MC bootstrap samples), while multifold_nonDY.h5 provides minimal coverage with just 2 base weight columns. All datasets include identical metadata columns (`Ntracks_trackj1`, `Ntracks_trackj2`) recording track multiplicities. This hierarchical weight structure suggests multifold.h5 serves as the primary analysis dataset with full uncertainty treatment, multifold_sherpa.h5 as an alternative generator sample for closure tests, and multifold_nonDY.h5 as a background process sample.

**Critical Missing Information for Weight Reuse:** The datasets lack essential metadata required for correct weight interpretation and application. Normalization information is completely absent: integrated luminosity, generator cross-sections, filter efficiencies, and the relationship between `weight_mc` and `weights_nominal` are not documented, preventing conversion of weights to physical cross-sections or proper dataset combination. Observable definitions are unspecified—units (GeV, radians, or degrees), coordinate system conventions (phi range, eta definition), jet clustering algorithms, track selection criteria, and N-subjettiness calculation parameters are not provided, making correct interpretation of numerical values impossible. OmniFold training configuration is entirely undocumented: neural network architecture, hyperparameters (learning rate, batch size, optimizer), number of iterations, random seeds, training feature list, and feature normalization procedures are absent, preventing reproduction of the unfolding procedure. Systematic uncertainty definitions are missing: the 100 ensemble weights are not mapped to specific systematic sources, correlation structures are unknown, and individual systematic magnitudes are not specified, making proper uncertainty propagation impossible. Bootstrap generation procedures lack documentation of random seeds, resampling method (with or without replacement), and cross-dataset index alignment, preventing correct statistical uncertainty estimation when combining datasets. Event selection criteria including kinematic cuts, trigger requirements, lepton identification criteria, and event quality selections are not documented, making it impossible to determine the phase space coverage or apply consistent selections across datasets.

**Standardization Challenges:** The absence of community-wide standards for OmniFold outputs creates fundamental barriers to cross-experiment collaboration and reproducibility. Different Monte Carlo generators (Pythia, Sherpa, Powheg) employ incompatible weight conventions and cross-section normalizations, yet generator identification and convention documentation are absent from these files. Experiment-specific differences in coordinate systems, object reconstruction algorithms, and systematic uncertainty categorizations prevent direct comparison between ATLAS, CMS, and other experiments without comprehensive metadata. Weight naming conventions lack standardization—the mixing of `weight_` and `weights_` prefixes, ambiguous systematic names like `weights_muEffReco`, and undocumented ensemble weight semantics complicate automated processing and increase misinterpretation risk. OmniFold training variability across implementations (TensorFlow vs PyTorch), hyperparameter choices, and iteration counts produces incompatible results, yet no standard exists for documenting training configurations. Numerical precision inconsistencies (float32 vs float64) across datasets suggest different production pipelines without coordination, and precision requirements are not documented. The HEP community lacks a standardized metadata schema for machine learning-based unfolding outputs—no required fields, no validation tools, no schema versioning, and no interoperability standards exist. These standardization gaps mean each analysis group invents ad-hoc conventions, making dataset reuse, cross-analysis validation, and long-term preservation extremely difficult. Without access to original analysts or analysis code, these datasets cannot be correctly interpreted, combined, or used to reproduce published results, fundamentally limiting their scientific value and violating core principles of reproducible research.

## Dataset Overview

| Dataset | Rows | Columns | Observables | Weights | Metadata |
|---------|------|---------|-------------|---------|----------|
| multifold.h5 | 418,014 | 200 | 23 | 175 | 2 |
| multifold_sherpa.h5 | 326,430 | 51 | 22 | 27 | 2 |
| multifold_nonDY.h5 | 433,397 | 26 | 22 | 2 | 2 |

## Dataset Role Interpretation

The structural differences across the three datasets provide strong evidence for their intended roles in the analysis workflow, though explicit documentation is absent:

**multifold.h5 - Primary Analysis Dataset:**
This dataset serves as the primary analysis output with complete uncertainty treatment. The presence of the `target_dd` column indicates it was used for OmniFold training, making it the central dataset for unfolding detector-level distributions to particle-level. The comprehensive weight structure—100 ensemble variations, 23 individual systematic sources, and 50 bootstrap samples (25 MC + 25 data)—demonstrates full systematic and statistical uncertainty propagation. The ensemble weights likely encode correlated systematic variations across multiple uncertainty sources, enabling proper uncertainty propagation to final physics results. The dual bootstrap structure (MC and data) suggests this dataset combines simulation and collision data, with bootstrap resampling applied to both components for statistical uncertainty estimation. The 175 total weight columns indicate this dataset is intended for final physics measurements where complete uncertainty quantification is required.

**multifold_sherpa.h5 - Alternative Generator Sample:**
This dataset represents an alternative Monte Carlo generator sample, likely produced with Sherpa for closure testing and generator systematic studies. The absence of the `target_dd` column indicates it was not used for OmniFold training but rather for validation. The weight structure—base weights plus 25 MC bootstrap samples—provides statistical uncertainty estimation but lacks systematic uncertainties. This structure is consistent with a closure test sample where the goal is to verify that the OmniFold procedure can correctly unfold a known truth distribution. The absence of data bootstrap weights confirms this is pure simulation. The 51 total columns (compared to 200 in multifold.h5) reflect the minimal weight structure needed for generator comparison studies. This dataset would typically be used to assess generator modeling uncertainties by comparing Sherpa predictions to the primary generator (likely Pythia) used in multifold.h5.

**multifold_nonDY.h5 - Background Process Sample:**
This dataset represents background processes (non-Drell-Yan events) for background subtraction in the dilepton analysis. The minimal weight structure—only `weight_mc` and `weights_nominal`—indicates this background contribution is either small or its uncertainties are absorbed into other systematic sources in the primary dataset. The absence of bootstrap weights suggests statistical uncertainties on the background are negligible compared to other uncertainty sources. The absence of the `target_dd` column confirms this dataset was not used in OmniFold training. The 26 total columns represent the bare minimum needed for background estimation: observables plus base weights. This dataset would be subtracted from collision data (or added to simulation) before or during the unfolding procedure, with its normalization likely determined from control regions or theoretical calculations documented elsewhere.

These role interpretations are inferred from structural evidence but remain assumptions without explicit metadata. Documenting dataset roles explicitly would prevent misuse and clarify the intended analysis workflow.

## Column Classification Summary

The datasets contain six distinct categories of columns, each serving a different purpose in the analysis:

| Category | Examples | Description | Present in Files |
|----------|----------|-------------|------------------|
| **Observable** | `pT_ll`, `eta_l1`, `phi_l1`, `m_trackj1` | Physics measurable quantities (kinematics, jet substructure) | All files (22 common) |
| **Base Weight** | `weight_mc`, `weights_nominal` | Fundamental event weights for cross-section normalization | All files |
| **Ensemble Weight** | `weights_ensemble_0` ... `weights_ensemble_99` | Systematic uncertainty variations (100 variations) | multifold.h5 only |
| **Bootstrap Weight** | `weights_bootstrap_mc_0` ... `weights_bootstrap_mc_24` | Statistical uncertainty propagation via resampling | multifold.h5, multifold_sherpa.h5 |
| **Systematic Weight** | `weights_pileup`, `weights_muEffReco`, `weights_theoryPDF` | Individual systematic uncertainty sources (23 sources) | multifold.h5 only |
| **Metadata** | `Ntracks_trackj1`, `Ntracks_trackj2` | Auxiliary event information (track multiplicities) | All files |
| **Training Target** | `target_dd` | OmniFold training target variable | multifold.h5 only |

This classification reveals the hierarchical structure of uncertainty treatment: multifold.h5 contains the complete uncertainty framework, multifold_sherpa.h5 includes only statistical uncertainties, and multifold_nonDY.h5 provides minimal weights for background estimation.

## Column Classification

### Physics Observables

All three datasets share 22 common observables describing dilepton and track jet kinematics. Based on naming conventions, these appear to represent:

**Dilepton system (8 observables):**
- `pT_ll`, `pT_l1`, `pT_l2`: Likely transverse momentum (units not specified in file)
- `eta_l1`, `eta_l2`: Likely pseudorapidity (dimensionless)
- `phi_l1`, `phi_l2`: Likely azimuthal angle (units not specified)
- `y_ll`: Likely rapidity (dimensionless)

**Track jet 1 and 2 (14 observables):**
- `pT_trackj1/2`, `y_trackj1/2`, `phi_trackj1/2`, `m_trackj1/2`: Kinematic properties
- `tau1_trackj1/2`, `tau2_trackj1/2`, `tau3_trackj1/2`: Likely N-subjettiness variables

**Unique to multifold.h5:**
- `target_dd`: Purpose not documented in file; likely related to OmniFold training target

The exact definitions, units, and coordinate conventions are not specified in the HDF5 files and would require external documentation.

### Weight Columns

**multifold.h5 (175 weights):**
- `weight_mc`, `weights_nominal`: Base weights (relationship between them not documented)
- `weights_ensemble_0` through `weights_ensemble_99`: 100 ensemble variations (generation method not specified)
- `weights_dd`: Purpose not documented
- Systematic categories inferred from naming: pileup, muon efficiency/calibration, tracking, theory, background, luminosity
- Bootstrap samples: 25 MC + 25 data (resampling procedure not documented)

**multifold_sherpa.h5 (27 weights):**
- `weight_mc`, `weights_nominal`: Base weights
- 25 bootstrap MC samples (no data bootstrap)

**multifold_nonDY.h5 (2 weights):**
- `weight_mc`, `weights_nominal`: Base weights only

The semantic meaning of weight columns is inferred from naming conventions but not explicitly documented in the files.

### Metadata Columns

All datasets contain:
- `Ntracks_trackj1`, `Ntracks_trackj2`: Integer track counts

## File Structure and Storage Format

The three datasets are stored as HDF5 files with pandas DataFrame structure. Each file organizes columns into blocks based on data type:

**multifold.h5 block structure:**
- Block 0: 148 columns (float32) - observables and most weights
- Block 1: 50 columns (float64) - bootstrap weights
- Block 2: 2 columns (int32) - metadata

**multifold_sherpa.h5 block structure:**
- Block 0: 23 columns (float32) - observables and weight_mc
- Block 1: 26 columns (float64) - weights_nominal and bootstrap weights
- Block 2: 2 columns (int32) - metadata

**multifold_nonDY.h5 block structure:**
- Block 0: 24 columns (float32) - observables and weights
- Block 1: 2 columns (int32) - metadata

This block structure reflects pandas' internal storage optimization, grouping columns by dtype. The variation in block organization across datasets indicates they were likely produced by different processing pipelines or at different times. This structural difference complicates direct block-level HDF5 operations and requires column-by-column access for compatibility.

The choice of float32 for observables provides sufficient precision (~7 decimal digits) for physics measurements, while float64 for bootstrap weights preserves precision during uncertainty propagation calculations. However, the inconsistent use of float64 for weights_nominal (float32 in multifold.h5 and multifold_nonDY.h5, but float64 in multifold_sherpa.h5) suggests inconsistent production standards.

## Structural Differences

### Missing Observables

The `target_dd` column appears only in multifold.h5. Without documentation, its role is unclear, but the naming suggests it may be a target variable for OmniFold training. The absence of this column in the other datasets suggests they serve different purposes in the analysis workflow, though the exact roles are not specified.

### Missing Weights

The three datasets have dramatically different weight structures:

- multifold_sherpa.h5 lacks all systematic uncertainty weights and ensemble variations present in multifold.h5
- multifold_nonDY.h5 contains only base weights with no uncertainty propagation

These differences suggest different intended uses, but without metadata describing dataset roles, users must infer the purpose from the weight structure alone.

### Data Type Inconsistencies

Observable columns consistently use `float32`, but weight precision varies:
- Bootstrap weights use `float64` in multifold.h5 and multifold_sherpa.h5
- Nominal weights use `float32` in multifold_nonDY.h5 but `float64` in multifold_sherpa.h5

This inconsistency suggests the datasets were produced by different pipelines or at different times.

## Missing Metadata Required for Reproducibility

The HDF5 files contain only numerical data without accompanying metadata. This creates significant barriers to reproducibility and reuse:

### OmniFold Training Configuration

The files do not document:
- Number of OmniFold iterations performed
- Neural network architecture (layers, nodes, activation functions)
- Training hyperparameters (learning rate, batch size, epochs, optimizer)
- Random seeds used for training and weight initialization
- Which observables were used as training features
- Whether observables were normalized or standardized before training
- Stopping criteria or convergence thresholds

Without this information, the OmniFold procedure cannot be reproduced. The `target_dd` column in multifold.h5 suggests OmniFold training occurred, but the training configuration is completely undocumented.

### Normalization and Scaling

Critical normalization information is missing:
- Integrated luminosity (required to convert event weights to cross-sections)
- Generator cross-sections for each process
- Filter efficiencies applied during event generation
- Whether `weights_nominal` includes luminosity normalization
- Relationship between `weight_mc` and `weights_nominal`

Without this metadata, combining datasets or comparing to theoretical predictions is not possible. Users cannot determine if weights represent absolute cross-sections, relative weights, or arbitrary normalizations.

### Observable Definitions

The files lack documentation of:
- Physical units (GeV, radians, etc.)
- Coordinate system conventions (e.g., phi range: [0, 2π] or [-π, π])
- Detector-level vs particle-level definitions
- Jet clustering algorithm and parameters (radius, pT threshold)
- Track selection criteria for track jets
- N-subjettiness calculation details (axes definition, beta parameter)

These ambiguities prevent correct interpretation of the numerical values. For example, without knowing if phi is in radians or degrees, angular calculations will be incorrect.

### Event Selection Criteria

The datasets do not document:
- Kinematic cuts applied (pT thresholds, eta acceptance)
- Trigger requirements
- Event quality criteria
- Dilepton selection (flavor, charge, isolation)
- How events with more than two jets were handled

Without this information, users cannot determine the phase space covered by the data or apply consistent selections across datasets.

### Bootstrap Generation Procedure

The bootstrap weight columns lack documentation of:
- Random seeds for each bootstrap sample
- Whether resampling was with or without replacement
- Whether bootstrap samples are independent across datasets
- How bootstrap indices align between MC and data samples

This prevents proper uncertainty propagation when combining datasets. Bootstrap sample 0 in one dataset may not correspond to the same random resampling in another dataset.

### Systematic Uncertainty Definitions

The systematic weight columns are named but not defined:
- Which specific systematic sources do ensemble weights cover?
- Are ensemble variations correlated or independent?
- What is the magnitude of each systematic variation?
- How were theory systematics (PDF, scale, αs) generated?
- What detector calibration uncertainties are included?

Without this information, users cannot assess which uncertainties are included or combine systematic uncertainties correctly.

## Reuse and Interoperability Challenges

### Weight Interpretation Ambiguity

The consistent naming convention (`weight_mc`, `weights_nominal`) across datasets suggests these weights have the same meaning, but this is not guaranteed. Each dataset may encode different corrections:
- Different generator cross-sections
- Different filter efficiencies
- Different detector acceptance corrections

Combining weighted histograms from different datasets without understanding the weight definitions will produce incorrect results.

### Inability to Reproduce OmniFold Training

The presence of `target_dd` and ensemble weights in multifold.h5 indicates OmniFold unfolding was performed, but the complete absence of training metadata makes reproduction impossible. Users cannot:
- Verify the unfolding procedure
- Retrain with different hyperparameters
- Apply the same unfolding to new data
- Understand what systematic uncertainties the ensemble captures

This fundamentally limits the scientific value of the dataset, as reproducibility is a core requirement of scientific analysis.

### Missing Correlation Information

The ensemble weights in multifold.h5 presumably encode correlations between systematic sources, but without documentation:
- Users cannot determine which systematics are correlated
- Combining with external systematic uncertainties may double-count correlations
- Propagating uncertainties to derived quantities requires assumptions about correlations

### Dataset Role Ambiguity

The intended purpose of each dataset is not documented. Based on structure, one might infer:
- multifold.h5: Primary analysis dataset with full uncertainties
- multifold_sherpa.h5: Alternative generator for closure tests
- multifold_nonDY.h5: Background process sample

However, these are assumptions. Without explicit role documentation, users may misuse datasets (e.g., treating background as signal, or using validation samples for training).

## Information Required for Correct Histogram Construction

Even the most basic analysis task—constructing a weighted histogram—requires information not present in these files:

**Observable binning:**
- Appropriate bin boundaries for each observable
- Whether bins should be uniform or variable width
- Recommended number of bins for each distribution
- Whether certain regions should be excluded (e.g., detector acceptance gaps)

**Weight application:**
- Which weight column to use for standard analysis (weight_mc or weights_nominal?)
- Whether weights should be normalized to unit sum or to luminosity
- How to handle negative weights (present in some MC generators)
- Whether weights represent cross-sections or arbitrary normalizations

**Uncertainty propagation:**
- How to combine bootstrap samples to compute statistical uncertainties
- Whether ensemble weights should be used for systematic uncertainties
- How to propagate uncertainties when combining multiple datasets
- Whether systematic uncertainties are symmetric or asymmetric

**Dataset combination:**
- How to combine signal and background (multifold.h5 + multifold_nonDY.h5)
- Whether datasets should be added or subtracted
- What relative normalization factors to apply
- How to handle overlapping phase space regions

Without this information, even experienced analysts must make arbitrary choices that may not match the original analysis intent. Different choices lead to different results, undermining reproducibility.

## Standardization Challenges Across Experiments

The lack of standardized metadata and schema conventions creates significant challenges for cross-experiment and cross-generator compatibility:

### Monte Carlo Generator Differences

Different generators (Pythia, Sherpa, Herwig, Powheg) produce events with different conventions:
- **Weight definitions vary:** Pythia and Sherpa use different cross-section normalizations and filter efficiency conventions
- **Observable naming inconsistencies:** Some generators use `pt` while others use `pT`; rapidity vs pseudorapidity conventions differ
- **Systematic uncertainty availability:** Theory systematics (PDF, scale variations) are generator-specific and not standardized

Without explicit documentation of which generator produced each dataset and what conventions it uses, combining datasets from different generators is error-prone. The presence of multifold_sherpa.h5 suggests generator comparison is intended, but the lack of generator metadata makes this comparison difficult to perform correctly.

### Cross-Experiment Compatibility

Different experiments (ATLAS, CMS, LHCb, future colliders) have different standards:
- **Coordinate system conventions:** ATLAS and CMS use different phi angle conventions and beam axis definitions
- **Object definitions:** Jet algorithms, lepton isolation criteria, and track selection vary between experiments
- **Systematic uncertainty categorization:** Each experiment has its own taxonomy for systematic sources
- **Data format standards:** No universal HDF5 schema exists for HEP analyses

A dataset produced for ATLAS cannot be directly compared to CMS results without understanding these differences. The current files provide no experiment identification, making cross-experiment studies impossible.

### OmniFold Training Pipeline Variations

Different OmniFold implementations and training procedures create incompatible outputs:
- **Framework differences:** TensorFlow vs PyTorch implementations may produce different results
- **Hyperparameter choices:** Learning rate, batch size, and network architecture significantly affect unfolding
- **Iteration count:** Different stopping criteria lead to different levels of unfolding
- **Feature selection:** Which observables are used for training affects the unfolding performance

Without documenting the OmniFold pipeline, users cannot determine if results from different analyses are comparable. The `target_dd` column suggests OmniFold was used, but the complete absence of training metadata prevents any validation or comparison.

### Weight Naming Convention Inconsistencies

Even within a single analysis, weight naming lacks standardization:
- **Inconsistent prefixes:** Some weights use `weight_` while others use `weights_`
- **Unclear semantics:** `weight_mc` vs `weights_nominal` relationship is not documented
- **Systematic naming ambiguity:** `weights_muEffReco` could mean muon reconstruction efficiency or muon efficiency reconstruction
- **No standard for ensemble weights:** The 100 ensemble variations have no documentation of what they represent

This lack of naming standards makes automated processing difficult and increases the risk of misinterpretation.

### Precision and Data Type Inconsistencies

The three datasets use inconsistent data types for similar quantities:
- **weights_nominal precision varies:** float32 in multifold.h5 and multifold_nonDY.h5, but float64 in multifold_sherpa.h5
- **No documented precision requirements:** Users cannot determine if float32 is sufficient or if float64 is required
- **Block structure differences:** Different dtype groupings complicate direct HDF5 operations

These inconsistencies suggest the datasets were produced by different pipelines or at different times, but without version control or production metadata, users cannot determine the cause or assess the impact on results.

### Lack of Universal Metadata Schema

The HEP community lacks a standardized metadata schema for analysis datasets:
- **No required fields:** Producers can omit critical information without violating any standard
- **No validation tools:** No automated checks ensure metadata completeness
- **No discovery mechanism:** Users cannot programmatically determine what metadata is available
- **No versioning:** Schema evolution is not tracked, making long-term preservation difficult

This absence of standards means each analysis group invents its own conventions, making cross-group collaboration and dataset reuse extremely difficult.

### Systematic Uncertainty Encoding Standards

Systematic uncertainties are encoded inconsistently across analyses:
- **No standard for correlation information:** Correlations between systematics are not documented
- **No standard for asymmetric uncertainties:** Up/down variations may not be symmetric
- **No standard for systematic categories:** Theory, experimental, and statistical uncertainties are not clearly separated
- **No standard for ensemble methods:** The relationship between ensemble weights and individual systematics is unclear

Without standardized encoding, combining systematic uncertainties from different sources or propagating them to derived quantities requires ad-hoc assumptions that may be incorrect.

These standardization challenges are not unique to these three datasets—they reflect systemic issues in how the HEP community shares analysis outputs. Addressing these challenges requires community-wide adoption of metadata standards and schema conventions.

## Physicist Reusability: What Cannot Be Done

The missing metadata creates concrete barriers that prevent physicists from performing standard analysis tasks:

### Cannot Reproduce OmniFold Training

A physicist attempting to reproduce the OmniFold unfolding cannot:
- **Recreate the neural network:** Architecture (number of layers, nodes per layer, activation functions) is not documented
- **Match training procedure:** Hyperparameters (learning rate, batch size, optimizer, number of epochs) are unknown
- **Reproduce random initialization:** Random seeds for weight initialization and data shuffling are not provided
- **Verify convergence:** Stopping criteria and convergence metrics are not specified
- **Validate feature preprocessing:** Whether observables were normalized, standardized, or transformed is unknown

Without this information, any attempt to reproduce the unfolding will produce different results. This violates the fundamental scientific principle of reproducibility.

### Cannot Correctly Normalize to Cross-Sections

A physicist attempting to compute cross-sections cannot:
- **Convert weights to absolute cross-sections:** Integrated luminosity is not provided
- **Account for filter efficiencies:** Generator-level filtering factors are not documented
- **Determine weight meaning:** Whether `weights_nominal` includes luminosity normalization is unknown
- **Compare to theory predictions:** Generator cross-sections are not provided for normalization checks
- **Combine signal and background:** Relative normalization between multifold.h5 and multifold_nonDY.h5 is not specified

Without normalization metadata, any cross-section measurement will have unknown and potentially large systematic uncertainties.

### Cannot Correctly Propagate Systematic Uncertainties

A physicist attempting to compute systematic uncertainties cannot:
- **Identify systematic sources:** The 100 ensemble weights are not mapped to specific systematic sources
- **Determine correlations:** Which systematics are correlated across observables is unknown
- **Avoid double-counting:** Combining ensemble weights with individual systematic weights may double-count uncertainties
- **Propagate to derived quantities:** Without correlation information, uncertainty propagation to ratios or differences is ambiguous
- **Assess completeness:** Whether all relevant systematic sources are included cannot be determined

Without systematic uncertainty metadata, any uncertainty estimate will be unreliable and potentially incorrect.

### Cannot Safely Combine Datasets

A physicist attempting to combine datasets (e.g., signal + background) cannot:
- **Determine compatibility:** Whether datasets cover the same phase space is unknown
- **Apply correct normalization:** Relative scale factors between datasets are not provided
- **Align bootstrap samples:** Whether bootstrap indices correspond across datasets is unknown
- **Handle systematic correlations:** Whether systematics are correlated between datasets is not documented
- **Verify event selection consistency:** Whether the same cuts were applied to all datasets is unknown

Without dataset relationship metadata, combining datasets may produce incorrect results with no indication of the error.

### Cannot Validate Physics Results

A physicist attempting to validate results cannot:
- **Check observable definitions:** Units and coordinate conventions are not specified, making validation against published results impossible
- **Verify event selection:** Kinematic cuts and trigger requirements are not documented
- **Compare to other experiments:** Experiment identification and detector acceptance are not provided
- **Assess systematic coverage:** Which systematic sources are included cannot be determined
- **Reproduce published plots:** Binning choices and normalization conventions are not specified

Without validation metadata, results cannot be independently verified, undermining confidence in the analysis.

These concrete limitations demonstrate that the missing metadata is not merely inconvenient—it fundamentally prevents physicists from performing reproducible, scientifically valid analyses with these datasets.

## Challenges in Standardizing Across Experiments and Analyses

The absence of standardized conventions for OmniFold outputs creates fundamental challenges for cross-experiment collaboration, multi-generator comparisons, and long-term dataset preservation. These challenges extend beyond the specific datasets examined here and reflect broader issues in how the high-energy physics community shares machine learning-based analysis results.

### Monte Carlo Generator Conventions and Weight Definitions

Different Monte Carlo event generators employ fundamentally different conventions for event weights and cross-section normalizations:

**Pythia conventions:** Pythia typically provides event weights that include the hard-process cross-section, parton shower corrections, and hadronization effects. The weight represents the differential cross-section for that specific event configuration. Filter efficiencies from generator-level cuts are often applied as separate scale factors.

**Sherpa conventions:** Sherpa uses a different weight structure where multi-parton matrix elements are merged with parton showers using the CKKW or MEPS@NLO schemes. Event weights include merging scale dependencies and may be negative due to NLO subtraction terms. The cross-section normalization differs from Pythia's approach.

**Powheg conventions:** Powheg generates events at NLO accuracy with positive-definite weights by construction, but the weight interpretation differs from both Pythia and Sherpa. The relationship between event weights and physical cross-sections depends on the specific Powheg process implementation.

The presence of both multifold.h5 (presumably Pythia-based) and multifold_sherpa.h5 in this analysis illustrates the challenge: without explicit documentation of generator conventions, users cannot correctly interpret or combine weights from different generators. The `weight_mc` column may represent fundamentally different quantities in each file, making direct comparison or combination invalid.

### Experiment-Specific Observable Definitions and Detector Conventions

Observable definitions vary significantly across experiments due to different detector geometries, reconstruction algorithms, and analysis conventions:

**Coordinate system differences:** ATLAS uses a right-handed coordinate system with the z-axis along the beam direction and phi measured from the x-axis. CMS uses a similar convention but with different sign conventions for certain quantities. LHCb uses a different coordinate system entirely due to its forward geometry. Without documenting which convention is used, observables like `phi_l1` and `eta_l1` cannot be correctly interpreted.

**Jet reconstruction differences:** ATLAS and CMS use different jet algorithms (anti-kt with different radius parameters), different particle flow algorithms, and different jet energy scale calibrations. Track jets, as used in these datasets, have experiment-specific definitions for track selection, vertex association, and jet clustering. The `pT_trackj1` observable cannot be compared across experiments without knowing the specific reconstruction procedure.

**Lepton identification differences:** Muon and electron identification criteria differ between experiments. Isolation requirements, impact parameter cuts, and quality selections are experiment-specific. The dilepton observables in these datasets (`pT_l1`, `eta_l1`, etc.) implicitly assume specific identification criteria that are not documented.

**N-subjettiness calculation differences:** The tau1, tau2, tau3 observables represent N-subjettiness variables, but the calculation depends on choices of axes (kt-axes, winner-take-all axes, etc.) and the beta parameter. Different experiments and analyses use different conventions, making these observables non-comparable without explicit documentation.

These experiment-specific differences mean that a dataset produced for ATLAS cannot be directly used for CMS comparisons, and vice versa, without comprehensive documentation of all observable definitions and reconstruction procedures.

### Lack of Standardized Naming Conventions for Weight Columns

The weight column naming in these datasets illustrates the absence of community-wide standards:

**Systematic weight naming ambiguity:** The column `weights_muEffReco` could mean "muon efficiency for reconstruction," "muon reconstruction efficiency," or "efficiency of muon reconstruction." Different analyses use different naming schemes, making automated processing error-prone. Some analyses use `muon_eff_reco`, others use `mu_eff_reco`, and still others use `MuonEfficiencyReconstruction`.

**Bootstrap weight indexing:** The bootstrap weights use zero-based indexing (`weights_bootstrap_mc_0`), but some analyses use one-based indexing (`weights_bootstrap_mc_1`). Without documentation, users cannot determine if sample 0 is the first bootstrap sample or a special nominal sample.

**Ensemble weight semantics:** The 100 ensemble weights (`weights_ensemble_0` through `weights_ensemble_99`) have no standard interpretation. They could represent:
- 100 independent systematic variations
- 100 correlated variations from a single systematic source
- 100 samples from a posterior distribution
- 100 iterations of an iterative unfolding procedure

Without standardized naming and documentation, users must guess the intended meaning, leading to incorrect uncertainty propagation.

**Prefix inconsistency:** The mixing of `weight_` (singular) and `weights_` (plural) prefixes within the same dataset suggests ad-hoc naming rather than adherence to a standard. This inconsistency complicates automated column selection and increases the risk of selecting the wrong weight column.

### OmniFold Training Variability and Reproducibility

OmniFold is a machine learning-based unfolding technique that depends critically on training configuration choices. Different implementations and training procedures produce different results:

**Neural network architecture variability:** The choice of network depth, width, activation functions, and regularization significantly affects unfolding performance. A shallow network may underfit, while a deep network may overfit. Without documenting the architecture, users cannot assess whether the unfolding is appropriate for the problem or reproduce the training.

**Hyperparameter sensitivity:** Learning rate, batch size, and optimizer choice (Adam, SGD, RMSprop) strongly influence convergence and final results. Different hyperparameters can lead to different local minima in the loss landscape, producing different unfolded distributions. The absence of hyperparameter documentation makes reproduction impossible.

**Iteration count and stopping criteria:** OmniFold is an iterative procedure where each iteration refines the unfolding. The number of iterations affects the degree of unfolding and the bias-variance tradeoff. Stopping too early leaves residual bias; stopping too late increases variance. Without documenting the iteration count and stopping criteria, users cannot reproduce or validate the unfolding.

**Feature normalization and preprocessing:** Whether input observables are standardized (zero mean, unit variance), normalized (scaled to [0,1]), or left unnormalized affects training dynamics and convergence. Different preprocessing choices lead to different results. The absence of preprocessing documentation prevents reproduction.

**Random seed dependence:** Neural network training depends on random initialization of weights and random shuffling of training batches. Different random seeds produce different trained networks and thus different unfolded results. Without documenting random seeds, exact reproduction is impossible, and users cannot assess the stability of the unfolding with respect to random initialization.

The `target_dd` column in multifold.h5 indicates that OmniFold training occurred, but the complete absence of training configuration metadata means the unfolding cannot be reproduced, validated, or extended to new datasets.

### Numerical Precision and Data Type Inconsistencies

The inconsistent use of float32 and float64 across these datasets creates both technical and scientific challenges:

**Precision requirements for uncertainty propagation:** Statistical uncertainties computed from bootstrap resampling require high numerical precision to avoid accumulation of rounding errors. The use of float64 for bootstrap weights in multifold.h5 and multifold_sherpa.h5 suggests this was recognized, but the inconsistent use of float32 for `weights_nominal` in some files indicates lack of standardization.

**Cross-dataset arithmetic precision loss:** When combining datasets with different precisions (e.g., adding multifold.h5 with float32 nominal weights to multifold_nonDY.h5 with float32 nominal weights, but comparing to multifold_sherpa.h5 with float64 nominal weights), precision loss can occur. The results depend on the order of operations and the specific arithmetic implementation.

**Block structure incompatibility:** The different block structures (different groupings of columns by dtype) mean that direct HDF5 block-level operations cannot be used for cross-dataset processing. Users must read columns individually, which is slower and more error-prone than block-level operations.

**No documented precision requirements:** Without documentation of required numerical precision for each quantity, users cannot determine if float32 is sufficient or if float64 is necessary. This is particularly important for quantities that span many orders of magnitude (event weights can range from 10^-10 to 10^10), where float32 may lose precision.

These precision inconsistencies suggest the datasets were produced by different pipelines without coordination, and the lack of precision documentation prevents users from assessing the numerical reliability of results.

### Lack of Standardized Metadata Schema for OmniFold Outputs

The high-energy physics community lacks a standardized schema for OmniFold and machine learning-based unfolding outputs:

**No required metadata fields:** Unlike traditional unfolding methods (e.g., iterative Bayesian unfolding, SVD unfolding) which have established conventions for documenting regularization parameters and iteration counts, OmniFold has no community-agreed metadata requirements. Producers can omit critical information without violating any standard.

**No validation or verification tools:** There are no automated tools to check that OmniFold outputs include necessary metadata. Users must manually inspect files to determine what information is available, which is time-consuming and error-prone.

**No schema versioning:** As OmniFold methodology evolves (e.g., adding new features, changing training procedures, incorporating new systematic uncertainties), there is no mechanism to track schema versions. Users cannot determine which version of OmniFold was used or what features are supported.

**No interoperability standards:** Different OmniFold implementations (TensorFlow-based, PyTorch-based, JAX-based) produce outputs in different formats with different metadata conventions. There is no standard for ensuring interoperability between implementations.

**No long-term preservation standards:** Without standardized metadata, datasets become difficult to interpret over time as analysis conventions evolve and original analysts move to other projects. Long-term preservation requires self-documenting datasets with comprehensive metadata.

The absence of these standards means each OmniFold analysis invents its own conventions, making cross-analysis comparisons, method validation, and dataset reuse extremely difficult. Establishing community-wide standards for OmniFold metadata would significantly improve reproducibility and enable broader adoption of machine learning-based unfolding techniques.

### Impact on Reproducibility and Interoperability

These standardization challenges have concrete negative impacts:

**Reproducibility barriers:** Without standardized metadata, reproducing OmniFold results requires access to original analysis code, which may not be publicly available or may depend on deprecated software versions. Scientific reproducibility is compromised.

**Interoperability failures:** Combining datasets from different generators, experiments, or analyses requires extensive manual work to understand conventions and apply appropriate transformations. Automated workflows are not possible.

**Validation difficulties:** Validating OmniFold results by comparing to alternative unfolding methods or to results from other experiments requires understanding all convention differences. Without standardized metadata, validation is error-prone.

**Collaboration friction:** Sharing datasets between research groups or across experiments requires extensive documentation and communication to explain conventions. This friction slows scientific progress and discourages collaboration.

**Long-term preservation risks:** Datasets without comprehensive metadata become increasingly difficult to interpret over time. Future researchers may be unable to use these datasets, representing a loss of scientific investment.

Addressing these standardization challenges requires community-wide coordination to develop and adopt metadata standards for machine learning-based physics analyses. The current ad-hoc approach, exemplified by these three datasets, is not sustainable as machine learning methods become more prevalent in high-energy physics.

## Minimal Metadata Required for Safe Reuse

To enable correct interpretation and reuse of these datasets, the following minimum metadata must be provided:

**Normalization and Cross-Section Information:**
- Integrated luminosity (fb⁻¹ or pb⁻¹)
- Generator cross-section for each process (pb)
- Filter efficiency applied during event generation
- Explicit definition of `weight_mc` (generator weight, cross-section weight, or combined)
- Explicit definition of `weights_nominal` (product of corrections, luminosity-normalized, or relative weight)
- Relationship between `weight_mc` and `weights_nominal` (multiplicative factor or independent)

**Observable Definitions:**
- Physical units for each observable (GeV, GeV/c, radians, degrees, dimensionless)
- Coordinate system conventions (phi range [0, 2π] or [-π, π], eta definition, beam axis)
- Observable level (detector-level, particle-level, or parton-level)
- Jet clustering algorithm and parameters (anti-kt, radius, pT threshold)
- Track selection criteria (pT cut, eta acceptance, vertex association, quality requirements)
- N-subjettiness parameters (beta value, axes definition: kt-axes, winner-take-all, etc.)
- Lepton identification criteria (isolation, impact parameter, quality selections)

**OmniFold Training Configuration:**
- Neural network architecture (number of layers, nodes per layer, activation functions)
- Training hyperparameters (learning rate, batch size, optimizer type, number of epochs)
- Number of OmniFold iterations performed
- Random seeds (network initialization, data shuffling, bootstrap generation)
- Training feature list (which observables were used as inputs)
- Feature preprocessing (normalization method, standardization, transformations applied)
- Stopping criteria (loss threshold, validation metric, early stopping parameters)
- Training/validation split methodology

**Systematic Uncertainty Definitions:**
- Mapping of ensemble weight indices to systematic sources
- Correlation structure between systematic sources (correlation matrix or independence statement)
- Magnitude of each systematic variation (±1σ, ±2σ, or custom)
- Generation method for theory systematics (PDF set, scale variation procedure, αs variation)
- Detector systematic sources included (efficiency, calibration, resolution, fake rate)
- Whether systematic variations are symmetric or asymmetric (up/down variations)

**Bootstrap Generation Procedure:**
- Random seed for each bootstrap sample (enables reproduction)
- Resampling method (with replacement, without replacement, or other)
- Bootstrap sample independence (whether samples are independent across datasets)
- Index alignment between MC and data bootstrap samples
- Whether bootstrap samples include systematic variations or are purely statistical

**Event Selection and Phase Space:**
- Kinematic cuts applied (pT thresholds, eta acceptance, mass windows)
- Trigger requirements (trigger paths, prescales, efficiency corrections)
- Event quality criteria (vertex requirements, detector status, data quality flags)
- Lepton selection (flavor, charge, multiplicity, isolation, identification working point)
- Jet selection (multiplicity, pT ordering, jet quality, overlap removal)
- Phase space definition (fiducial region, detector acceptance, analysis cuts)

**Dataset Provenance and Interoperability:**
- Dataset origin (collision data, Monte Carlo simulation, or pseudodata)
- Monte Carlo generator and version (Pythia 8.306, Sherpa 2.2.11, etc.)
- Experiment identification (ATLAS, CMS, LHCb, or theory study)
- Production date and software versions (ROOT, pandas, OmniFold implementation)
- Intended use (primary analysis, validation, background, closure test)
- Compatible datasets (which datasets can be safely combined)
- Known limitations or caveats (phase space restrictions, known issues)

This minimal metadata checklist represents the absolute minimum information required for safe dataset reuse. Additional metadata may be necessary depending on the specific analysis context, but omitting any of these elements will compromise reproducibility, correctness, or interoperability.

## Recommendations for Unified Schema

A unified schema should include both data and metadata. Recommended metadata fields:

### Dataset Provenance
- `dataset_origin`: Data, MC, or pseudodata
- `generator`: Pythia, Sherpa, Powheg, etc.
- `generator_version`: Specific version and tune
- `production_date`: When dataset was created
- `production_software`: Software versions used

### OmniFold Training Parameters
- `omnifold_iterations`: Number of iterations performed
- `neural_network_architecture`: Layer structure and activation functions
- `training_hyperparameters`: Learning rate, batch size, optimizer, epochs
- `random_seeds`: Seeds for reproducibility
- `training_features`: List of observables used for training
- `feature_normalization`: Standardization or normalization applied

### Observable Definitions
- `observable_units`: Physical units for each observable (GeV, radians, etc.)
- `coordinate_conventions`: Phi range, eta definition, etc.
- `jet_algorithm`: Clustering algorithm and parameters
- `track_selection`: Criteria for track jets
- `nsubjettiness_parameters`: Beta value and axes definition

### Normalization Information
- `integrated_luminosity`: Luminosity in fb^-1 or pb^-1
- `cross_section`: Generator cross-section in pb
- `filter_efficiency`: Event filter efficiency
- `weight_normalization`: Whether weights include luminosity
- `weight_definitions`: Explicit definition of weight_mc and weights_nominal relationship

### Event Selection
- `kinematic_cuts`: pT and eta thresholds
- `trigger_requirements`: Trigger paths applied
- `lepton_selection`: Flavor, charge, isolation criteria
- `event_quality`: Quality cuts applied

### Systematic Uncertainty Definitions
- `systematic_sources`: List of systematic sources included
- `ensemble_generation_method`: How ensemble variations were created
- `systematic_magnitudes`: Size of each systematic variation
- `correlation_matrix`: Correlations between systematic sources

### Bootstrap Information
- `bootstrap_method`: With or without replacement
- `bootstrap_random_seeds`: Seed for each bootstrap sample
- `bootstrap_alignment`: Whether indices align across datasets

### Dataset Role
- `intended_use`: Primary analysis, validation, background, closure test
- `compatible_datasets`: Which datasets can be combined
- `usage_restrictions`: Known limitations or caveats

This metadata structure would enable reproducible analysis, proper uncertainty propagation, and safe dataset combination. The current datasets lack nearly all of this information, severely limiting their reusability.

## Conclusion

The three OmniFold datasets examined here illustrate a common challenge in computational physics: data without metadata has limited scientific value. While the HDF5 files contain numerical values for observables and weights, the absence of documentation makes it nearly impossible to use these datasets correctly without access to the original analysts or analysis code.

Reproducibility requires more than sharing data files. It requires sharing the complete context: what the data represents, how it was generated, what assumptions were made, and how it should be used. The missing metadata documented in this analysis—from OmniFold training parameters to observable definitions to normalization conventions—is not optional information. It is essential for anyone attempting to reproduce, validate, or extend the analysis.

For future dataset releases, metadata should be treated as equally important as the data itself. A unified schema that includes both numerical data and comprehensive metadata would transform these datasets from difficult-to-interpret files into valuable scientific resources that enable reproducible research and facilitate collaboration across research groups.
