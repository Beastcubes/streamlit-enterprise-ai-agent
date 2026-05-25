import os
from pydantic import BaseModel

class Settings(BaseModel):
    project_id: str = os.getenv("GCP_PROJECT_ID", "YOUR_PROJECT_ID")
    dataset: str = os.getenv("BQ_DATASET_ID", "finance_analytics")
    location: str = os.getenv("GCP_LOCATION", "US")

settings = Settings()