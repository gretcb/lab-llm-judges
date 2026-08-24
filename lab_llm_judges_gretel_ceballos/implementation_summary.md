# Implementation Summary

The evaluation pipeline was implemented in Python using the OpenAI API and a small custom test set of five retail customer-service scenarios.

Each case includes a customer prompt, structured system context and expected behaviour. The chatbot generates a response using only the supplied context, and a second LLM evaluates that response against a fixed rubric covering grounding, tool/action correctness, policy compliance, hallucination, resolution, dialogue quality and privacy.

The judge was calibrated before running the full test set. In the first version, it gave a perfect score to a response that was safe and correct but did not mention that delivery notes and proof of delivery were unavailable. Calibration examples and clearer score anchors were added, after which the same response was scored 4/5. This helped reduce leniency and made the difference between a correct answer and a complete answer more explicit.

## Results

The evaluation ran across all five test cases.

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

The strongest result was consistency across the test set: no case triggered a critical failure such as invented delivery information, unauthorized refund claims or privacy violations.

The main limitation is the size of the dataset. Five cases are enough to demonstrate the evaluation approach, but not enough to make production-level claims about the system. A larger private dataset, repeated runs and human review would be needed before deployment.