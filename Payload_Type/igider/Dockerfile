# Stage 1: Linux executable build
FROM itsafeaturemythic/mythic_python_base:latest AS linux-build

WORKDIR /Mythic/

# Install PyInstaller and dependencies
RUN pip3 install pyinstaller

# Install UPX for executable compression
RUN apt-get update && \
    apt-get install -y upx-ucl && \
    rm -rf /var/lib/apt/lists/*

# Copy source code
COPY . /Mythic/

# Create directory for build artifacts
RUN mkdir -p /tmp/build_cache
ENV PYINSTALLER_CACHE_DIR=/tmp/build_cache

# Run PyInstaller to build Linux executable
RUN python3 main.py --target-os linux

# Stage 2: Windows executable build (using Wine on Linux for simplicity)
FROM itsafeaturemythic/mythic_python_base:latest AS windows-build

WORKDIR /Mythic/

# Install PyInstaller and Wine for Windows cross-compilation
RUN pip3 install pyinstaller && \
    dpkg --add-architecture i386 && \
    apt-get update && \
    apt-get install -y wine wine32 wine64 && \
    rm -rf /var/lib/apt/lists/*

# Install UPX for executable compression
RUN apt-get update && \
    apt-get install -y upx-ucl && \
    rm -rf /var/lib/apt/lists/*

# Configure Wine
RUN wine --version || true
ENV WINE_PREFIX=/root/.wine

# Copy source code
COPY . /Mythic/

# Create directory for build artifacts
RUN mkdir -p /tmp/build_cache
ENV PYINSTALLER_CACHE_DIR=/tmp/build_cache

# Run PyInstaller to build Windows executable using Wine
RUN wine python3 main.py --target-os windows

# Stage 3: Collect artifacts
FROM ubuntu:22.04 AS final

WORKDIR /artifacts/

# Copy Linux executable
COPY --from=linux-build /Mythic/dist/systemd-update /artifacts/systemd-update

# Copy Windows executable
COPY --from=windows-build /Mythic/dist/svchost.exe /artifacts/svchost.exe

# Optional: Keep the container running or provide artifacts
CMD ["bash", "-c", "ls -l /artifacts/ && sleep infinity"]