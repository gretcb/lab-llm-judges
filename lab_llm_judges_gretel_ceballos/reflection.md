# Reflection

## 1. What would change if the client data was in French?

I would not assume that an evaluation built in English would work the same way in French.

I would adapt the customer prompts, policies, expected behaviour and judge examples to French, rather than translating them literally. Customer-service language changes with context, and a model can perform well in English while being less precise or less natural in another language.

I would also check whether the external benchmarks we selected have useful French coverage. If not, I would rely more on a private French test set built around the retailer's real customer journeys.

The judge would need calibration in French as well. A model can produce fluent French and still be wrong about a refund, an order status or a policy, so language quality and operational accuracy should be assessed separately.

---

## 2. The client asks: “Is this model AGI-level?”

I would say that this evaluation cannot answer that question.

We are testing whether the model can handle a specific set of retail customer-service tasks under defined conditions. A strong result means it performed well on those tasks. It does not tell us whether the model has general intelligence.

“AGI-level” is also not a single, agreed benchmark. A much broader evaluation would be needed across reasoning, planning, tool use, learning, transfer to new tasks and performance in very different domains.

For a client, I would bring the discussion back to a more useful question:

> Is this system reliable enough for the business task we want to use it for?

That is something we can actually test.

---

## 3. What is one thing I could not evaluate without a human?

One area I would still want human judgement for is whether the resolution feels acceptable in a real customer interaction.

We can check whether the chatbot used the right data, followed policy, avoided hallucinations and selected a valid next step. An LLM judge can also help assess clarity and tone.

But a technically correct answer can still feel dismissive, confusing or inappropriate, especially in complaints, repeated service failures or situations involving money or personal data.

I would not use human reviewers for every case. I would use them mainly for high-risk, borderline or disputed examples. Deterministic checks and LLM-based evaluation can handle most of the volume, while human review is reserved for the cases where context and judgement matter most.