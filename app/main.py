from fastapi import FastAPI
from typing import Dict, Any
from pydantic import BaseModel, ValidationError

from app.tools.overspend_hotlist import run_overspend_hotlist
from app.tools.trend_shift_signals import run_trend_shift_signals
from app.tools.variance_explain import run_variance_explain

from app.models import (
    OverspendHotlistResponse,
    TrendShiftSignalsResponse,
    VarianceExplainResponse,
)

# -------------------------------------------------
# App
# -------------------------------------------------

app = FastAPI(
    title="BvA MCP Server",
    version="1.0",
    description="Deterministic MCP tools for FP&A BvA analysis",
)

# -------------------------------------------------
# Health
# -------------------------------------------------

@app.get("/health")
def health():
    return {"status": "ok"}

# -------------------------------------------------
# MCP Envelope
# -------------------------------------------------

class MCPRequest(BaseModel):
    tool: str
    args: Dict[str, Any]

# -------------------------------------------------
# MCP Entrypoint
# -------------------------------------------------

@app.post("/mcp")
def mcp_entrypoint(request: MCPRequest):
    """
    MCP MUST NEVER CRASH.
    Always return JSON.
    """

    try:
        args = request.args or {}

        # -----------------------------
        # Normalize period
        # -----------------------------
        if "period" in args:
            period = args["period"]
        elif "year" in args and "month" in args:
            period = f"{args['year']}-{int(args['month']):02d}"
        else:
            return {
                "error": "Invalid arguments",
                "expected": "period OR year+month",
                "received": args,
            }

        req = type("Req", (), {"period": period})()

        # -----------------------------
        # Overspend Hotlist
        # -----------------------------
        if request.tool == "overspend_hotlist":
            result = run_overspend_hotlist(req)

            if not isinstance(result, OverspendHotlistResponse):
                return {"error": "Invalid response from overspend_hotlist"}

            if result.row_count == 0:
                return {
                    "period": period,
                    "row_count": 0,
                    "rows": [],
                    "message": (
                        "No data available for requested period. "
                        "Latest available data is fiscal year 2025, periods 6–9."
                    ),
                }

            return result

        # -----------------------------
        # Trend Shift Signals
        # -----------------------------
        if request.tool == "trend_shift_signals":
            result = run_trend_shift_signals(req)

            if not isinstance(result, TrendShiftSignalsResponse):
                return {"error": "Invalid response from trend_shift_signals"}

            if result.row_count == 0:
                return {
                    "period": period,
                    "row_count": 0,
                    "rows": [],
                    "message": "No trend shift signals for this period.",
                }

            return result

        # -----------------------------
        # Variance Explain
        # -----------------------------
        if request.tool == "variance_explain":
            result = run_variance_explain(req)

            if not isinstance(result, VarianceExplainResponse):
                return {"error": "Invalid response from variance_explain"}

            if result.row_count == 0:
                return {
                    "period": period,
                    "row_count": 0,
                    "rows": [],
                    "message": "No variance drivers identified for this period.",
                }

            return result

        # -----------------------------
        # Unknown tool
        # -----------------------------
        return {
            "error": f"Unknown tool: {request.tool}",
            "available_tools": [
                "overspend_hotlist",
                "trend_shift_signals",
                "variance_explain",
            ],
        }

    except ValidationError as ve:
        return {
            "error": "ValidationError",
            "details": ve.errors(),
        }

    except Exception as e:
        return {
            "error": "InternalServerError",
            "message": str(e),
        }
