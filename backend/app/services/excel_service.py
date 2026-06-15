import pandas as pd
from pathlib import Path
from typing import Any


def read_excel_sheets(file_path: str) -> dict[str, list[dict[str, Any]]]:
    """Read all sheets from an Excel file, return as {sheet_name: [rows]}."""
    xl = pd.ExcelFile(file_path)
    result = {}
    for sheet in xl.sheet_names:
        df = xl.parse(sheet).fillna("")
        result[sheet] = df.to_dict(orient="records")
    return result


def get_sheet_summary(file_path: str, sheet_name: str, max_rows: int = 50) -> str:
    """Return a text summary of an Excel sheet for the LLM."""
    df = pd.read_excel(file_path, sheet_name=sheet_name).fillna("")
    total_rows = len(df)
    sample = df.head(max_rows)
    lines = [
        f"Sheet: {sheet_name}",
        f"Total rows: {total_rows}",
        f"Columns: {', '.join(str(c) for c in df.columns)}",
        "",
        sample.to_string(index=False),
    ]
    return "\n".join(lines)


def search_excel(file_path: str, query: str) -> list[dict[str, Any]]:
    """Search all cells across all sheets for a keyword."""
    xl = pd.ExcelFile(file_path)
    matches = []
    for sheet in xl.sheet_names:
        df = xl.parse(sheet).fillna("")
        mask = df.apply(
            lambda col: col.astype(str).str.contains(query, case=False, na=False)
        ).any(axis=1)
        hits = df[mask].to_dict(orient="records")
        for row in hits:
            matches.append({"sheet": sheet, "row": row})
    return matches
