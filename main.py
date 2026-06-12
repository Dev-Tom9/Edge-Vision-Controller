import asyncio
import sys
import signal
from src.perception.vision_engine import FramePerceptionEngine
from src.cognition.llm_client import CloudCognitionClient
from src.actuation.gpio_controller import PhysicalActuationController


class EdgeAISystemOrchestrator:
    """
    Asynchronous runtime orchestrator managing the core perception-cognition-actuation loop.
    Enforces concurrency boundaries and clean lifecycle tear-downs.
    """
    def __init__(self) -> None:
        self.perception = FramePerceptionEngine()
        self.cognition = CloudCognitionClient()
        self.actuation = PhysicalActuationController()
        self.is_running = True

    def register_lifecycle_signals(self) -> None:
        """Binds system termination signals to ensure deterministic shutdowns."""
        for sig in (signal.SIGINT, signal.SIGTERM):
            try:
                loop = asyncio.get_running_loop()
                loop.add_signal_handler(sig, self.initiate_graceful_shutdown)
            except NotImplementedError:
                # Signal handlers are not fully implemented in some non-Linux development environments
                pass

    def initiate_graceful_shutdown(self) -> None:
        """Gracefully halts execution loops and safely releases peripheral hooks."""
        print("\n[SYSTEM SHUTDOWN] Termination signal intercepted. Cleaning up resources...")
        self.is_running = False

    async def execution_loop(self) -> None:
        """Main non-blocking execution cycle tracking real-time frames and triggers."""
        print("[SYSTEM STARTUP] Initializing video ingestion streams...")
        try:
            video_capture = self.perception.initialize_camera()
        except Exception as e:
            print(f"[CRITICAL ERROR] Hardware failure initializing camera module: {e}")
            self.actuation.cleanup()
            sys.exit(1)

        print("[SYSTEM READY] Asynchronous Edge Automation Loop Active.")
        self.register_lifecycle_signals()

        try:
            while self.is_running:
                # Capture frame from hardware buffer
                success, frame = video_capture.read()
                if not success:
                    print("[PERCEPTION WARNING] Dropped frame detected from device stream channel.")
                    await asyncio.sleep(0.1)
                    continue

                # Execute local computer vision anomaly filtration algorithm
                anomaly_detected, optimized_frame_bytes = self.perception.process_and_validate_frame(frame)

                if anomaly_detected:
                    print("[EDGE EVENT] Anomaly threshold crossed. Initiating cloud cognition bridge...")
                    
                    # Run the cognitive analysis concurrently without freezing the primary system loop
                    decision = await self.cognition.analyze_diagnostic_frame(optimized_frame_bytes)
                    
                    if decision:
                        print(f"[COGNITION DECISION] Trust Score: {decision.confidence_score} | Context: {decision.analysis_summary}")
                        
                        if decision.trigger_actuator:
                            # Fire-and-forget actuation execution so hardware delays don't lock software tracking
                            asyncio.create_task(
                                asyncio.to_thread(self.actuation.trigger_relay, duration_seconds=1.5)
                            )
                        else:
                            print("[ACTUATION BYPASS] AI evaluators assessed no hardware mitigation required.")

                # Explicit yield to allow concurrent asynchronous tasks to execute seamlessly
                await asyncio.sleep(0.01)

        finally:
            # Absolute safety guarantee: release resources even if an unhandled runtime error occurs
            video_capture.release()
            self.actuation.cleanup()
            print("[SYSTEM OFFLINE] Main processing pipeline terminated safely.")


if __name__ == "__main__":
    # Initialize the modern, high-performance asynchronous event loop runtime
    orchestrator = EdgeAISystemOrchestrator()
    try:
        asyncio.run(orchestrator.execution_loop())
    except KeyboardInterrupt:
        # Standard fallback tracking for local shell terminations
        pass
                          
