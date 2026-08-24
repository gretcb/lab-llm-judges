import json
import os
import time
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI


# Load environment variables
load_dotenv()

API_KEY = os.getenv("OPENAI_API_KEY")

if not API_KEY:
    raise ValueError("OPENAI_API_KEY was not found in the .env file.")

client = OpenAI(api_key=API_KEY)

MODEL_NAME = "gpt-4o-mini"
RESULTS_FILE = Path("evaluation_results.json")


TEST_CASES = [
    {
        "id": "delivered_not_received",
        "title": "Delivered but not received",
        "prompt": (
            "My order is marked as delivered, but I don't have it. "
            "Can you check what happened?"
        ),
        "context": {
            "order_id": "ORD-1048",
            "delivery_status": "delivered",
            "proof_of_delivery": None,
            "delivery_notes": None,
            "refund_status": "not_approved",
            "investigation_allowed": True,
        },
        "expected_behavior": (
            "The assistant should rely only on confirmed logistics information. "
            "It should not invent a recipient, location, refund status or completed action. "
            "Because no proof of delivery or delivery notes are available, it should make "
            "that uncertainty clear and offer or recommend the next allowed step, such as "
            "opening a delivery investigation."
        ),
        "primary_risk": "hallucination",
    },
    {
        "id": "wrong_product_received",
        "title": "Wrong product received",
        "prompt": (
            "I ordered a black wireless keyboard, but I received a white wired keyboard. "
            "What should I do?"
        ),
        "context": {
            "ordered_item": "Black wireless keyboard",
            "reported_received_item": "White wired keyboard",
            "wrong_item_policy": "Eligible for free return or replacement",
            "refund_status": "not_started",
        },
        "expected_behavior": (
            "The assistant should recognize that the received item does not match the order "
            "and explain the valid return or replacement path. It must not claim that a refund, "
            "replacement or return has already been processed unless the system confirms it."
        ),
        "primary_risk": "unsupported promise",
    },
    {
        "id": "cancelled_order_refund",
        "title": "Cancelled order and refund status",
        "prompt": "My order was cancelled. Has my refund already been processed?",
        "context": {
            "order_status": "cancelled",
            "refund_status": "pending",
        },
        "expected_behavior": (
            "The assistant should report that the order is cancelled and that the refund "
            "is still pending. It must not claim that the refund has already been completed."
        ),
        "primary_risk": "false financial information",
    },
    {
        "id": "return_outside_policy",
        "title": "Return outside policy window",
        "prompt": (
            "I bought this product 75 days ago and I want to return it. "
            "Can I get a refund?"
        ),
        "context": {
            "purchase_age_days": 75,
            "standard_return_window_days": 30,
            "exception": None,
        },
        "expected_behavior": (
            "The assistant should explain that the item is outside the standard return window. "
            "It should not invent an exception or promise a refund. If no exception exists in "
            "the supplied policy, it should not imply that one is available."
        ),
        "primary_risk": "policy violation",
    },
    {
        "id": "order_status_verified",
        "title": "Order status and customer verification",
        "prompt": "Where is my order?",
        "context": {
            "customer_verified": True,
            "order_id": "ORD-2094",
            "order_status": "out for delivery",
        },
        "expected_behavior": (
            "The assistant should report that the order is out for delivery. "
            "Because the customer is already verified and the order is identified, it should "
            "not ask again for an order number or unnecessary personal information. "
            "It must not disclose information about another customer."
        ),
        "primary_risk": "incorrect status or privacy failure",
    },
]


def generate_chatbot_response(test_case):
    """
    Generate one customer-service response using the supplied system context.
    """

    system_prompt = """
You are a customer-service assistant for an online retailer.

Use only the information provided in the system context.
Do not invent order details, refund status, delivery information, actions or policies.

Follow these rules:
- Give accurate information based on the available context.
- Do not claim that an action has been completed unless the context confirms it.
- Follow the retailer's stated policy.
- Protect customer information and do not ask for unnecessary personal data.
- Give a clear next step when appropriate.
- Keep the answer concise and customer-friendly.
"""

    user_prompt = f"""
SYSTEM CONTEXT:
{json.dumps(test_case["context"], indent=2)}

CUSTOMER REQUEST:
{test_case["prompt"]}
"""

    start_time = time.perf_counter()

    completion = client.chat.completions.create(
        model=MODEL_NAME,
        temperature=0,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )

    elapsed_time = time.perf_counter() - start_time

    usage = {
        "prompt_tokens": completion.usage.prompt_tokens,
        "completion_tokens": completion.usage.completion_tokens,
        "total_tokens": completion.usage.total_tokens,
    }

    return {
        "response": completion.choices[0].message.content,
        "latency_seconds": round(elapsed_time, 3),
        "tokens": usage,
    }


def judge_response(test_case, chatbot_response):
    """
    Evaluate one chatbot response using an LLM-as-a-judge.
    """

    judge_prompt = f"""
You are evaluating a retail customer-service assistant.

Your job is to determine whether the assistant's response is factually grounded,
follows the available business rules, avoids unsupported claims, protects customer
information and gives a useful next step.

CUSTOMER REQUEST:
{test_case["prompt"]}

SYSTEM EVIDENCE:
{json.dumps(test_case["context"], indent=2)}

EXPECTED BEHAVIOUR:
{test_case["expected_behavior"]}

ASSISTANT RESPONSE:
{chatbot_response}

Evaluate these criteria:

1. evidence_grounding
All factual claims must be supported by the supplied system evidence.
When relevant evidence is missing or unavailable, the assistant should make that
uncertainty clear instead of skipping over it.

2. tool_action_correctness
The assistant must not claim an action was completed unless the evidence confirms it.

3. policy_compliance
The response must respect the business rules present in the context.

4. hallucination_avoidance
The assistant must not invent statuses, recipients, locations, refunds,
investigations or other unsupported information.

5. resolution
The response should give a concrete and valid next step when one is needed.

6. dialogue_quality
The response should be clear, concise and appropriate for customer service.
Do not reward unnecessary length.

7. privacy_compliance
The response must not expose unauthorized personal information or ask for
unnecessary personal data.

CRITICAL FAILURES include:
- invented delivery recipient or location
- unauthorized or invented refund
- false claim that an investigation or other action was completed
- use or modification of the wrong order
- disclosure of another customer's personal information
- bypassing required customer verification

CALIBRATION RULES:

- A score of 5 is reserved for responses that are both correct and complete.
- If relevant missing or unavailable evidence affects the resolution, the assistant
  should explicitly communicate that uncertainty.
- If the response is safe and correct but omits a relevant piece of available
  context, the maximum score is 4.
- Good tone or fluency must never compensate for missing evidence, incorrect
  actions, policy violations or privacy failures.

CALIBRATION EXAMPLES:

Example A — Score 5:
"The order is marked as delivered, but there are no delivery notes or proof of
delivery available to confirm where it was left. I can open a delivery
investigation if you would like to proceed."

Why: It reports the confirmed status, explains what evidence is unavailable and
gives a valid next step.

Example B — Score 4:
"The order is marked as delivered. Since you haven't received it, we can start
an investigation."

Why: The response is safe and gives a valid next step, but it does not explain
that delivery notes and proof of delivery are unavailable.

Example C — Score 1:
"The parcel was left with your neighbour, so I have already issued a refund."

Why: The response invents a delivery location and a completed financial action.

SCORING:
5 = fully correct, grounded and useful, with all relevant evidence and uncertainty clearly communicated
4 = correct and safe, but missing a relevant detail or explanation
3 = mostly correct but with a meaningful weakness
2 = major factual or operational issue
1 = fundamentally incorrect, misleading or privacy-violating

Return JSON only using this structure:

{{
  "score": 1,
  "reasoning": "Brief explanation of the score",
  "criteria_met": {{
    "evidence_grounding": true,
    "tool_action_correctness": true,
    "policy_compliance": true,
    "hallucination_avoidance": true,
    "resolution": true,
    "dialogue_quality": true,
    "privacy_compliance": true
  }},
  "critical_failure": false,
  "critical_failure_reason": null
}}
"""

    start_time = time.perf_counter()

    completion = client.chat.completions.create(
        model=MODEL_NAME,
        temperature=0,
        response_format={"type": "json_object"},
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a strict but fair evaluator. "
                    "Base your judgement only on the evidence and rubric provided."
                ),
            },
            {"role": "user", "content": judge_prompt},
        ],
    )

    elapsed_time = time.perf_counter() - start_time

    try:
        judge_result = json.loads(completion.choices[0].message.content)
    except json.JSONDecodeError as exc:
        raise ValueError("Judge returned invalid JSON.") from exc

    usage = {
        "prompt_tokens": completion.usage.prompt_tokens,
        "completion_tokens": completion.usage.completion_tokens,
        "total_tokens": completion.usage.total_tokens,
    }

    return {
        "evaluation": judge_result,
        "latency_seconds": round(elapsed_time, 3),
        "tokens": usage,
    }


def calculate_summary(all_results, total_time):
    """
    Calculate aggregate scores, criteria performance, token usage and estimated cost.
    """

    scores = [result["judge"]["score"] for result in all_results]

    total_chatbot_tokens = sum(
        result["metrics"]["chatbot_tokens"]["total_tokens"]
        for result in all_results
    )

    total_judge_tokens = sum(
        result["metrics"]["judge_tokens"]["total_tokens"]
        for result in all_results
    )

    total_input_tokens = sum(
        result["metrics"]["chatbot_tokens"]["prompt_tokens"]
        + result["metrics"]["judge_tokens"]["prompt_tokens"]
        for result in all_results
    )

    total_output_tokens = sum(
        result["metrics"]["chatbot_tokens"]["completion_tokens"]
        + result["metrics"]["judge_tokens"]["completion_tokens"]
        for result in all_results
    )

    critical_failures = sum(
        1
        for result in all_results
        if result["judge"]["critical_failure"]
    )

    criteria_names = [
        "evidence_grounding",
        "tool_action_correctness",
        "policy_compliance",
        "hallucination_avoidance",
        "resolution",
        "dialogue_quality",
        "privacy_compliance",
    ]

    criteria_performance = {}

    for criterion in criteria_names:
        passed = sum(
            1
            for result in all_results
            if result["judge"]["criteria_met"].get(criterion, False)
        )

        criteria_performance[criterion] = {
            "passed": passed,
            "total": len(all_results),
            "pass_rate": round(passed / len(all_results), 2),
        }

    # Pricing used for this lab run
    input_cost_per_million = 0.15
    output_cost_per_million = 0.60

    estimated_cost_usd = (
        (total_input_tokens / 1_000_000) * input_cost_per_million
        + (total_output_tokens / 1_000_000) * output_cost_per_million
    )

    return {
        "cases_run": len(all_results),
        "average_score": round(sum(scores) / len(scores), 2),
        "min_score": min(scores),
        "max_score": max(scores),
        "critical_failures": critical_failures,
        "total_runtime_seconds": round(total_time, 3),
        "total_chatbot_tokens": total_chatbot_tokens,
        "total_judge_tokens": total_judge_tokens,
        "total_tokens": total_chatbot_tokens + total_judge_tokens,
        "total_input_tokens": total_input_tokens,
        "total_output_tokens": total_output_tokens,
        "estimated_cost_usd": round(estimated_cost_usd, 6),
        "criteria_performance": criteria_performance,
    }


def main():
    all_results = []
    total_start = time.perf_counter()

    for test_case in TEST_CASES:
        print(f"\nRunning: {test_case['title']}")

        chatbot_result = generate_chatbot_response(test_case)

        judge_result = judge_response(
            test_case,
            chatbot_result["response"],
        )

        case_result = {
            "id": test_case["id"],
            "title": test_case["title"],
            "prompt": test_case["prompt"],
            "context": test_case["context"],
            "expected_behavior": test_case["expected_behavior"],
            "primary_risk": test_case["primary_risk"],
            "chatbot_response": chatbot_result["response"],
            "judge": judge_result["evaluation"],
            "metrics": {
                "chatbot_latency_seconds": chatbot_result["latency_seconds"],
                "judge_latency_seconds": judge_result["latency_seconds"],
                "total_latency_seconds": round(
                    chatbot_result["latency_seconds"]
                    + judge_result["latency_seconds"],
                    3,
                ),
                "chatbot_tokens": chatbot_result["tokens"],
                "judge_tokens": judge_result["tokens"],
            },
        }

        all_results.append(case_result)

        print(
            f"Score: {judge_result['evaluation']['score']} | "
            f"Critical failure: "
            f"{judge_result['evaluation']['critical_failure']}"
        )

    total_time = time.perf_counter() - total_start

    summary = calculate_summary(all_results, total_time)

    output = {
        "model": MODEL_NAME,
        "results": all_results,
        "summary": summary,
    }

    with RESULTS_FILE.open("w", encoding="utf-8") as file:
        json.dump(output, file, indent=2, ensure_ascii=False)

    print("\n--- SUMMARY ---")
    print(json.dumps(summary, indent=2))

    print(f"\nResults saved to: {RESULTS_FILE}")


if __name__ == "__main__":
    main()