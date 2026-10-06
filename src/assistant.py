from __future__ import annotations

import argparse
import json
import re
from decimal import Decimal
from urllib.request import Request, urlopen

from .policy_tools import get_invoice_approvers
from .retrieve import search

OLLAMA_CHAT_URL = "http://127.0.0.1:11434/api/chat"
DEFAULT_MODEL = "qwen3:4b-instruct-2507-q4_K_M"
MIN_RELEVANCE_SCORE = 0.60


def ask_ollama(question: str, model: str = DEFAULT_MODEL) -> str:
    lowered_question = question.lower()

    is_invoice_approval_question = (
        "invoice" in lowered_question
        and (
            "approve" in lowered_question
            or "approval" in lowered_question
            or "approver" in lowered_question
        )
    )

    amount_match = re.search(
        r"\$?\s*([\d,]+(?:\.\d{1,2})?)",
        question,
    )

    if is_invoice_approval_question and amount_match:
        amount = Decimal(amount_match.group(1).replace(",", ""))
        rule_result = get_invoice_approvers(amount)
        approvers = " and ".join(rule_result["approvers"])

        return (
            f"A {rule_result['currency']} {rule_result['amount']} invoice "
            f"requires approval from the {approvers}. [1]\n\n"
            "Retrieved sources:\n"
            f"[1] [{rule_result['source']} · "
            f"{rule_result['section']}]"
        )

    results = [
        result
        for result in search(question, top_k=3)
        if result.score >= MIN_RELEVANCE_SCORE
    ]

    if not results:
        return (
            "I could not find that information in the available "
            "company documents."
        )

    context_sections = []
    citations = []

    for number, result in enumerate(results, start=1):
        context_sections.append(
            f"[{number}] {result.citation}\n"
            f"{result.metadata['text']}"
        )
        citations.append(f"[{number}] {result.citation}")

    context = "\n\n".join(context_sections)

    system_prompt = """
You are a company knowledge assistant.

Answer using only the supplied company-document passages.

Rules:
1. Cite every factual claim using citations such as [1] or [2].
2. Never use outside knowledge.
3. If the passages do not support an answer, say:
   "I could not find that information in the available company documents."
4. Do not invent policies, numbers, dates, approvals, or exceptions.
5. Keep the answer concise and practical.
6. Preserve every number from the user's question exactly.
7. Do not substitute a source threshold for the user's value.
""".strip()

    user_prompt = f"""
QUESTION:
{question}

RETRIEVED COMPANY PASSAGES:
{context}

Answer the exact question above using only the retrieved passages.
""".strip()

    payload = json.dumps(
        {
            "model": model,
            "stream": False,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "options": {
                "temperature": 0,
            },
        }
    ).encode("utf-8")

    request = Request(
        OLLAMA_CHAT_URL,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urlopen(request, timeout=180) as response:
            result = json.loads(response.read().decode("utf-8"))
    except Exception as exc:
        raise RuntimeError(
            "Could not reach Ollama. Confirm Ollama is running "
            f"and that {model} is installed."
        ) from exc

    answer = result["message"]["content"].strip()

    return (
        f"{answer}\n\n"
        "Retrieved sources:\n"
        + "\n".join(citations)
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Answer questions using retrieved company evidence."
    )
    parser.add_argument("question")
    parser.add_argument("--model", default=DEFAULT_MODEL)
    args = parser.parse_args()

    print(ask_ollama(args.question, args.model))


if __name__ == "__main__":
    main()