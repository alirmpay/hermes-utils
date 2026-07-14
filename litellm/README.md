# Why litellm

Without a protective layer we risk:

* Queue buildup inside Agentmemory itself → memory pressure or crashes
* Timeouts cascading back into Hermes
* Unstable 24/7 operation

A proper middleware gives us:

* Durable queue
* Strict rate limiting / concurrency = 1 (matching llama.cpp)
* Strong backpressure so user can keep submitting without blocking
* Observability of the lag
* Local llama.cpp never flooded
* Downstream Applications never crashes / hangs / exhausts resources

Litellm proxy:
* Durable queue / non-blocking submit
    Requests are accepted immediately and held (semaphore + internal queue). With Redis backend it becomes highly durable across restarts.
* Strict concurrency = 1
    `max_parallel_requests: 1` (or `global_max_parallel_requests: 1`) + low rpm
* Backpressure
    Excess requests wait or receive controlled 429s instead of flooding the backend
* Protects llama.cpp
    Never sends more than 1 concurrent request to `:8080`
* Protects Agentmemory
    Agentmemory can fire jobs freely; they queue safely instead of hanging or OOMing
* Observability of lag
    "Built-in logging, success/failure callbacks, optional Prometheus / Langfuse / etc."
* OpenAI + multi-model llama.cpp
    Native support. Just point it at our OpenAI-compatible endpoint. Model name is passed through.
* Maturity & risk
    "Very widely used in production, actively maintained, far more mature than Hoglah / llm-threader"
* Lightweight enough for home server
    "Yes (Python, low overhead)"

Configuration philosophy:

* `max_parallel_requests: 1`
* Very low RPM (e.g. 2–4) so the slow 7B hybrid never gets overwhelmed
* Long timeouts (to accommodate slow generation)
* Pass-through of the `model` field (so our multi-model automatic switching continues to work)
* Good logging + optional Redis for stronger durability and rate-limit sharing
* Simple health / lag observability

