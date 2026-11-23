# NutriLens ingredient MLP — research model card

Trained 30 October 2026. Status: **experimental; consumer release gates failed**. The deployed consumer application does not use this model.

## Research basis and purpose

Primary reference: Ma et al. (2022), *Deep learning accurately predicts food categories and nutrients based on ingredient statements*, Food Chemistry 391, 133243. [DOI](https://doi.org/10.1016/j.foodchem.2022.133243). We reviewed the abstract and USDA author technical summary, not the unavailable full publisher methods. This is an adaptation, not a reproduction of their reported results.

The paper motivates ingredient-text features and multilayer perceptrons. Our different question is whether ingredient text can predict three bands derived from existing 2023 Nutri-Score labels for Indian-market snacks and nonalcoholic beverages. A multilayer network can learn nonlinear ingredient combinations; its usefulness must still be established against simpler models. This experiment did not establish superiority.

## Data and target

Open Food Facts provided 361 eligible unique products: 260 snacks and 101 beverages listed for India. India listing does not imply Indian manufacture or representative market coverage. English ingredient statements and an applicable, computed, non-estimated 2023 score on an as-sold basis were required. Infant foods, supplements, alcohol and other specified categories are excluded by taxonomy checks; see the preparation code and data audit.

Targets: A/B → more favourable; C → intermediate; D/E → less favourable. These are project-defined bands, not new official Nutri-Score classes. They are source-derived nutritional-quality labels, not clinical health outcomes, FSSAI approval, allergen safety or contaminant measurements.

Collection was partial because of repeated upstream failures. Supplemental label-stratified sampling creates a convenience sample. Class counts are 45 more favourable, 54 intermediate and 262 less favourable. Database omissions and annotation errors remain possible. Raw snapshots and collection manifests are retained locally under ignored `ml/data/`; redistribution requires review of Open Food Facts licensing.

## Model and leakage controls

Ingredient TF-IDF unigrams/bigrams plus category produce 1,699 input features. Three ReLU hidden layers have 128, 64 and 32 units, followed by three-class softmax. Adam training uses balanced training weights, L2 regularisation and validation-loss early stopping; epoch 10 was selected. Vocabulary is fitted on training data only. Nutrients, source scores, brands, barcodes and product names are not model inputs.

Brand and identical normalised-recipe connections define disjoint groups. Fixed-seed grouped splits contain 221 training, 90 validation and 50 test products. These controls cannot detect every related recipe or corporate brand relationship. Test results were inspected after model selection, not used to choose the epoch.

## Observed results

| Model | Validation macro-F1 | Test macro-F1 |
|---|---:|---:|
| Majority baseline | 0.287 | 0.245 |
| Logistic regression | 0.450 | 0.515 |
| Random forest | 0.494 | 0.509 |
| Deep MLP | 0.489 | 0.504 |

MLP test accuracy is 54%. Macro-F1 gives each class equal importance, useful with the observed imbalance. The small differences between models do not demonstrate statistical superiority.

Snack test macro-F1 is 0.347 on 40 products; recall for the more-favourable class is zero (four examples). Beverage test macro-F1 is 0.528 on only 10 products with no intermediate examples. Neither supports reliable category-wide claims.

All release gates failed: sufficient category/class test support, validation macro-F1 ≥0.70, beating the strongest validation baseline, and independent expert review. These are project screening gates, not a certification standard.

## Inference and explanations

Inference abstains on short inputs or low vocabulary coverage. This is a heuristic, not validated detection of all unfamiliar foods. Softmax outputs are uncalibrated model scores, never a percentage of healthiness. Ingredient-removal changes describe model sensitivity, not causal effects or proof an ingredient is harmful. Ingredient amounts, nutrients, portions, allergies and medical context cannot be inferred reliably from ingredient words alone.

Training produced numerical runtime warnings on this machine. All saved weights and predictions were checked for finiteness. An independent forward implementation matched sklearn probabilities on all 361 curated records with maximum absolute difference 0.0; see `numerical-validation.json`. Inference uses that checked forward implementation. This check verifies arithmetic agreement, not predictive validity.

## Next acceptance work

Collect and independently review substantially more Indian labels across every category and class, including missing beverage intermediate examples. Preserve this evaluation as the pilot; use fresh held-out data for subsequent final claims. Compare models under grouped cross-validation, assess calibration and abstention, inspect subgroup errors, and obtain food-science review before consumer integration. Keep measured nutrition and allergy warnings separate from model estimates.

See `RESEARCH_DESIGN.md`, `data-audit.json`, `evaluation.json` and `../ml/README.md` for methodology, machine-readable results and execution instructions. Learned weights are local in `ml/artifacts/ingredient-mlp.joblib`; they are not checked into Git.
