import asyncio
from typing import List, Dict
from types import SimpleNamespace

from google.cloud import bigquery
from google.adk.agents import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools.function_tool import FunctionTool


# =====================================================
# GOVERNED BIGQUERY TOOLS
# =====================================================

def overspend_hotlist(period: str) -> List[Dict]:
    client = bigquery.Client(project="alteryxone-dev-7393")

    query = """
    SELECT *
    FROM `alteryxone-dev-7393.bva_variance_uc.v_hook_overspend_hotlist`
    """

    rows = client.query(query).result()
    result = [dict(row) for row in rows]

    print(f"[TOOL] overspend_hotlist returned {len(result)} rows")
    return result


def variance_explain(department_name: str, period: str) -> List[Dict]:
    client = bigquery.Client(project="alteryxone-dev-7393")

    query = """
    SELECT *
    FROM `alteryxone-dev-7393.bva_variance_uc.v_hook_variance_explain`
    WHERE department_name = @department_name
    """

    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter(
                "department_name", "STRING", department_name
            )
        ]
    )

    rows = client.query(query, job_config=job_config).result()
    result = [dict(row) for row in rows]

    print(f"[TOOL] variance_explain returned {len(result)} rows")
    return result


def trend_shift_signals(period: str) -> List[Dict]:
    client = bigquery.Client(project="alteryxone-dev-7393")

    query = """
    SELECT *
    FROM `alteryxone-dev-7393.bva_variance_uc.v_hook_trend_shift_signals`
    """

    rows = client.query(query).result()
    result = [dict(row) for row in rows]

    print(f"[TOOL] trend_shift_signals returned {len(result)} rows")
    return result


# =====================================================
# TOOL REGISTRATION
# =====================================================

tools = [
    FunctionTool(overspend_hotlist),
    FunctionTool(variance_explain),
    FunctionTool(trend_shift_signals),
]


# =====================================================
# AGENT (LOCKED CONTRACT)
# =====================================================

agent = Agent(
    name="bva_agent",
    model="gemini-2.0-flash",
    tools=tools,
    instruction=(
        "You are an FP&A Budget vs Actual variance explanation agent.\n"
        "You MUST call a tool before responding.\n"
        "You MUST NOT compute totals, variances, percentages, or rankings.\n"
        "You MUST NOT invent numbers.\n"
        "You may only summarize what the tool returns.\n"
        "If no rows are returned, say exactly: "
        "'No data returned for the request.'\n"
        "Never ask follow-up questions."
    ),
)


# =====================================================
# RUNTIME
# =====================================================

session_service = InMemorySessionService()


async def main():
    await session_service.create_session(
        app_name="bva_agent_app",
        user_id="local-user",
        session_id="s1",
    )

    runner = Runner(
        app_name="bva_agent_app",
        agent=agent,
        session_service=session_service,
    )

    message = SimpleNamespace(
        role="user",
        parts=[{"text": "Show overspend hotlist for period 2024-12"}],
    )

    for event in runner.run(
        user_id="local-user",
        session_id="s1",
        new_message=message,
    ):
        if not event.content:
            continue

        for part in event.content.parts:
            if hasattr(part, "text") and part.text:
                print(part.text.strip())


if __name__ == "__main__":
    asyncio.run(main())
