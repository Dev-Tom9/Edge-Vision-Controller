from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class ApplicationSettings(BaseSettings):
    """
    Centralized production-grade configuration layer utilizing Pydantic V2.
    Defines systemic runtime constraints, security credential targets, 
    and physical safety guardrail thresholds matching the Axon Dashboard.
    """
    
    # --- System Security Gate ---
    OPENAI_API_KEY: str = Field(
        ..., 
        description="Production API token loaded securely from host environment runtime vectors."
    )
    VISION_MODEL: str = Field(
        default="gpt-4o-mini", 
        description="Targeted multimodal vision language model core."
    )

    # --- Edge Perception Parameters ---
    CAMERA_INDEX: int = Field(
        default=0, 
        description="Hardware bus channel mapping target for local video ingestion feed."
    )
    FRAME_WIDTH: int = Field(
        default=1280, 
        description="Target horizontal matrix resolution matching dashboard video feed."
    )
    FRAME_HEIGHT: int = Field(
        default=720, 
        description="Target vertical matrix resolution matching dashboard video feed."
    )
    MOTION_THRESHOLD: int = Field(
        default=10000, 
        description="Minimum structural pixel area displacement required to trip anomaly flags."
    )

    # --- Physical Actuation Channels & Guardrails ---
    TRIGGER_GPIO_PIN: int = Field(
        default=17, 
        description="Broadcom SoC GPIO pin channel assigned to execution Relay-A (Active High)."
    )
    VENT_GPIO_PIN: int = Field(
        default=22, 
        description="Broadcom SoC GPIO pin channel assigned to execution Vent Relay (Active High)."
    )
    MAX_SAFE_ROTATION: float = Field(
        default=180.0, 
        description="Absolute physical hardware safety boundary constraint. Intercepts structural hallucinations."
    )

    # --- Pydantic Engine Settings Config ---
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


# Instantiate a secure configuration singleton for immediate global application access
settings = ApplicationSettings()
