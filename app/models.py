from pydantic import BaseModel
from typing import Dict, Any, List


# -------------------------------------------------
# MCP Envelope
# -------------------------------------------------

class MCPRequest(BaseModel):
    tool: str
    args: Dict[str, Any]


# -------------------------------------------------
# Overspend Hotlist
# -------------------------------------------------

class OverspendHotlistRequest(BaseModel):
    period: str  # YYYY-MM


class OverspendRow(BaseModel):
    account_rollup: str
    actual_amount: float
    budget_amount: float
    variance_amount: float
    variance_pct: float
    fiscal_period: int
    fiscal_year: int


class OverspendHotlistResponse(BaseModel):
    period: str
    row_count: int
    rows: List[OverspendRow]


# -------------------------------------------------
# Trend Shift Signals
# -------------------------------------------------

class TrendShiftSignalsRequest(BaseModel):
    period: str


class TrendShiftSignalRow(BaseModel):
    account_rollup: str
    metric: str
    prior_value: float
    current_value: float
    delta: float
    fiscal_period: int
    fiscal_year: int


# 🔒 ALIAS — REQUIRED FOR EXISTING TOOL IMPORTS
TrendShiftRow = TrendShiftSignalRow


class TrendShiftSignalsResponse(BaseModel):
    period: str
    row_count: int
    rows: List[TrendShiftSignalRow]


# -------------------------------------------------
# Variance Explain
# -------------------------------------------------

class VarianceExplainRequest(BaseModel):
    period: str


class VarianceExplainRow(BaseModel):
    account_rollup: str
    driver: str
    explanation: str
    variance_amount: float
    fiscal_period: int
    fiscal_year: int


class VarianceExplainResponse(BaseModel):
    period: str
    row_count: int
    rows: List[VarianceExplainRow]
