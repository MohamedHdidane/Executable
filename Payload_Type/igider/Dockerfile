FROM itsafeaturemythic/mythic_python_base:latest

WORKDIR /Mythic/

# Install basic build tools and mingw-w64 for cross-compilation
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    wget \
    git \
    zip \
    upx \
    mingw-w64 \
    python3-pip \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install PyInstaller
RUN pip install --no-cache-dir pyinstaller

# Set up mingw-w64 as the cross-compiler
ENV CC=x86_64-w64-mingw32-gcc
ENV CXX=x86_64-w64-mingw32-g++

# Create build cache directory
RUN mkdir -p /tmp/build_cache
ENV PYINSTALLER_CACHE_DIR=/tmp/build_cache

CMD ["python3", "main.py"]