import os
import pytest
import pandas as pd
from pathlib import Path


@pytest.fixture
def sample_excel(tmp_path):
    path = tmp_path / "test.xlsx"
    df1 = pd.DataFrame({"Name": ["Alice", "Bob"], "Amount": [1000, 2000]})
    df2 = pd.DataFrame({"Invoice": ["INV-001", "INV-002"], "Status": ["Paid", "Pending"]})
    with pd.ExcelWriter(path) as writer:
        df1.to_excel(writer, sheet_name="Employees", index=False)
        df2.to_excel(writer, sheet_name="Invoices", index=False)
    return str(path)


def test_read_excel_sheets(sample_excel):
    from app.services.excel_service import read_excel_sheets
    sheets = read_excel_sheets(sample_excel)
    assert "Employees" in sheets
    assert "Invoices" in sheets
    assert sheets["Employees"][0]["Name"] == "Alice"


def test_search_excel_found(sample_excel):
    from app.services.excel_service import search_excel
    results = search_excel(sample_excel, "Alice")
    assert len(results) == 1
    assert results[0]["sheet"] == "Employees"


def test_search_excel_not_found(sample_excel):
    from app.services.excel_service import search_excel
    results = search_excel(sample_excel, "ZZZNOMATCH")
    assert results == []


def test_get_sheet_summary(sample_excel):
    from app.services.excel_service import get_sheet_summary
    summary = get_sheet_summary(sample_excel, "Employees")
    assert "Employees" in summary
    assert "Alice" in summary
