#

## 1. Build llama.cpp from source

```bash
# Install build dependencies
sudo apt update
sudo apt install -y build-essential cmake git libcurl4-openssl-dev

# Clone latest llama.cpp
git clone https://github.com/ggml-org/llama.cpp.git
cd llama.cpp

# Build with CUDA, targeting GTX 980 (Compute Capability 5.2)
cmake -B build \
  -DGGML_CUDA=ON \
  -DCMAKE_CUDA_ARCHITECTURES=52 \
  -DCMAKE_BUILD_TYPE=Release \
  -DLLAMA_CURL=ON

cmake --build build --config Release -j$(nproc)
```

After build, the important binary is `./build/bin/llama-server`

(Optional but recommended) Install system-wide:
```bash
sudo cp build/bin/llama-server /usr/local/bin/
sudo cp build/bin/llama-* /usr/local/bin/   # optional other tools
```
## 2. Prepare models directory

```bash
sudo mkdir -p /opt/llama-models
sudo chown $USER:$USER /opt/llama-models
cd /opt/llama-models
```

Download the recommended GGUF files (Q4_K_M recommended):
```bash
# Primary recommended models (use huggingface-cli or wget/curl)
# Example with huggingface-cli (install if needed: pip install huggingface_hub)

hf download bartowski/Llama-3.2-3B-Instruct-GGUF \
  Llama-3.2-3B-Instruct-Q4_K_M.gguf --local-dir .

hf download bartowski/Qwen2.5-Coder-7B-Instruct-GGUF \
  Qwen2.5-Coder-7B-Instruct-Q4_K_M.gguf --local-dir .

hf download bartowski/Mistral-7B-Instruct-v0.3-GGUF \
  Mistral-7B-Instruct-v0.3-Q4_K_M.gguf --local-dir .

hf download bartowski/DeepSeek-R1-Distill-Qwen-7B-GGUF \
  DeepSeek-R1-Distill-Qwen-7B-Q4_K_M.gguf --local-dir .
```

Make alias for model names in `/opt/llama-models/rename_only.ini`:
```bash
[llama3.2-3b]
model=Llama-3.2-3B-Instruct-Q4_K_M.gguf

[mistral-7b-instruct]
model=Mistral-7B-Instruct-v0.3-Q4_K_M.gguf

[qwen2.5-coder-7b]
model=Qwen2.5-Coder-7B-Instruct-Q4_K_M.gguf

[deepseek-r1-7b]
model=DeepSeek-R1-Distill-Qwen-7B-Q4_K_M.gguf
```


Test it:
```bash
llama-server \
  --models-dir /opt/llama-models \
  --models-preset /opt/llama-models/rename_only.ini \
  --models-max 1 \
  --host 0.0.0.0 \
  --port 8080 \
  --ctx-size 4096 \
  --n-gpu-layers 99 \
  --parallel 1 \
  --threads 14 \
  --mlock \
  --flash-attn on \
  --cache-type-k q8_0 \
  --cache-type-v q8_0 \
  --no-mmap
```

Key flags explained (tuned for your hardware):

* `--models-dir` + `--models-max 1` → fully automatic load/unload, only one model resident.
* `--n-gpu-layers 99` → push as many layers as possible to the GPU (will automatically fall back for larger models).
* `--ctx-size 4096` → more than enough for Agentmemory short tasks, saves VRAM/RAM.
* `--parallel 1` → single concurrency (protects the weak GPU/CPU).
* `--threads 14` → good for 16-thread CPU (leaves 2 for OS).
* `--mlock` → lock model in RAM (important with only low free memory).
* `--cache-type-k/v q8_0` → halves KV cache memory usage with almost no quality loss.
* `--flash-attn on` → better speed + lower memory on supported builds.




## 3. Systemd service

Create `/etc/systemd/system/llama-server.service`

```bash
[Unit]
Description=llama.cpp multi-model server for Agentmemory
After=network.target

[Service]
Type=simple
User=<YOUR_USERNAME>
WorkingDirectory=/opt/llama-models
ExecStart=/usr/local/bin/llama-server \
  --models-dir /opt/llama-models \
  --models-preset /opt/llama-models/rename_only.ini \
  --models-max 1 \
  --host 0.0.0.0 \
  --port 8080 \
  --ctx-size 4096 \
  --n-gpu-layers 99 \
  --parallel 1 \
  --threads 14 \
  --mlock \
  --flash-attn on \
  --cache-type-k q8_0 \
  --cache-type-v q8_0 \
  --no-mmap
Restart=always
RestartSec=5
LimitNOFILE=65535

[Install]
WantedBy=multi-user.target

```
Then:
```bash
sudo systemctl daemon-reload
sudo systemctl enable --now llama-server
sudo systemctl status llama-server
```

## 4. Quick verification

```bash
curl http://127.0.0.1:8080/v1/models

# Test a short completion
curl http://127.0.0.1:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "llama3.2-3b",
    "messages": [{"role": "user", "content": "Say hello in one sentence."}],
    "max_tokens": 50
  }'
```

