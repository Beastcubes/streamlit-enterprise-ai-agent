from pydantic import BaseModel

class Settings(BaseModel):
    project_id: str = "alteryxone-dev-7393"
    dataset: str = "bva_variance_uc"
    location: str = "US"

settings = Settings()
