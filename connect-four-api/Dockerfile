FROM rust:1.79-slim AS chef
RUN cargo install cargo-chef
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 python3-pip python3-dev build-essential patchelf \
    && apt-get clean && rm -rf /var/lib/apt/lists/*
RUN pip3 install --no-cache-dir --break-system-packages maturin
WORKDIR /build

# Planner and Builder stages remain unchanged for minimax and monte-carlo
FROM chef AS planner-minimax
COPY agents/minimax/Cargo.toml agents/minimax/Cargo.lock ./
RUN mkdir src && echo "pub fn dummy() {}" > src/lib.rs
RUN cargo chef prepare --recipe-path recipe.json

FROM chef AS builder-minimax
COPY --from=planner-minimax /build/recipe.json recipe.json
RUN cargo chef cook --release --recipe-path recipe.json
COPY agents/minimax .
RUN maturin build --release

FROM chef AS planner-monte-carlo
COPY agents/monte-carlo/Cargo.toml agents/monte-carlo/Cargo.lock ./
RUN mkdir src && echo "pub fn dummy() {}" > src/lib.rs
RUN cargo chef prepare --recipe-path recipe.json

FROM chef AS builder-monte-carlo
COPY --from=planner-monte-carlo /build/recipe.json recipe.json
RUN cargo chef cook --release --recipe-path recipe.json
COPY agents/monte-carlo .
RUN maturin build --release --strip

# Now, the python stage to support USB camera access on Raspberry Pi
FROM python:3.11-slim
WORKDIR /app

# Install necessary libraries for USB camera support (e.g., OpenCV)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1-mesa-glx libglib2.0-0 libsm6 libxext6 libxrender-dev \
    libopencv-dev \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Install Rust-built wheels for agents
COPY --from=builder-minimax /build/target/wheels/*.whl /tmp/
COPY --from=builder-monte-carlo /build/target/wheels/*.whl /tmp/
RUN pip install --no-cache-dir /tmp/*.whl && rm -rf /tmp/*.whl

COPY . .

EXPOSE 8000

# Command to run your Python app
CMD ["python", "main.py"]