"""
Gemini function-calling tools for the audit agent.
Tool declarations use google.genai types (new SDK).
"""
import json
from app.services.excel_service import get_sheet_summary, search_excel, read_excel_sheets
from app.services.pdf_service import extract_pdf_text, search_pdf


# ── Tool implementations ───────────────────────────────────────────────────────

def tool_list_sheets(file_path: str) -> str:
    import pandas as pd
    xl = pd.ExcelFile(file_path)
    return json.dumps({"sheets": xl.sheet_names})


def tool_read_sheet(file_path: str, sheet_name: str, max_rows: int = 50) -> str:
    return get_sheet_summary(file_path, sheet_name, max_rows)


def tool_search_excel(file_path: str, query: str) -> str:
    results = search_excel(file_path, query)
    if not results:
        return json.dumps({"message": "No matches found.", "results": []})
    return json.dumps({"count": len(results), "results": results[:20]})


def tool_read_pdf(file_path: str) -> str:
    text = extract_pdf_text(file_path)
    return text[:4000] + ("..." if len(text) > 4000 else "")


def tool_search_pdf(file_path: str, query: str) -> str:
    results = search_pdf(file_path, query)
    if not results:
        return json.dumps({"message": "No matches found.", "results": []})
    return json.dumps({"count": len(results), "results": results})


def tool_generate_audit_finding(
    finding_title: str,
    criteria: str,
    condition: str,
    cause: str,
    effect: str,
    recommendation: str,
) -> str:
    finding = {
        "finding": finding_title,
        "criteria": criteria,
        "condition": condition,
        "cause": cause,
        "effect": effect,
        "recommendation": recommendation,
    }
    return json.dumps(finding, indent=2)


def tool_create_evidence_summary(evidence_items: list[str]) -> str:
    summary = {
        "total_items": len(evidence_items),
        "evidence": [{"#": i + 1, "description": item} for i, item in enumerate(evidence_items)],
    }
    return json.dumps(summary, indent=2)


# ── Tool dispatch map ──────────────────────────────────────────────────────────

TOOL_DISPATCH = {
    "list_sheets": lambda args: tool_list_sheets(**args),
    "read_sheet": lambda args: tool_read_sheet(**args),
    "search_excel": lambda args: tool_search_excel(**args),
    "read_pdf": lambda args: tool_read_pdf(**args),
    "search_pdf": lambda args: tool_search_pdf(**args),
    "generate_audit_finding": lambda args: tool_generate_audit_finding(**args),
    "create_evidence_summary": lambda args: tool_create_evidence_summary(**args),
}

# ── google.genai Tool schema ───────────────────────────────────────────────────

TOOL_SCHEMA = {
    "function_declarations": [
        {
            "name": "list_sheets",
            "description": "List all sheet names in an Excel file",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {"type": "string", "description": "Absolute path to the Excel file"},
                },
                "required": ["file_path"],
            },
        },
        {
            "name": "read_sheet",
            "description": "Read and summarise rows from an Excel sheet",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {"type": "string"},
                    "sheet_name": {"type": "string"},
                    "max_rows": {"type": "integer", "description": "Max rows to return (default 50)"},
                },
                "required": ["file_path", "sheet_name"],
            },
        },
        {
            "name": "search_excel",
            "description": "Search all cells in an Excel file for a keyword",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {"type": "string"},
                    "query": {"type": "string"},
                },
                "required": ["file_path", "query"],
            },
        },
        {
            "name": "read_pdf",
            "description": "Extract text from a PDF document",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {"type": "string"},
                },
                "required": ["file_path"],
            },
        },
        {
            "name": "search_pdf",
            "description": "Search a PDF for a keyword and return matching page snippets",
            "parameters": {
                "type": "object",
                "properties": {
                    "file_path": {"type": "string"},
                    "query": {"type": "string"},
                },
                "required": ["file_path", "query"],
            },
        },
        {
            "name": "generate_audit_finding",
            "description": "Generate a structured audit finding with all standard fields",
            "parameters": {
                "type": "object",
                "properties": {
                    "finding_title": {"type": "string"},
                    "criteria": {"type": "string"},
                    "condition": {"type": "string"},
                    "cause": {"type": "string"},
                    "effect": {"type": "string"},
                    "recommendation": {"type": "string"},
                },
                "required": ["finding_title", "criteria", "condition", "cause", "effect", "recommendation"],
            },
        },
        {
            "name": "create_evidence_summary",
            "description": "Create a structured evidence summary table from a list of evidence descriptions",
            "parameters": {
                "type": "object",
                "properties": {
                    "evidence_items": {
                        "type": "array",
                        "items": {"type": "string"},
                    },
                },
                "required": ["evidence_items"],
            },
        },
    ]
}
