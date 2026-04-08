from __future__ import annotations

import argparse
import csv
from pathlib import Path

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.common.enums import (
    AccountMainType,
    FinancialStatementType,
    NormalBalance,
    SubledgerType,
)
from app.modules.accounting.models.accounts import Account


def to_bool(value) -> bool:
    if isinstance(value, bool):
        return value
    text = str(value).strip().lower()
    return text in {"1", "true", "yes", "y"}


def parse_enum(enum_cls, value):
    if value is None or value == "":
        return None
    text = str(value).strip()
    for item in enum_cls:
        if item.value == text or item.name == text:
            return item
    raise ValueError(f"Invalid value '{value}' for enum {enum_cls.__name__}")


def load_rows(csv_file: Path) -> list[dict]:
    rows: list[dict] = []
    with csv_file.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if not row.get("code"):
                continue
            rows.append(
                {
                    "code": str(row["code"]).strip(),
                    "name_ar": (row.get("name_ar") or "").strip(),
                    "name_en": (row.get("name_en") or "").strip(),
                    "parent_code": (row.get("parent_code") or "").strip() or None,
                    "level": int(row["level"]),
                    "account_type": parse_enum(AccountMainType, row["account_type"]),
                    "financial_statement_type": parse_enum(FinancialStatementType, row["financial_statement_type"]),
                    "normal_balance": parse_enum(NormalBalance, row["normal_balance"]),
                    "is_postable": to_bool(row["is_postable"]),
                    "is_active": to_bool(row["is_active"]),
                    "requires_subledger": to_bool(row.get("requires_subledger", False)),
                    "subledger_type": parse_enum(SubledgerType, row.get("subledger_type") or "NONE"),
                    "allow_manual_entry": to_bool(row.get("allow_manual_entry", True)),
                    "allow_reconciliation": to_bool(row.get("allow_reconciliation", False)),
                }
            )
    rows.sort(key=lambda r: (r["level"], len(r["code"]), r["code"]))
    return rows


def validate_rows(rows: list[dict]) -> None:
    codes = {r["code"] for r in rows}
    for row in rows:
        parent_code = row["parent_code"]
        if row["level"] == 1 and parent_code is not None:
            raise ValueError(f"Level 1 account must not have parent_code: {row['code']}")
        if row["level"] > 1 and not parent_code:
            raise ValueError(f"Level {row['level']} account requires parent_code: {row['code']}")
        if parent_code:
            if parent_code not in codes:
                raise ValueError(f"Parent code '{parent_code}' not found for child '{row['code']}'")
            if len(row["code"]) <= len(parent_code):
                raise ValueError(
                    f"Child account code must be longer than parent code. child={row['code']} parent={parent_code}"
                )
        if row["is_postable"] and row["level"] != 4:
            raise ValueError(f"Posting account must be level 4: {row['code']}")
        if row["level"] < 4 and row["is_postable"]:
            raise ValueError(f"Non-leaf account cannot be postable: {row['code']}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Import COA from CSV into المحاسب المثالي")
    parser.add_argument("--file", required=True, help="Path to IMPORT_READY.csv")
    parser.add_argument("--dry-run", action="store_true", help="Validate only, do not write to DB")
    parser.add_argument("--skip-existing", action="store_true", help="Skip existing accounts by code")
    args = parser.parse_args()

    csv_file = Path(args.file)
    if not csv_file.exists():
        raise FileNotFoundError(f"File not found: {csv_file}")

    rows = load_rows(csv_file)
    validate_rows(rows)

    engine = create_engine(settings.database_url, future=True)

    with Session(engine) as db:
        existing = {
            acc.code: acc
            for acc in db.scalars(select(Account).order_by(Account.code)).all()
        }

        if args.dry_run:
            print(f"Validation successful. Rows ready: {len(rows)}")
            print(f"Existing accounts in DB: {len(existing)}")
            return

        created = 0
        skipped = 0
        code_to_id: dict[str, int] = {acc.code: acc.id for acc in existing.values()}

        for row in rows:
            if row["code"] in existing:
                if args.skip_existing:
                    skipped += 1
                    continue
                else:
                    raise ValueError(f"Account already exists: {row['code']}")

            parent_id = code_to_id.get(row["parent_code"]) if row["parent_code"] else None

            account = Account(
                code=row["code"],
                name_ar=row["name_ar"],
                name_en=row["name_en"],
                level=row["level"],
                parent_id=parent_id,
                account_type=row["account_type"],
                financial_statement_type=row["financial_statement_type"],
                normal_balance=row["normal_balance"],
                is_postable=row["is_postable"],
                requires_subledger=row["requires_subledger"],
                subledger_type=row["subledger_type"],
                allow_manual_entry=row["allow_manual_entry"],
                allow_reconciliation=row["allow_reconciliation"],
                is_active=row["is_active"],
            )
            db.add(account)
            db.flush()
            code_to_id[row["code"]] = account.id
            created += 1

        db.commit()
        print(f"Import completed successfully. Created={created}, Skipped={skipped}, Existing={len(existing)}")


if __name__ == "__main__":
    main()
