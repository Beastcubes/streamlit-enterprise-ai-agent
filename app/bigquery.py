from google.cloud import bigquery
from app.settings import settings

def get_bq_client() -> bigquery.Client:
    return bigquery.Client(
        project=settings.project_id,
        location=settings.location
    )
