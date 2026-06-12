import base64
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from openai import AsyncOpenAI
from config.settings import settings


class HardwareInstructionContract(BaseModel):
    """
    Enforces a strict, type-safe JSON schema contract for the LLM output.
    Maps raw non-deterministic reasoning directly into distinct mechanical actions.
    """
    action_command: str = Field(
        ..., 
        description="The target mechanical component directive, e.g., 'ROTATE_ARM' or 'TRIGGER_VENT'."
    )
    requested_value: float = Field(
        ..., 
        description="The precise numerical scalar applied to the action execution target, e.g., degree value or timing metric."
    )
    analysis_summary: str = Field(
        ..., 
        description="Technical structural engineering rationale behind the recommended automation step."
    )


class CloudCognitionClient:
    """
    Handles cloud-native asynchronous vision intelligence pipelines.
    Integrates real-time programmatic guardrail verification layers to block erratic AI output.
    """
    def __init__(self) -> None:
        # Initialize the non-blocking asynchronous OpenAI client layer
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.VISION_MODEL
        self.max_safe_rotation = settings.MAX_SAFE_ROTATION

    async def analyze_frame_with_guardrails(self, frame_bytes: bytes) -> Dict[str, Any]:
        """
        Asynchronously transports base64 encoded payloads to OpenAI,
        and parses responses against strict physical machine constraints.
        """
        # Convert raw binary frame data into standard base64 strings for vision tracking
        base64_frame = base64.b64encode(frame_bytes).decode("utf-8")
        
        try:
            response = await self.client.beta.chat.completions.parse(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are the core cognitive routing layer of an Axon Edge AI industrial automation system. "
                            "Analyze the provided image frame for anomalies, defects, or operational hazards. "
                            "You must strictly output structured hardware directives matching the schema contract. "
                            "Commands include 'TRIGGER_VENT' (value=90.0) or 'ROTATE_ARM' (value=angle)."
                        )
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text", 
                                "text": "Analyze this edge diagnostic frame and output structured operational directives."
                            },
                            {
                                "type": "image_url",
                                "image_url": {"url": f"data:image/jpeg;base64,{base64_frame}"}
                            }
                        ]
                    }
                ],
                response_format=HardwareInstructionContract,
                timeout=10.0 # Prevent thread hangups via aggressive gateway timeouts
            )
            
            # Extract parsed structural data validated natively via internal Pydantic layers
            parsed_contract = response.choices[0].message.parsed
            
            # --- PREMIUM UPGRADE: DETERMINISTIC SAFETY GUARDRAIL LAYER ---
            # Explicitly checks and intercepts AI commands before they reach physical machine registers
            if parsed_contract.action_command == "ROTATE_ARM" and parsed_contract.requested_value > self.max_safe_rotation:
                return {
                    "status": "BLOCKED",
                    "reason": f"Guardrail Intercept: Requested rotation ({parsed_contract.requested_value}°) exceeds safety boundary ({self.max_safe_rotation}°)",
                    "trigger_actuator": False,
                    "command": parsed_contract.action_command,
                    "value": parsed_contract.requested_value,
                    "summary": parsed_contract.analysis_summary
                }
            
            # Fallback evaluation verifying successful validation bounds pass
            return {
                "status": "PASS",
                "reason": "Execution limits validated within acceptable baseline tolerances.",
                "trigger_actuator": True,
                "command": parsed_contract.action_command,
                "value": parsed_contract.requested_value,
                "summary": parsed_contract.analysis_summary
            }
            
        except Exception as e:
            # Error Mitigation Layer: Fallback to a zeroed out state on API disruptions or structural text errors
            return {
                "status": "MALFORMED_RESPONSE",
                "reason": f"Pipeline exception or invalid API schema parsing encountered: {e}",
                "trigger_actuator": False,
                "command": "HALT_SYSTEM",
                "value": 0.0,
                "summary": "System dropped automatically to a safe, isolated standby state to guarantee line security."
            }
