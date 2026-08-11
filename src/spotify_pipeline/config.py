# src/spotify_pipeline/config.py
from pydantic_settings import BaseSettings
from pydantic import Field

class PipelineConfig(BaseSettings):
    # Spotify API
    spotify_client_id: str = Field(description="Spotify Client ID")
    spotify_client_secret: str = Field(description="Spotify Client Secret")

    # AWS
    aws_bucket_raw: str = Field(description="S3 Bronze bucket")
    aws_bucket_transformed: str = Field(description="S3 Silver/Gold bucket")
    aws_region: str = Field(default="us-east-1")
    aws_access_key_id: str = Field(description="AWS Access Key ID")
    aws_secret_access_key: str = Field(description="AWS Secret Access Key")

    # Pipeline
    environment: str = Field(default="development")
    batch_size: int = Field(default=50)
    max_retries: int = Field(default=3)


    @property
    def is_production(self) -> bool:
        return self.environment == "production"

    model_config = {
        "env_file": ".env",
        "case_sensitive": False,
        "extra": "ignore"
    }

config = PipelineConfig()