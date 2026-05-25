from google.cloud import bigquery

from app.bigquery import get_bq_client
from app.settings import settings
from app.models import (
    VarianceExplainRequest,
    VarianceExplainResponse,
    VarianceExplainRow,
)

QUERY = """
SELECT
  account_rollup_l1 AS account_rollup,
  variance_direction,
  variance_amount,
  fiscal_period,
  fiscal_year
FROM `{project}.{dataset}.v_hook_variance_explain`
WHERE fiscal_year = @fiscal_year
  AND fiscal_period = @fiscal_period
  AND is_material = TRUE
ORDER BY ABS(variance_amount) DESC
"""

def run_variance_explain(
    req: VarianceExplainRequest
) -> VarianceExplainResponse:
    client = get_bq_client()

    year, period = req.period.split("-")
    fiscal_year = int(year)
    fiscal_period = int(period)

    query = QUERY.format(
        project=settings.project_id,
        dataset=settings.dataset
    )

    job_config = bigquery.QueryJobConfig(
        query_parameters=[
            bigquery.ScalarQueryParameter(
                "fiscal_year", "INT64", fiscal_year
            ),
            bigquery.ScalarQueryParameter(
                "fiscal_period", "INT64", fiscal_period
            ),
        ]
    )

    job = client.query(query, job_config=job_config)
    rows = job.result()

    result_rows = [
        VarianceExplainRow(
            account_rollup=r.account_rollup,
            driver=r.variance_direction,
            explanation=f"Variance direction: {r.variance_direction}",
            variance_amount=float(r.variance_amount),
            fiscal_period=int(r.fiscal_period),
            fiscal_year=int(r.fiscal_year),
        )
        for r in rows
    ]

    return VarianceExplainResponse(
        period=req.period,
        row_count=len(result_rows),
        rows=result_rows,
    )
