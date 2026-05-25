MCP_TOOLS = [
    {
        "name": "overspend_hotlist",
        "description": "Returns top overspending accounts for a given fiscal period.",
        "endpoint": "/tools/overspend_hotlist",
        "method": "POST",
        "input_schema": {
            "type": "object",
            "properties": {
                "period": {
                    "type": "string",
                    "description": "Fiscal period in YYYY-MM format"
                }
            },
            "required": ["period"]
        }
    },
    {
        "name": "variance_explain",
        "description": "Explains Budget vs Actual variances for a department and period.",
        "endpoint": "/tools/variance_explain",
        "method": "POST",
        "input_schema": {
            "type": "object",
            "properties": {
                "period": {"type": "string"},
                "department": {"type": "string"}
            },
            "required": ["period", "department"]
        }
    },
    {
        "name": "trend_shift_signals",
        "description": "Detects trend shifts across cost centers, GLs, and P&L categories.",
        "endpoint": "/tools/trend_shift_signals",
        "method": "POST",
        "input_schema": {
            "type": "object",
            "properties": {
                "period": {"type": "string"}
            },
            "required": ["period"]
        }
    }
]
