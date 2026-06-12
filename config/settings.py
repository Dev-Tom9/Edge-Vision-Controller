import os
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class EdgeSystemSettings(BaseSettings):
    """
    High-fidelity configuration management for the Edge AI Controller.
    Enforces type safety and system-wide constants at initialization.
    """
    # OpenAI Platform Configuration
    OPENAI_API_KEY: str = Field(
        ..., 
        description="Bearer token for OpenAI API authenticated requests."
    )
    VISION_MODEL: str = Field(
        default="gpt-4o-mini", 
        description="LLM engine used for contextual visual processing."
    )
    
    # Hardware & Peripheral Configuration
    CAMERA_INDEX: int = Field(
        default=0, 
        description="Local system index for the primary video capture hardware."
    )
    TRIGGER_GPIO_PIN: int = Field(
        default=18, 
        description="BCM pin layout designation for physical actuator relay."
    )
    
    # Vision Pipeline Thresholds
    FRAME_WIDTH: int = Field(default=640, description="Downsampled frame width for optimization.")
    FRAME_HEIGHT: int = Field(default=480, description="Downsampled frame height for optimization.")
    MOTION_THRESHOLD: int = Field(default=10000, description="Minimum contour area delta to trigger anomaly.")

    # Configuration Metadata
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


# Instantiate a singleton instance for cross-module usage
try:
    settings = EdgeSystemSettings()
except Exception as e:
    # Fallback pattern for GitHub profile display purposes if .env isn't local yet
    print(f"[PRE-FLIGHT WARNING]: Missing environment configurations: {e}")
    # Mock fallback to prevent strict initialization failure during raw inspection
    os.environ["OPENAI_API_KEY"] = "mock_key_for_repository_inspection"
    settings = EdgeSystemSettings()
  
