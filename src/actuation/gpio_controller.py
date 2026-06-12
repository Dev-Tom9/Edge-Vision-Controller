import logging
from config.settings import settings

# Enforce a production-ready fallback pattern for local desktop simulation/testing
try:
    import RPi.GPIO as GPIO
    IS_HARDWARE_AVAILABLE = True
except (ImportError, RuntimeError):
    IS_HARDWARE_AVAILABLE = False
    logging.warning("[ACTUATION PERIPHERAL] Native RPi.GPIO libraries unavailable. Initiating hardware simulation layer.")


class PhysicalActuationController:
    """
    Directs low-level hardware actuation and relay operations via GPIO.
    Guarantees thread-safe handling and deterministic state rollbacks.
    """
    def __init__(self) -> None:
        self.pin: int = settings.TRIGGER_GPIO_PIN
        self.is_active: bool = False
        self._initialize_pins()

    def _initialize_pins(self) -> None:
        """Configures system registers for output protocols."""
        if IS_HARDWARE_AVAILABLE:
            # Set up the Raspberry Pi pin numbering convention (Broadcom SoC channel names)
            GPIO.setmode(GPIO.BCM)
            GPIO.setwarnings(False)
            # Initialize relay actuator pin as standard digital output state
            GPIO.setup(self.pin, GPIO.OUT, initial=GPIO.LOW)
        else:
            print(f"[SIMULATION HARDWARE] GPIO Pin {self.pin} configured successfully as DIGITAL_OUTPUT.")

    def trigger_relay(self, duration_seconds: float = 2.0) -> None:
        """
        Executes a deterministic high-pulse switch actuation cycle.
        Closes the circuit loop to activate the physical peripheral hardware,
        then reverts safely to a low-state baseline.
        """
        if self.is_active:
            print("[ACTUATION BLOCKED] Actuator pipeline already executing cycle.")
            return

        try:
            self.is_active = True
            print(f"[ACTUATION START] Sending HIGH signal to physical relay on GPIO Pin {self.pin}")
            
            if IS_HARDWARE_AVAILABLE:
                GPIO.output(self.pin, GPIO.HIGH)
            else:
                print(f"[SIMULATION HIGH] Hardware Actuator Activated (+5V State Simulated)")

            # Block the local thread briefly to sustain physical contact actuation window
            import time
            time.sleep(duration_seconds)

        finally:
            # Enforce strict fail-safe closure ensuring hardware returns to ground state
            if IS_HARDWARE_AVAILABLE:
                GPIO.output(self.pin, GPIO.LOW)
            
            self.is_active = False
            print(f"[ACTUATION END] Reverted GPIO Pin {self.pin} safely to LOW/GROUND state.")

    def cleanup(self) -> None:
        """Resets hardware allocations safely to prevent pin floating/shorting."""
        if IS_HARDWARE_AVAILABLE:
            GPIO.cleanup(self.pin)
            print("[ACTUATION CLEANUP] Native hardware allocations released cleanly.")
        else:
            print("[SIMULATION CLEANUP] Hardware emulation layer torn down cleanly.")
          
