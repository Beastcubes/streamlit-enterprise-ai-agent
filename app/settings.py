from pydantic import BaseModel

class Settings(BaseModel):
    project_id: str = "env-based placeholders"
    dataset: str = "env-based placeholders"
    location: str = "US"

settings = Settings()
