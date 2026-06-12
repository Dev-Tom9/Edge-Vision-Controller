import base64
from typing import Optional
from pydantic import BaseModel, Field
from openai import AsyncOpenAI
from config.settings import settings


class HardwareInstructionContract(BaseModel):
    """
    Enforces a strict, type-safe JSON contract for the LLM decision engine output.
    Ensures the AI output maps perfectly to physical hardware execution layers.
    """
    trigger_actuator: bool = Field(
        ..., 
        description="Explicit boolean command stating whether physical GPIO actuation should occur."
    )
    confidence_score: float = Field(
        ..., 
        description="Model confidence calibration scalar ranging from 0.0 to 1.0."
    )
    analysis_summary: str = Field(
        ..., 
        description="Structured, technical reasoning behind the operational trigger decision."
    )


class CloudCognitionClient:
    """
    Handles cloud-native asynchronous vision intelligence pipelines.
    Enforces structured analytical contracts on non-deterministic data streams.
    """
    def __init__(self) -> None:
        # Initialize the non-blocking asynchronous OpenAI client layer
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.VISION_MODEL

    async def analyze_diagnostic_frame(self, frame_bytes: bytes) -> Optional[HardwareInstructionContract]:
        """
        Asynchronously transports base64 encoded payload to OpenAI platform.
        Enforces structured validation schemas natively at the API gate.
        """
        # Convert raw binary frame strings into standard base64 data URIs for vision models
        base64_frame = base64.b64encode(frame_bytes).decode("utf-8")
        
        try:
            response = await self.client.beta.chat.completions.parse(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are the core cognitive routing layer of an industrial automation system. "
                            "Analyze the provided image frame for anomalies, defects, safety compliance, or operational hazards. "
                            "You must strictly output structured hardware automation directives matching the schema contract."
                        )
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text", 
                                "text": "Analyze this edge diagnostic frame and output immediate system actuation directives."
                            },
                            {
                                "type": "image_url",
                                "image_url": {"url": f"data:image/jpeg;base64,{base64_frame}"}
                            }
                        ]
                    }
                ],
                response_format=HardwareInstructionContract,
                timeout=10.0 # Strict timeout boundaries to prevent systemic edge hang-ups
            )
            
            # Extract parsed structure validated perfectly via internal Pydantic compiler layers
            return response.choices[0].message.parsed
            
        except Exception as e:
            print(f"[COGNITION ERROR] Pipeline execution exception encountered: {e}")
            return None
          
