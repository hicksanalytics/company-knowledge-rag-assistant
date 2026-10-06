from __future__ import annotations

import argparse
import json
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RULES = ROOT / "data" / "rules" / "invoice_approval.json"


def get_invoice_approvers(
    amount: Decimal,
    rules_path: Path = DEFAULT_RULES,
) -> dict:
    policy = json.loads(rules_path.read_text(encoding="utf-8"))

    for rule in policy["rules"]:
        minimum = Decimal(str(rule["minimum_exclusive"]))
        maximum_value = rule["maximum_inclusive"]
        maximum = (
            Decimal(str(maximum_value))
            if maximum_value is not None
            else None
        )

        above_minimum = amount > minimum
        below_maximum = maximum is None or amount <= maximum

        if above_minimum and below_maximum:
            return {
                "amount": f"{amount:,.2f}",
                "currency": policy["currency"],
                "approvers": rule["approvers"],
                "source": policy["source"],
                "section": policy["section"],
            }

    raise ValueError(f"No approval rule matched amount {amount}")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Apply deterministic invoice approval rules."
    )
    parser.add_argument("amount", type=Decimal)
    args = parser.parse_args()

    result = get_invoice_approvers(args.amount)
    approvers = " and ".join(result["approvers"])

    print(
        f"A {result['currency']} {result['amount']} invoice requires "
        f"approval from: {approvers}."
    )
    print(
        f"[{result['source']} · {result['section']}]"
    )


if __name__ == "__main__":
    main()