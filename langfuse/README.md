## Enhanced Observability Configuration for LiteLLM Proxy


Best practical combination:

* Prometheus metrics (already built into LiteLLM Proxy)
    - Gives you live queue depth, request rate, latency, and error counters.
    - Perfect for watching how the protective queue behaves under real Agentmemory load.

* Langfuse (self-hosted or cloud)
    - Gives rich per-request traces:
    - Total wall-clock time (submit → finish)
    - Time spent waiting in LiteLLM queue
    - Actual generation time from llama.cpp
    - Tokens generated, model used, success/failure


