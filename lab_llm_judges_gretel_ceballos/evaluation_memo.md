# Evaluation Memo — Retail Customer Service LLM

**TO:** Retail Client  
**FROM:** Gretel Ceballos  
**DATE:** 24 August 2026  
**SUBJECT:** LLM Evaluation Results — Retail Customer Service Assistant

---

## Executive Summary

We evaluated an LLM-powered customer service assistant across five retail scenarios covering delivery issues, incorrect items, refunds, returns and order status.

Under the tested conditions, the assistant performed strongly, with an average judge score of **4.8/5** and **no critical failures**. The results are encouraging, but the test set is intentionally small and controlled. They support further evaluation, not a production-readiness claim.

---

## Methodology

The evaluation combined external benchmark research with a small custom retail test set.

Three current benchmarks informed the design:

| Benchmark | What we used it for |
|---|---|
| **τ³-bench** | End-to-end customer service with policies, tools and state |
| **BFCL V4** | Tool and function-calling behaviour |
| **JourneyBench** | Business-process and policy adherence |

We did not treat benchmark performance as sufficient evidence for our specific retailer. Instead, we created five custom scenarios using structured system context and expected behaviour.

The five cases covered:

1. Delivered but not received
2. Wrong product received
3. Cancelled order and refund status
4. Return outside the policy window
5. Order status and customer verification

Each response was assessed using a hybrid evaluation approach.

Deterministic checks were used for facts and operational rules that can be verified directly, such as system state, allowed actions and privacy requirements. An LLM-as-a-judge was used for semantic qualities such as grounding, hallucination avoidance, resolution quality and customer-facing clarity.

The judge was calibrated before the full run. Its first version scored a safe but incomplete response too generously. We added clearer score anchors and reference examples, after which the judge correctly distinguished between a good response and a complete one.

---

## Results

The assistant completed all five test cases without triggering a critical failure.

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

Four cases received a score of 5/5. The "delivered but not received" case received 4/5 because the response correctly identified the order as delivered and proposed an investigation, but did not explicitly state that delivery notes and proof of delivery were unavailable.

This was not considered a safety or policy failure. It was treated as a completeness issue.

Across the five cases, the assistant did not invent recipients, delivery locations, completed refunds or investigation actions. It also did not trigger the privacy-related critical failure defined in the evaluation.

---

## Caveats & Limitations

The main limitation is sample size. Five scenarios are sufficient to demonstrate the evaluation method, but they are not representative of the full range of customer-service behaviour that would occur in production.

The test also uses simulated system context rather than live retail APIs. This means we are evaluating model behaviour against controlled evidence, not validating a complete production integration.

Benchmark results also require caution. Public benchmarks can be affected by contamination, and older or simpler tasks can become saturated as models improve. This is one reason the evaluation relies on custom cases rather than external benchmark scores alone.

The LLM judge is another source of uncertainty. It can show bias towards fluent or convincing responses, which is why we calibrated it and kept factual and critical business rules outside the judge wherever possible.

---

## Recommendation

Under these test conditions, the assistant is suitable for further controlled evaluation.

I would not recommend production deployment based on this dataset alone. The next step should be a larger private evaluation set covering more edge cases, failed tool calls, ambiguous customer requests, policy conflicts and privacy-sensitive scenarios.

High-risk journeys such as refunds, account verification and personal-data access should continue to use deterministic checks and human review where appropriate.

Confidence in the current result is **moderate**: the model performed consistently across the tested scenarios, but the evidence base is still limited.

---

## Additional Metrics

The evaluation also shows that automated judging adds measurable overhead.

The chatbot generated **1,109 tokens**, while the judge used **5,268 tokens**. In this run, the evaluation layer consumed significantly more tokens than the customer-facing model itself.

This does not make LLM-as-a-judge unsuitable, but it does mean evaluation cost should be considered when scaling to hundreds or thousands of test cases.

For a larger evaluation programme, I would track:

- task success rate
- policy pass rate
- tool accuracy
- hallucination rate
- privacy failures
- latency
- token usage
- cost per evaluated case
- consistency across repeated runs

Token consumption also provides a basic proxy for compute demand, but this evaluation does not measure energy use or carbon emissions directly, so no environmental-impact claim is made.

The objective should not be to maximise a single score, but to understand where the system is reliable, where it fails and what level of control is required before deployment.