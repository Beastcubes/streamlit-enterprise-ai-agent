from google.cloud import bigquery

from app.bigquery import get_bq_client
from app.settings import settings
from app.models import (
    TrendShiftSignalsResponse,
    TrendShiftSignalRow,
)

# -------------------------------------------------
# Trend Shift Signals
# -------------------------------------------------
# SOURCE: v_hook_trend_shift_signals
# VALID COLUMNS (confirmed):
# fiscal_year, fiscal_period, fiscal_month_start_date
# budget_version, region
# drill_type, drill_key
# variance_amount
# avg_var_3m, avg_var_6m, avg_var_12m
# std_var_12m
# delta_vs_3m, delta_vs_6m, delta_vs_12m
# zscore_vs_12m
# is_trend_shift
# -------------------------------------------------

QUERY = """
SELECT
  drill_type,
  drill_key,
  variance_amount,
  delta_vs_3m,
  delta_vs_6m,
  delta_vs_12m,
  zscore_vs_12m,
  fiscal_period,
  fiscal_year
FROM `{project}.{dataset}.v_hook_trend_shift_signals`
WHERE fiscal_year = @year
  AND fiscal_period = @period
  AND is_trend_shift = TRUE
ORDER BY ABS(zscore_vs_12m) DESC
"""

def run_trend_shift_signals(req) -> TrendShiftSignalsResponse:
    client = get_bq_client()

    year = int(req.period.split("-")[0])
    period = int(req.period.split("-")[1])

    query = QUERY.format(
        project=settings.project_id,
        dataset=settings.dataset,
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
        job_id_prefix="trend_shift_signals_",
    )

    rows = job.result()

    result_rows = [
        TrendShiftSignalRow(
            account_rollup=f"{r.drill_type}: {r.drill_key}",
            metric="variance_amount",
            prior_value=float(r.delta_vs_12m * -1),
            current_value=float(r.variance_amount),
            delta=float(r.delta_vs_12m),
            fiscal_period=int(r.fiscal_period),
            fiscal_year=int(r.fiscal_year),
        )
        for r in rows
    ]

    return TrendShiftSignalsResponse(
        period=req.period,
        row_count=len(result_rows),
        rows=result_rows,
    )
