# NutriLens ML research pipeline

This is an adaptation of ingredient-text neural modelling for Indian snacks and beverages. Read [research design](../research/RESEARCH_DESIGN.md) before presenting it. It predicts **source Nutri-Score bands**, not medical health or food safety.

## Reproduce (Python 3.12)

```sh
python3.12 -m venv .venv-ml
.venv-ml/bin/pip install -r ml/requirements.txt
.venv-ml/bin/python ml/collect.py
.venv-ml/bin/python ml/prepare.py
.venv-ml/bin/python -m unittest discover -s ml -p 'test_*.py'
.venv-ml/bin/python ml/train.py
.venv-ml/bin/python ml/predict.py --category snack --ingredients "wheat flour sugar palm oil salt raising agents"
```

Collection is resumable and deliberately slow to respect API limits. Raw snapshots, the manifest, curated rows and product split IDs stay in ignored `ml/data/`. Fetch errors stop the run rather than manufacture records. Completeness is limited by `--max-pages` (default 50 per category). Prepare/train scripts do not infer that a partial download is complete; inspect collection progress and manifest.

`research/data-audit.json` reports exclusions and coverage. `research/evaluation.json` exists only after successful real training. `ml/artifacts/ingredient-mlp.joblib` stores the learned vocabulary and network weights locally. Never load untrusted joblib files; loading can execute code. Do not commit the virtual environment or raw database by accident.

Inference is experimental and local. Vocabulary coverage can trigger abstention, but it is not a validated out-of-distribution detector. There is no claim of calibrated probability, general multilingual support, FSSAI approval or consumer deployment. The existing website continues to use measured database information and explicit rules until the research model is evaluated and separately integrated.

After successful training, run `.venv-ml/bin/python ml/serve.py` and open http://127.0.0.1:8765 for the local research interface. It shows the real evaluation report and model output separately from the consumer app. It binds only to loopback and does not log form contents.

If broad API pagination fails, `.venv-ml/bin/python ml/collect_stratified.py` supplements up to 100 records for each category/grade band. This is **label-stratified convenience sampling**, not a representative survey. Keep its separate manifest and disclose the sampling bias when presenting metrics. The curator deduplicates overlapping barcodes.
