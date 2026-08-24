# Benchmark Audit — Retail Customer Service LLM

## Client Scenario

A mid-sized online retailer wants to introduce an LLM-powered customer service assistant for common post-purchase requests such as delivery issues, wrong products, cancellations, refunds, returns and order-status questions.

The assistant needs to give accurate information, use the right tools, follow company policies, protect personal data and avoid making claims it cannot support. The main risks are hallucinated order or refund information, incorrect actions, policy violations, privacy issues and answers that sound helpful but do not actually solve the customer's problem.

---

## What We Need to Test

For this use case, a good answer is not enough on its own.

We also need to know whether the assistant can:

| Area | What we want to check |
|---|---|
| Task resolution | Does it actually solve the customer's issue? |
| Tool use | Does it use the correct system or API? |
| Policy adherence | Does it follow the retailer's rules and process? |
| Grounding | Are its claims supported by the available data? |
| Privacy | Does it avoid exposing or requesting unnecessary personal data? |
| Hallucination control | Does it avoid inventing statuses, actions or customer information? |
| Customer experience | Does it give a clear and useful next step? |

---

# Benchmark Shortlist

We shortlisted three benchmarks because they cover different parts of the problem.

| Benchmark | Main reason for using it | Verdict |
|---|---|---|
| **τ³-bench** | End-to-end customer service with policies, tools and state | Adapt |
| **BFCL V4** | Tool and function calling | Adapt |
| **JourneyBench** | Business process and policy adherence | Adapt |

None of them matches our retailer exactly, so we will use them as references rather than as a complete answer. The final evaluation will use our own retail cases, policies and tool outputs.

---

# 1. τ³-bench

**Benchmark Name:** τ³-bench  
**Year:** 2026 — v1.0.1, July 2026  
**Source:** Sierra Research  
**Repository:** https://github.com/sierra-research/tau2-bench

### Why it seemed relevant

τ³-bench is a strong fit because it evaluates agents across full interactions involving a customer, business policies, tools and system state.

That is close to how a real retail support assistant would work. A missing-delivery case, for example, may require checking the order, looking at delivery information, applying policy and deciding what the next allowed action is.

We first looked at the original τ-bench from 2024, but the project now says those earlier retail and airline tasks are outdated. For a 2026 evaluation, τ³-bench is the more useful reference.

### Contamination Risk

- [ ] Low
- [x] Medium
- [ ] High

**Explanation:**  
The benchmark is public, so there is some chance that benchmark-related material could appear in training or fine-tuning data. At the same time, it has been actively updated, which makes it less stale than an older static benchmark.

### Saturation Risk

- [x] Low
- [ ] Medium
- [ ] High

**Explanation:**  
The benchmark still focuses on multi-step tasks involving tools, policy and state, which are harder than simple question-answer tasks. It is also actively maintained and has received recent corrections.

### Format

- [ ] Multiple Choice
- [ ] Free-form text
- [ ] Code generation
- [x] Other: Multi-turn agent interaction with policies, tools and state

### Verdict

- [ ] Use it as-is
- [x] **Adapt it**
- [ ] Reject it

**Why:**  
The setup is very relevant, but our retailer would have different tools, policies, escalation rules and customer data.

We would reuse the same type of structure:

`customer request → tools → policy → system state → resolution`

but with our own retail scenarios.

---

# 2. Berkeley Function Calling Leaderboard — BFCL V4

**Benchmark Name:** Berkeley Function Calling Leaderboard (BFCL V4)  
**Year:** 2025 — V4, still current in 2026  
**Source:** Gorilla / UC Berkeley  
**Leaderboard:** https://gorilla.cs.berkeley.edu/leaderboard.html  
**Repository:** https://github.com/ShishirPatil/gorilla/tree/main/berkeley-function-call-leaderboard

### Why it seemed relevant

A customer service chatbot may need to call functions such as:

```text
get_order()
get_delivery_status()
get_delivery_notes()
get_refund_status()
create_return()
open_delivery_investigation()
````

BFCL is useful because it checks whether a model chooses the correct function, passes the right arguments and handles more complex multi-turn tool use.

This is important for our use case because an assistant can give a convincing answer while using the wrong tool or changing the wrong order.

### Contamination Risk

* [ ] Low
* [x] Medium
* [ ] High

**Explanation:**
BFCL is public and widely used, so some exposure is possible. However, the benchmark has evolved through several versions and includes newer evaluation data instead of relying only on one fixed dataset.

### Saturation Risk

* [ ] Low
* [x] Medium
* [ ] High

**Explanation:**
Simpler function-calling tasks have become easier for strong models. BFCL V4 puts more focus on multi-turn and agentic tasks, which are more useful for our scenario.

### Format

* [ ] Multiple Choice
* [ ] Free-form text
* [ ] Code generation
* [x] Other: Function calling and multi-turn tool use

### Verdict

* [ ] Use it as-is
* [x] **Adapt it**
* [ ] Reject it

**Why:**
BFCL is useful for checking tool use, but it does not know our retailer's rules or customer journeys.

We would use its ideas to check things like:

* Did the assistant choose the correct tool?
* Did it use the correct order ID?
* Did it avoid calling a tool when required information was missing?
* Did it perform multiple actions in the right order?

A good BFCL result would not automatically mean the chatbot provides good customer service.

---

# 3. JourneyBench

**Benchmark Name:** JourneyBench — Beyond IVR: Benchmarking Customer Support LLM Agents for Business-Adherence
**Year:** 2026
**Source:** Balaji, Mishra, Sachdeva & Agrawal — EACL 2026 Industry Track
**Paper:** [https://aclanthology.org/2026.eacl-industry.15/](https://aclanthology.org/2026.eacl-industry.15/)

### Why it seemed relevant

JourneyBench is especially useful because it looks at whether a customer-support agent follows the required business process, not just whether the final answer sounds correct.

That matters in retail. An assistant may reach a reasonable answer but still skip a required check or perform an action too early.

For example, in a "delivered but not received" case, the assistant should not automatically open an investigation before checking the order and available delivery evidence.

A valid process could look like this:

```text
identify order
→ check delivery status
→ review available delivery evidence
→ apply policy
→ choose the next allowed action
```

### Contamination Risk

* [x] Low
* [ ] Medium
* [ ] High

**Explanation:**
JourneyBench is recent, so it has had less time to circulate than older benchmarks. That lowers the contamination risk, although it does not remove it completely.

### Saturation Risk

* [x] Low
* [ ] Medium
* [ ] High

**Explanation:**
It tests multi-step customer-support workflows, branching logic, missing information and tool failures. These are still difficult and closer to real operational work than simple response-generation tests.

### Format

* [ ] Multiple Choice
* [ ] Free-form text
* [ ] Code generation
* [x] Other: Multi-turn customer-support workflows and SOP evaluation

### Verdict

* [ ] Use it as-is
* [x] **Adapt it**
* [ ] Reject it

**Why:**
Our retailer would have its own return rules, escalation paths, privacy requirements and internal processes.

We would use JourneyBench's main idea: evaluate whether the assistant followed the correct process, not only whether the final answer looked good.

---

# Audit Conclusion

The three benchmarks help us look at different parts of the same system:

```text
τ³-bench
└── Can the assistant complete the customer-service task?

BFCL V4
└── Can it use the right tools correctly?

JourneyBench
└── Can it follow the required business process?
```

What they cannot tell us is whether the chatbot works with our retailer's own policies, tools, customers and privacy requirements.

That is why the next step is to create a small custom evaluation set based on five realistic retail cases:

1. Delivered but not received
2. Wrong product received
3. Cancelled order and refund status
4. Return outside the policy window
5. Order status and customer verification

The custom evaluation will use both rule-based checks and an LLM judge.

Rule-based checks are better for things we can verify directly, such as tool selection, order state, policy rules or unauthorized data access.

The LLM judge will be used for things that are harder to measure with simple rules, such as grounding, hallucination, resolution quality and clarity.

Privacy is also part of the evaluation. If the chatbot exposes personal data without proper verification, that will be treated as a critical failure rather than something that can be compensated for by good tone or fluent language.