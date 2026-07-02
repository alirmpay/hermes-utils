FROM nvidia/cuda:12.6.3-cudnn-runtime-ubuntu22.04

RUN apt-get update && apt-get install -y --no-install-recommends python3 python3-pip \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# cu126 wheels still include sm_52 (Maxwell) kernels
RUN pip3 install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cu126
RUN pip3 install --no-cache-dir sentence-transformers "fastapi>=0.110" "uvicorn[standard]"

COPY server.py .

ENV MODEL_ID=sentence-transformers/all-MiniLM-L6-v2
ENV HF_HOME=/data
EXPOSE 80

CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "80"]
