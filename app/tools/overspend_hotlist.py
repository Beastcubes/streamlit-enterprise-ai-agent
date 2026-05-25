from google.cloud import bigquery

from app.bigquery import get_bq_client
from app.settings import settings
from app.models import (
    OverspendHotlistRequest,
    OverspendHotlistResponse,
    OverspendRow
)

QUERY = """
SELECT
  account_rollup_l1 AS account_rollup,
  actual_amount,
  budget_amount,
  variance_amount,
  variance_pct,
  fiscal_period,
  fiscal_year
FROM `{project}.{dataset}.v_hook_overspend_hotlist`
WHERE fiscal_year = @year
  AND fiscal_period = @period
ORDER BY variance_amount DESC
"""

LATEST_PERIOD_QUERY = """
SELECT
  fiscal_year,
  fiscal_period
FROM `{project}.{dataset}.v_hook_overspend_hotlist`
ORDER BY fiscal_year DESC, fiscal_period DESC
LIMIT 1
"""

def run_overspend_hotlist(req: OverspendHotlistRequest) -> OverspendHotlistResponse:
    client = get_bq_client()

    year, period = req.period.split("-")
    year = int(year)
    period = int(period)

    query = QUERY.format(
        project=settings.project_id,
        dataset=settings.dataset
    )

    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter("year", "INT64", year),
            bigquery.ScalarQueryParameter("period", "INT64", period),
        ]
    )

    job = client.query(
        query,
        job_config=job_config,
        job_id_prefix="overspend_hotlist_"
    )

    rows = list(job.result())

    # ----------------------------------
    # NO DATA → return informative message
    # ----------------------------------
    if not rows:
        latest_query = LATEST_PERIOD_QUERY.format(
            project=settings.project_id,
            dataset=settings.dataset
        )

        latest_job = client.query(latest_query)
        latest = list(latest_job.result())[0]

        return OverspendHotlistResponse(
            period=req.period,
            row_count=0,
            rows=[],
        )

    result_rows = [
        OverspendRow(
            account_rollup=r.account_rollup,
            actual_amount=float(r.actual_amount),
            budget_amount=float(r.budget_amount),
            variance_amount=float(r.variance_amount),
            variance_pct=float(r.variance_pct),
            fiscal_period=int(r.fiscal_period),
            fiscal_year=int(r.fiscal_year),
        )
        for r in rows
    ]

    return OverspendHotlistResponse(
        period=req.period,
        row_count=len(result_rows),
        rows=result_rows
    )
