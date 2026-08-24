# Retail LLM Evaluation

![Python](https://img.shields.io/badge/Python-3.11-blue)
![OpenAI](https://img.shields.io/badge/OpenAI-API-black)
![LLM Evaluation](https://img.shields.io/badge/LLM-Evaluation-purple)
![Privacy](https://img.shields.io/badge/Privacy-GDPR%20Aware-green)

A practical evaluation framework for a retail customer-service LLM, focused on whether the system is not only helpful, but also grounded, policy-compliant, privacy-aware and operationally correct.

---

## What this project tests

The evaluation covers five common retail customer-service journeys:

- Delivered but not received
- Wrong product received
- Cancelled order and refund status
- Return outside the policy window
- Order status and customer verification

The objective is to test more than response quality.

We also check whether the assistant:

- uses the available evidence correctly
- avoids unsupported claims
- follows business rules
- handles customer data appropriately
- gives a valid next step
- avoids critical operational failures

---

## Evaluation approach

The project combines two evaluation layers:

```text
Customer case
    ↓
Structured system context
    ↓
LLM response
    ↓
Deterministic checks + LLM-as-a-Judge
    ↓
Structured evaluation result
````

### Deterministic checks

Used for things that can be verified directly:

* system state
* allowed actions
* policy rules
* privacy requirements
* critical failures

### LLM-as-a-Judge

Used for dimensions that require semantic judgement:

* evidence grounding
* hallucination avoidance
* resolution quality
* clarity
* customer-facing quality

The judge is calibrated with known good, borderline and bad examples to reduce overly generous scoring.

---

## Benchmark references

The design was informed by three current benchmark families:

| Benchmark        | What it contributes                                                 |
| ---------------- | ------------------------------------------------------------------- |
| **τ³-bench**     | End-to-end customer-service evaluation with tools, policy and state |
| **BFCL V4**      | Function and tool-calling behaviour                                 |
| **JourneyBench** | Business-process and policy adherence                               |

External benchmarks are used as references, not as proof that the system works for a specific retailer.

The main evidence comes from the custom retail test set.

---

## Results

The current test run covered all five scenarios.

| Metric | Result |
|---|---:|
| Cases run | 5 |
| Average score | 4.8 / 5 |
| Minimum score | 4 |
| Maximum score | 5 |
| Critical failures | 0 |
| Total runtime | 15.72 seconds |
| Chatbot tokens | 1,130 |
| Judge tokens | 5,281 |
| Total tokens | 6,411 |
| Estimated cost | $0.001388 |

The only non-perfect result was the missing-delivery case. The answer was safe and correct, but did not explicitly explain that no proof of delivery or delivery notes were available.

That case was also used to calibrate the judge.

---

## Project structure

```text
.
├── README.md
├── benchmark_audit.md
├── evaluation_design.md
├── evaluation_memo.md
├── reflection.md
├── implementation_summary.md
├── llm_judge_evaluation.py
├── evaluation_results.json
├── requirements.txt
├── .env.example
└── .gitignore
```

### File guide

| File                        | Purpose                                                             |
| --------------------------- | ------------------------------------------------------------------- |
| `benchmark_audit.md`        | Review of the external benchmarks used to shape the evaluation      |
| `evaluation_design.md`      | Five custom test cases, judge rubric, bias analysis and calibration |
| `llm_judge_evaluation.py`   | Python evaluation pipeline                                          |
| `evaluation_results.json`   | Raw results and aggregate metrics                                   |
| `evaluation_memo.md`        | Client-facing summary and recommendation                            |
| `implementation_summary.md` | Technical summary of the implementation                             |
| `reflection.md`             | Notes on multilingual evaluation, AGI claims and human review       |

---

## Run locally

### 1. Create or activate a Python environment

Python 3.11 is recommended.

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Add the API key

Create a `.env` file:

```text
OPENAI_API_KEY=your_openai_api_key_here
```

The `.env` file is excluded from version control.

### 4. Run the evaluation

```bash
python llm_judge_evaluation.py
```

Results are written to:

```text
evaluation_results.json
```

---

## Evaluation principles

This project follows a few simple rules:

* Do not treat fluency as correctness.
* Do not use an LLM judge for facts that can be checked directly.
* Treat privacy, policy and financial errors as operational risks.
* Keep critical failures separate from style quality.
* Use external benchmarks as references, not as production evidence.
* Calibrate the judge before trusting its scores.
* Treat results as valid only for the scenarios and conditions tested.

---

## Current scope

This is a small controlled evaluation, not a production benchmark.

The current version uses:

* 5 retail scenarios
* simulated system context
* one target model
* one judge model
* deterministic checks for critical rules

A production evaluation would need a larger private test set, repeated runs, real tool integrations and targeted human review for high-risk cases.
