FROM itsafeaturemythic/mythic_python_base:latest

WORKDIR /Mythic/

# Install ONLY what we need for cross-compilation
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    mingw-w64 \
    upx-ucl \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install PyInstaller with Windows support
RUN pip install --no-cache-dir pyinstaller

# Set mingw-w64 as the compiler
ENV CC=x86_64-w64-mingw32-gcc
ENV CXX=x86_64-w64-mingw32-g++

# Create build directory
RUN mkdir -p /tmp/build_cache
ENV PYINSTALLER_CACHE_DIR=/tmp/build_cache

CMD ["python3", "main.py"]