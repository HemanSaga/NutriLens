# NutriLens: ingredient-based nutritional-quality estimation for Indian packaged foods

Status: research implementation. A model is not trained merely because the code exists. Check `evaluation.json` for a completed run; absent results must never be represented as accuracy claims.

## Main reference and the evidence we can use

Ma, P. et al. (2022). *Deep learning accurately predicts food categories and nutrients based on ingredient statements*. Food Chemistry 391, 133243. DOI: https://doi.org/10.1016/j.foodchem.2022.133243.

Evidence inspected: the indexed abstract and the authors' USDA technical summary, not the paywalled full experimental methods. Sources: https://pubmed.ncbi.nlm.nih.gov/35623276/ and https://www.ars.usda.gov/research/publications/publication/?seqNo115=391003 .

The authors describe 134k USDA branded-food records, ingredient-text TF-IDF encoding, MLP models, and SMOTEENN rebalancing. They report up to 99% food-classification accuracy and calcium R² of 0.98 on their tasks. These numbers are NOT NutriLens results and do not establish performance on Indian products. The useful finding is that ingredient statements contain a learnable signal for food attributes. We adapt that representation and model family; we do not claim an exact reproduction, reuse of their dataset, or their performance.

Supporting full-text reference: Menichetti et al. (2023), *Machine learning prediction of the degree of food processing*, Nature Communications 14, 2312, https://www.nature.com/articles/s41467-023-37457-1 . FoodProX uses random forests on nutrient profiles to predict NOVA processing classes. It supports comparing nonlinear models against baselines and distinguishing processing from overall health. It is NOT a deep-learning paper or an Indian clinical validation.

Additional methods reference inspected: Arora et al., *Machine learning and natural language processing models to predict the extent of food processing*, preprint https://arxiv.org/abs/2412.17217 and full PDF https://arxiv.org/pdf/2412.17217 . The study compares conventional classifiers, MLP and pretrained text representations using FNDDS/NOVA data. We use it to motivate model comparisons and evaluation beyond accuracy, not to borrow its reported scores. It is a preprint, and its processing prediction differs from our nutritional-quality target.

## Product scope

Two strata, evaluated separately:

1. Packaged snacks listed as sold in India: biscuits/crackers, chips/crisps, namkeen/savoury snacks, bars, nuts and other records tagged as snacks. Report the observed subcategory composition; the dataset may overrepresent confectionery or biscuits.
2. Packaged non-alcoholic beverages listed as sold in India: soft drinks, juices/fruit drinks, flavoured dairy/plant beverages and ready-to-drink tea/coffee. Community category tags are imperfect; review sampled labels and exclusions.

Exclude infant foods, supplements, meal replacements, alcoholic beverages, and known powdered/dehydrated drinks. Only source scores explicitly marked `as_sold` are eligible. This is an initial taxonomy-based scope, not a manually verified catalogue of every Indian brand. English ingredient text only in the first experiment; a language heuristic is not a reliable language detector.

## Research question and target

Can a neural network estimate a source-defined nutritional-quality band from ingredients and broad product category, including on held-out brands/recipes?

Target: Open Food Facts' **2023 Nutri-Score** grouped as A/B = `more_favourable`, C = `intermediate`, D/E = `less_favourable`. These three bands are our research simplification, not official additional Nutri-Score classes. Source labels must be computed, applicable, non-estimated, and as-sold. Nutri-Score is not an FSSAI certification or an Indian clinical health standard. No label is a ground-truth measure of personal health, allergies, adulteration, freshness or contamination.

Inputs: English ingredient TF-IDF unigrams/bigrams plus snack/beverage one-hot indicators. Do NOT input product name, barcode, brand, original score, grade, NOVA, or nutrient values used to compute the target. Excluding the score inputs avoids the trivial experiment of teaching a network to imitate a known formula from its exact ingredients. Correlation with source scores still requires external validation.

Measured nutrition remains authoritative in the app. Predictions must never fill missing label values or overwrite a supplied grade. Processing level and allergen findings remain separate.

## Model justification and comparison

Main neural model: TF-IDF (maximum 4,000 train-fitted text features) → Dense 128/ReLU → Dense 64/ReLU → Dense 32/ReLU → 3-way softmax. This is a trained feed-forward neural network with three hidden layers, not a rules engine. Adam learns weights by backpropagation; L2 regularisation and validation-loss early stopping constrain overfitting. Class-balanced training weights address skew without making synthetic food labels. Category is explicitly included because snacks and beverages differ.

Why this model: direct connection to Ma et al.'s ingredient-text/MLP approach; feasible on a student's CPU; auditable vocabulary and weights; avoids claiming visual nutrition can be inferred from front-of-pack images. Layer widths, label bands and weighting are OUR choices, not reported hyperparameters reproduced from Ma et al.

Comparators on identical splits: majority-class predictor; class-weighted logistic regression over identical features; random forest over identical features. The deep model must be compared honestly even if a baseline wins. A transformer is a subsequent experiment, not automatically a better model or an implemented component. Tesseract OCR and speech playback are existing third-party components; they do not count as our trained health prediction model.

## Data and leakage controls

Data source: Open Food Facts public API, filtered to India and snack/beverage categories. Save raw pages, request URLs, fetch times and SHA-256 hashes. Preserve ODbL attribution; raw data and binary models are ignored by Git by default. Community labels/ingredients can be wrong, incomplete, stale or imbalanced.

Deduplicate by barcode. Join records into connected components if they share any normalised brand or an identical normalised ingredient list. Split these groups with a fixed-seed, five-fold stratified-group procedure: fold 0 test, fold 1 validation, remaining folds training. Neither train vocabulary nor class weights see held-out rows. Early stopping uses validation loss only. Test results are reported after model selection, never used to choose the epoch. This is stricter than random product splitting but does not remove all manufacturer aliases, near-duplicate recipes or language noise.

## Evaluation and release gates

Report raw/eligible counts, exclusion reasons, each category's class balance, group counts, split sizes, architecture, dependencies and dataset hash. For every comparator report macro-F1, accuracy, per-class precision/recall/F1, confusion matrix and log loss. For the MLP also report snack and beverage test metrics separately. Probability outputs are uncalibrated model scores, not percentages of healthiness or confidence guarantees.

Predeclared engineering gates: at least 30 test records for each category/class combination; validation macro-F1 ≥0.70; validation macro-F1 better than the strongest baseline; independent food-science review. These thresholds are project requirements, not established clinical standards. A failing gate leaves the model research-only. Independent review is currently absent and must not be auto-approved by software.

## Explanation approach

Measured label facts explain the displayed nutrition assessment. For the experimental neural model, token removal shows which ingredient words change its score. These are model-sensitivity explanations, not proof that an ingredient caused an outcome or is hazardous. They can be affected by correlated words and unnatural masked text. Do not label them SHAP or attention explanations.

## What remains before a defensible final submission

Complete the actual data run; save actual evaluation and model artifact; review errors and minority-class coverage; verify representative products against Indian pack labels; add a clearly identified experimental inference panel only after results are available; include methodology, limitations, confusion matrices and a model card in the dissertation. A production health product also needs independent review and broader validation. No invented dataset, fabricated accuracy, or model-name-only interface is acceptable.

### Pilot collection amendment

The public paginated endpoint repeatedly returned HTTP 503 for later pages. A supplemental collector requests category × source-grade strata (A/B, C, D/E), capped at 100 records per stratum. These records are merged with the initial pages and deduplicated by barcode. This purposive, label-stratified pilot must not be used to estimate prevalence, population accuracy or probability calibration. The same frozen grouping and evaluation procedure applies; it remains exploratory. The original API filters may use a top-level current grade; eligibility and training targets are always rechecked against the explicit 2023 record.
