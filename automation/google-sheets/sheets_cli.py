#!/usr/bin/env python3

import argparse
import base64
import json
import os
import sys
import binascii

import gspread
from dotenv import load_dotenv


DEFAULT_CREDS = os.path.expanduser("~/.config/gspread/service_account.json")

# Load .env from the repo root (parent of this module) and this folder, so the
# service-account credentials can live alongside the project's other secrets.
_HERE = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(os.path.dirname(_HERE), ".env"))
load_dotenv(os.path.join(_HERE, ".env"))


def _client():
    """Build a gspread client from, in order of preference:

    1. GOOGLE_SERVICE_ACCOUNT_B64  - base64 of the service-account JSON (.env friendly)
    2. GOOGLE_SERVICE_ACCOUNT_JSON - the raw service-account JSON string
    3. GOOGLE_SERVICE_ACCOUNT_FILE / default path - a JSON file on disk
    """
    b64 = os.environ.get("GOOGLE_SERVICE_ACCOUNT_B64")
    if b64:
        try:
            raw = base64.b64decode(b64, validate=True)
        except (binascii.Error, ValueError):
            print("GOOGLE_SERVICE_ACCOUNT_B64 is not valid base64.", file=sys.stderr)
            sys.exit(1)
        return gspread.service_account_from_dict(json.loads(raw))

    raw_json = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON")
    if raw_json:
        return gspread.service_account_from_dict(json.loads(raw_json))

    creds_path = os.environ.get("GOOGLE_SERVICE_ACCOUNT_FILE", DEFAULT_CREDS)
    if not os.path.exists(creds_path):
        print(
            "No service-account credentials found. Set GOOGLE_SERVICE_ACCOUNT_B64 "
            f"in .env, or place the key at {creds_path}.",
            file=sys.stderr,
        )
        sys.exit(1)
    return gspread.service_account(filename=creds_path)


def get_worksheet(spreadsheet_id: str, worksheet_name: str):
    spreadsheet = _client().open_by_key(spreadsheet_id)
    return spreadsheet.worksheet(worksheet_name)


def cmd_read(args):
    ws = get_worksheet(args.spreadsheet_id, args.worksheet)
    values = ws.get(args.range)
    print(json.dumps(values, indent=2, ensure_ascii=False))


def cmd_append(args):
    ws = get_worksheet(args.spreadsheet_id, args.worksheet)
    row = json.loads(args.row)

    if not isinstance(row, list):
        raise ValueError("--row must be a JSON list, e.g. '[\"Alice\", \"Paid\", 25]'")

    ws.append_row(row, value_input_option="USER_ENTERED")
    print("Appended row.")


def cmd_update(args):
    ws = get_worksheet(args.spreadsheet_id, args.worksheet)
    values = json.loads(args.values)

    if not isinstance(values, list) or not all(isinstance(r, list) for r in values):
        raise ValueError("--values must be a JSON list of lists, e.g. '[[\"Name\", \"Email\"]]'")

    # gspread 6.x signature is update(values, range_name=...).
    ws.update(values, args.range, value_input_option="USER_ENTERED")
    print(f"Updated range {args.range}.")


def cmd_rows(args):
    """Filter rows by column predicates and emit JSON with 1-based sheet row numbers.

    Uses the first row as a header. Each emitted object maps header -> value plus a
    "row" key (the 1-based sheet row, so it can be used directly in A1 ranges).
    """
    ws = get_worksheet(args.spreadsheet_id, args.worksheet)
    grid = ws.get_all_values()
    if not grid:
        print("[]")
        return
    header = grid[0]

    def col_index(name):
        if name not in header:
            raise ValueError(f"Column {name!r} not in header: {header}")
        return header.index(name)

    empty_idx = [col_index(c) for c in (args.empty or [])]
    nonempty_idx = [col_index(c) for c in (args.non_empty or [])]
    matches = []
    for spec in (args.match or []):
        if "=" not in spec:
            raise ValueError(f"--match must be COLUMN=VALUE, got {spec!r}")
        col, val = spec.split("=", 1)
        matches.append((col_index(col), val))

    def cell(row, idx):
        return row[idx].strip() if len(row) > idx else ""

    out = []
    for r in range(1, len(grid)):
        row = grid[r]
        if any(cell(row, i) for i in empty_idx):
            continue
        if any(not cell(row, i) for i in nonempty_idx):
            continue
        if any(cell(row, i) != val for i, val in matches):
            continue
        obj = {"row": r + 1}
        for i, name in enumerate(header):
            obj[name] = cell(row, i)
        out.append(obj)
    print(json.dumps(out, indent=2, ensure_ascii=False))


def main():
    parser = argparse.ArgumentParser(description="Read/write Google Sheets from Claude Code.")
    parser.add_argument("--spreadsheet-id", required=True)
    parser.add_argument("--worksheet", default="Sheet1")

    subparsers = parser.add_subparsers(dest="command", required=True)

    read = subparsers.add_parser("read")
    read.add_argument("--range", default="A1:Z100")
    read.set_defaults(func=cmd_read)

    append = subparsers.add_parser("append")
    append.add_argument("--row", required=True, help='JSON row, e.g. \'["Alice", "Paid", 25]\'')
    append.set_defaults(func=cmd_append)

    update = subparsers.add_parser("update")
    update.add_argument("--range", required=True)
    update.add_argument("--values", required=True, help='JSON list of lists, e.g. \'[["Name", "Email"]]\'')
    update.set_defaults(func=cmd_update)

    rows = subparsers.add_parser("rows", help="Filter rows by column; emits JSON with 1-based row numbers")
    rows.add_argument("--empty", action="append", metavar="COLUMN",
                      help="Keep rows where COLUMN is empty (repeatable)")
    rows.add_argument("--non-empty", action="append", metavar="COLUMN",
                      help="Keep rows where COLUMN is non-empty (repeatable)")
    rows.add_argument("--match", action="append", metavar="COLUMN=VALUE",
                      help="Keep rows where COLUMN equals VALUE (repeatable)")
    rows.set_defaults(func=cmd_rows)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
