import os
import json
import re
import requests
import google.genai as genai

# -------------------------------------------------
# MCP endpoint
# -------------------------------------------------

MCP_URL = "http://localhost:8080/mcp"

# -------------------------------------------------
# Gemini client (Vertex AI)
# -------------------------------------------------

client = genai.Client(
    vertexai=True,
    project=os.environ.get("GOOGLE_CLOUD_PROJECT", "alteryxone-dev-7393"),
    location=os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1"),
)

# -------------------------------------------------
# SYSTEM PROMPT — TOOL ROUTING ONLY
# -------------------------------------------------

SYSTEM_PROMPT = """
You are a STRICT tool router.

You MUST return ONLY valid JSON.
NO markdown.
NO code fences.
NO explanations.

Allowed tools:
- overspend_hotlist
- trend_shift_signals
- variance_explain

Schemas:

overspend_hotlist:
{
  "tool": "overspend_hotlist",
  "args": { "period": "YYYY-MM" }
}

trend_shift_signals:
{
  "tool": "trend_shift_signals",
  "args": { "period": "YYYY-MM" }
}

variance_explain:
{
  "tool": "variance_explain",
  "args": { "period": "YYYY-MM" }
}
"""

# -------------------------------------------------
# NARRATIVE PROMPT — READ-ONLY SYNTHESIS
# -------------------------------------------------

NARRATIVE_PROMPT = """
You are a CFO commentary generator.

You will be given structured financial results in JSON.
Your job is to write a concise executive-ready explanation.

Rules:
- Do NOT invent numbers
- Do NOT add new insights
- Do NOT infer causes beyond the data
- Do NOT reference tools, SQL, or systems
- Use professional FP&A language
- Be concise (3–6 sentences)

Focus on:
- What changed
- Why it matters
- Where management should look

If rows are empty:
- Clearly state that no data exists for the requested period
"""

# -------------------------------------------------
# Intent validation (NEW — HARD GUARDRAIL)
# -------------------------------------------------

VALID_KEYWORDS = [
    "overspend", "variance", "trend", "shift",
    "budget", "actual", "driver", "explain",
    "spending", "cost", "expense"
]

DATE_PATTERN = re.compile(
    r"(20\d{2})|jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec",
    re.IGNORECASE,
)

def is_valid_fpna_question(question: str) -> bool:
    q = question.lower()
    has_keyword = any(k in q for k in VALID_KEYWORDS)
    has_date = bool(DATE_PATTERN.search(q))
    return has_keyword and has_date

# -------------------------------------------------
# Helpers
# -------------------------------------------------

ALLOWED_TOOLS = {
    "overspend_hotlist",
    "trend_shift_signals",
    "variance_explain",
}

def _clean_json(text: str) -> str:
    text = text.strip()
    text = re.sub(r"^```(?:json)?", "", text)
    text = re.sub(r"```$", "", text)
    return text.strip()

def call_mcp(tool: str, args: dict):
    resp = requests.post(
        MCP_URL,
        json={"tool": tool, "args": args},
        timeout=30,
    )
    resp.raise_for_status()
    return resp.json()

# -------------------------------------------------
# Narrative synthesis
# -------------------------------------------------

def synthesize_commentary(question: str, mcp_result: dict) -> str:
    prompt = f"""
{NARRATIVE_PROMPT}

Original question:
{question}

MCP result:
{json.dumps(mcp_result, indent=2)}
"""

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt,
    )

    if not response.text:
        raise RuntimeError("Empty narrative response")

    return response.text.strip()

# -------------------------------------------------
# Public API
# -------------------------------------------------

def ask(question: str):

    # ---------- HARD INTENT GATE ----------
    if not is_valid_fpna_question(question):
        return {
            "data": {},
            "commentary": (
                "Please ask a clear FP&A question that includes a time period, "
                "such as a month or year. For example: "
                "“Explain overspend in September 2025.”"
            ),
        }

    # ---------- Stage 1: Tool routing ----------
    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=f"{SYSTEM_PROMPT}\n\nUser question: {question}",
    )

    if not response.text:
        raise RuntimeError("Empty response from model")

    cleaned = _clean_json(response.text)

    try:
        payload = json.loads(cleaned)
    except Exception:
        raise RuntimeError(f"Model returned invalid JSON:\n{cleaned}")

    tool = payload.get("tool")
    args = payload.get("args", {})

    if tool not in ALLOWED_TOOLS:
        raise RuntimeError(f"Invalid or missing tool: {tool}")

    # Normalize period
    if "period" not in args:
        if "year" in args and "month" in args:
            args["period"] = f"{args['year']}-{int(args['month']):02d}"
        else:
            raise RuntimeError(f"Invalid args: {args}")

    # ---------- Stage 2: Deterministic MCP ----------
    mcp_result = call_mcp(tool, args)

    # ---------- Stage 3: Narrative synthesis ----------
    commentary = synthesize_commentary(question, mcp_result)

    return {
        "data": mcp_result,
        "commentary": commentary,
    }
