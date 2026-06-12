# Autonomous Edge AI & Computer Vision Controller

An enterprise-grade, asynchronous backend system engineered for deployment on edge hardware (Raspberry Pi). This architecture bridges the gap between low-level hardware actuation and advanced cloud-native vision intelligence, optimizing for local network bandwidth, compute resource conservation, and minimal cloud runtime costs.

Built as a flagship blueprint for advanced automation and Industry 4.0 robotics frameworks, this architecture demonstrates a clean separation of concerns across local perception, non-deterministic cloud-native cognition, and safe physical actuation loops.

---

## 🛠️ Architecture & Tech Stack

- **Perception:** OpenCV (Local real-time frame processing, optimization, and structural motion filtration).
- **Cognition Engine:** Async OpenAI Vision API (Contextual, structured JSON decision formatting).
- **Actuation Layer:** Native Linux/Raspberry Pi GPIO with simulation/testing failovers.
- **Core Engine:** Asynchronous Python (`asyncio`) executing a non-blocking Perception-Cognition-Actuation (PCA) loop.

---

## 🏗️ Architectural Design (Ports & Adapters Pattern)

The codebase strictly follows a decoupled Hexagonal design, isolating peripheral hardware inputs and external cloud dependencies from core system logic:
[ Camera Stream ] ➡️ [ Local OpenCV Perception ] ➡️ (Anomaly Detected?)
⬇️ Yes
[ Physical Relay ] ⬅️ [ GPIO Actuation ] ⬅️ [ Asynchronous LLM Decision Engine ]
1. **Local Perception Layer (The Edge):** Frame chunks are captured locally. OpenCV processes the matrices on-chip (grayscale conversion, Gaussian noise blurring, and structural frame-differencing). 
2. **Cognition Pipeline (The Cloud):** To eliminate immense cloud bandwidth bills, raw video is never streamed over the network. The system only triggers the `AsyncOpenAI` Vision pipeline with heavily compressed, optimized diagnostic frames when local perception flags a significant area delta.
3. **Hardware Actuation (The Loop Closure):** The AI engine processes the visual context and outputs a strict, type-safe JSON schema. Based on this contract, the main event loop spawns a background thread to pulse physical GPIO relays, maintaining an uninterrupted, zero-lag frame-ingestion loop.

---

## ⚙️ Mode of Operation (Step-by-Step Execution)

The entire system runs as a continuous, non-blocking asynchronous loop executing the following precise operational steps:

1. **Hardware Initialization:**
   * The system boots headless and instantiates the configuration singleton via `Pydantic`.
   * It probes the host OS for hardware registers. If `RPi.GPIO` is detected, it maps the physical BCM pins; if not, it transparently spawns the virtual hardware emulator to prevent startup crashes.
   * The camera peripheral is bound and downsampled to a fixed 640x480 matrix to protect memory allocation.

2. **Edge-Level Perception & Noise Filtration:**
   * The system captures video frames sequentially. 
   * Each raw frame is converted to grayscale and passed through a Gaussian blur filter to erase camera sensor noise or minor flickering.
   * A mathematical frame-differencing algorithm compares the current frame against the active environmental baseline. 
   * If the structural changes cross the `MOTION_THRESHOLD`, the system flags an active anomaly and captures a high-resolution JPEG byte buffer. If no changes occur, the frame is instantly dropped from memory to save cache space.

3. **Asynchronous Cognitive Analysis:**
   * The moment an anomaly flag is tripped, the main loop packages the compressed JPEG bytes into a Base64 string payload.
   * This payload is sent over a non-blocking asynchronous network pipeline to the OpenAI Vision engine.
   * The primary video ingestion loop *never freezes* while waiting for this network response; it immediately continues scanning the camera stream for subsequent inputs.

4. **Structured Decision Parsing:**
   * The AI vision engine evaluates the frame context against strict behavioral guidelines.
   * The engine returns a strictly formatted JSON payload enforced directly at the API gateway via a `Pydantic` schema contract (`HardwareInstructionContract`).
   * The system extracts three core metrics: `trigger_actuator` (boolean directive), `confidence_score` (float validation), and `analysis_summary` (string telemetry log).

5. **Hardware Actuation & Fail-Safe Reset:**
   * If `trigger_actuator` resolves to `True`, the asynchronous orchestrator offloads the task to a background thread pool (`asyncio.to_thread`).
   * This worker thread drives the designated GPIO pin to a `HIGH` (+5V) state, closing the physical relay circuit to activate the attached machinery (valves, alarms, locks, or conveyors) for a precise duration.
   * Once the execution timer expires, a `finally` block forces the GPIO pin back to a safe `LOW` (ground) state, ensuring the physical hardware can never get stuck in an active or dangerous position if the software encounters an unexpected interruption.

---

## 🚀 Advanced Production Highlights

* **Defensive Hardware Fallbacks:** Implements an automated import fallback mechanism. If the system executes on a desktop machine or CI/CD runner lacking `RPi.GPIO` registers, it seamlessly steps down to an isolated, mock software simulation layout without throwing runtime crashes.
* **Non-Deterministic to Deterministic Mapping:** Uses OpenAI Structured Outputs forced against strict **Pydantic V2 schemas** at the API gateway, eliminating loose, unpredictable text outputs and mapping raw AI logic into boolean execution instructions.
* **Asynchronous Multi-Threading:** Utilizing `asyncio` combined with thread pools (`asyncio.to_thread`) for hardware execution, preventing blocking synchronous operations (like physical relay sleep durations) from freezing the camera feed.

---

## 📦 Installation & Local Development

### Hardware Matrix
- Raspberry Pi (Model 4B/5 recommended)
- Standard USB Web Camera or CSI Camera Module
- 5V Relay Switch / Optocoupler module pinned to designated GPIO layout

### Environment Initialization
1. Clone the repository to your host environment:
   ```bash
   git clone [https://github.com/YOUR_USERNAME/edge-vision-controller.git](https://github.com/YOUR_USERNAME/edge-vision-controller.git)
   cd edge-vision-controller
