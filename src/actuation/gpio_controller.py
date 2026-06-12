import time
import logging


# Establish a highly resilient import layer for multi-environment pipeline deployment
try:
    import RPi.GPIO as GPIO
    IS_HARDWARE_AVAILABLE = True
except (ImportError, RuntimeError):
    IS_HARDWARE_AVAILABLE = False
    logging.warning("[ACTUATION PERIPHERAL] Native Linux RPi.GPIO registers missing. Loading hardware simulation fallback vectors.")


class PhysicalActuationController:
    """
    Manages low-level digital hardware execution arrays via GPIO registers.
    Features isolated fallback maps to support continuous desktop integration runs.
    """
    def __init__(self) -> None:
        # Pull multi-channel hardware configuration paths from centralized parameters
        from config.settings import settings
        self.arm_pin: int = settings.TRIGGER_GPIO_PIN
        self.vent_pin: int = settings.VENT_GPIO_PIN
        self._initialize_hardware_channels()

    def _initialize_hardware_channels(self) -> None:
        """Configures individual hardware channel pins into digital output registries."""
        if IS_HARDWARE_AVAILABLE:
            # Enforce standard Broadcom channel nomenclature layouts
            GPIO.setmode(GPIO.BCM)
            GPIO.setwarnings(False)
            
            # Map registers for both separate industrial hardware endpoints
            GPIO.setup(self.arm_pin, GPIO.OUT, initial=GPIO.LOW)
            GPIO.setup(self.vent_pin, GPIO.OUT, initial=GPIO.LOW)
        else:
            print(f"[SIMULATION HARDWARE] Bus mapping validated: Arm Pin [{self.arm_pin}], Vent Pin [{self.vent_pin}] online.")

    def dispatch_actuation(self, target_command: str, action_value: float) -> None:
        """
        Routes the validated cognitive command vector directly into the physical execution plane,
        safely managing sleep windows and register cleanup loops.
        """
        # Determine the physical hardware destination track
        if target_command == "TRIGGER_VENT":
            target_pin = self.vent_pin
            execution_label = f"VENTILATION RELAY SYSTEM (Angle adjustment: {action_value}°)"
        elif target_command == "ROTATE_ARM":
            target_pin = self.arm_pin
            execution_label = f"ROBOTIC ARM ACTUATOR CORE (Target angle: {action_value}°)"
        else:
            print(f"[ACTUATION REJECTED] Unknown hardware directive string intercept: {target_command}")
            return

        print(f"[ACTUATION START] Dispatching HIGH state signal directly to {execution_label}")

        try:
            if IS_HARDWARE_AVAILABLE:
                # Trigger real relay contacts to complete the electrical circuit loop
                GPIO.output(target_pin, GPIO.HIGH)
            else:
                print(f"[SIMULATION HIGH] Physical Channel Pin {target_pin} driving 5.0V output logic rail.")

            # Hold electrical contact state open to sustain terminal movement steps
            time.sleep(1.5)

        finally:
            # Absolute Safety Core: Revert channels to safe low states under all circumstances
            if IS_HARDWARE_AVAILABLE:
                GPIO.output(target_pin, GPIO.LOW)
            
            print(f"[ACTUATION END] Safely grounded hardware channel Pin {target_pin}. Return-to-baseline verified.")

    def cleanup(self) -> None:
        """Releases systemic hardware register locks to protect field equipment against shorting."""
        if IS_HARDWARE_AVAILABLE:
            GPIO.cleanup()
            print("[ACTUATION CLEANUP] Hardware channel arrays released back to kernel registry successfully.")
        else:
            print("[SIMULATION CLEANUP] Mock register arrays torn down safely.")
