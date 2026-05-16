"""Configuration management for CodeLens"""

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    app_name: str = "CodeLens"
    app_version: str = "0.1.0"
    debug: bool = False
    
    # Database
    database_url: str = "sqlite:///./codelens.db"
    
    # Server Configuration
    api_host: str = "127.0.0.1"
    api_port: int = 8000
    frontend_url: str = "http://localhost:5173"
    
    # Watsonx.ai Configuration
    watsonx_api_key: Optional[str] = None
    watsonx_project_id: Optional[str] = None
    watsonx_url: str = "https://us-south.ml.cloud.ibm.com"
    watsonx_model_id: str = "ibm/granite-13b-chat-v2"
    watsonx_embedding_model_id: str = "ibm/granite-embedding-278m-multilingual"
    watsonx_answering_model_id: str = "meta-llama/llama-3-3-70b-instruct"
    
    # GitHub Configuration (optional)
    github_token: Optional[str] = None
    
    # Analysis Settings
    max_file_size_mb: int = 10
    supported_languages: str = "python,javascript,typescript"
    analysis_timeout_seconds: int = 300
    max_workers: int = 4
    
    # AI Settings
    max_tokens: int = 2048
    temperature: float = 0.3
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()

# Made with Bob
