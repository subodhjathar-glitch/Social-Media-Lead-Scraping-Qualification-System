"""Configuration management using pydantic-settings."""

import socket
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List

# Set default socket timeout to prevent hanging on network issues
socket.setdefaulttimeout(10.0)


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

    # Supabase (replaces Airtable)
    supabase_url: str
    supabase_key: str  # Anon/public key for client

    # Airtable (deprecated - kept for backward compatibility)
    airtable_token: str = ""
    airtable_base_id: str = ""
    airtable_table_name: str = "Leads"

    # Email
    email_from: str
    email_to: str
    email_password: str

    # Scraping Configuration
    search_terms: str = "Sadhguru official,Sadhguru meditation,Sadhguru yoga"
    target_channels: str = """@sadhguru,@ishafoundation,@TheMysticWorld,
        @TheWisdomofsages,@Mysticsofindia,@Shemaroospirituallife,
        @UnofficialSadhguruChannel,@simply.sadhguru,@Adiyogi1008,
        @this_is_last_time_sg,@Spiritual1Seeker,@lifeinsights,
        @EnlightenedBySadhguru,@wisechoice_fanpage,
        @TheShivGuru,@Walking.Dhyanalinga"""
    days_back: int = 7
    max_videos_per_channel: int = 10
    max_comments_per_video: int = 100

    @property
    def search_terms_list(self) -> List[str]:
        """Parse comma-separated search terms into a list."""
        return [term.strip() for term in self.search_terms.split(",")]

    @property
    def target_channels_list(self) -> List[str]:
        """Parse comma-separated channel handles into a list."""
        channels = [ch.strip() for ch in self.target_channels.replace('\n', ',').split(",")]
        return [ch for ch in channels if ch]  # Filter empty strings

    @property
    def email_recipients(self) -> List[str]:
        """Parse comma-separated email addresses into a list."""
        return [email.strip() for email in self.email_to.split(",")]


# Global settings instance
settings = Settings()
