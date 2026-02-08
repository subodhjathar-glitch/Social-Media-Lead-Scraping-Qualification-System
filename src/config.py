"""Configuration management using pydantic-settings."""

from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )

    # YouTube API
    youtube_api_key: str
    youtube_quota_limit: int = 3330
    min_subscriber_count: int = 100000

    # OpenAI API
    openai_api_key: str
    openai_model: str = "gpt-4o-mini"
    openai_temperature: float = 0.3
    openai_max_tokens: int = 200

    # Airtable
    airtable_token: str
    airtable_base_id: str
    airtable_table_name: str = "Leads"

    # Email
    email_from: str
    email_to: str
    email_password: str

    # Scraping Configuration
    search_terms: str = "Sadhguru official,Sadhguru meditation,Sadhguru yoga"
    days_back: int = 7
    max_videos_per_channel: int = 10
    max_comments_per_video: int = 100

    @property
    def search_terms_list(self) -> List[str]:
        """Parse comma-separated search terms into a list."""
        return [term.strip() for term in self.search_terms.split(",")]

    @property
    def email_recipients(self) -> List[str]:
        """Parse comma-separated email addresses into a list."""
        return [email.strip() for email in self.email_to.split(",")]


# Global settings instance
settings = Settings()
