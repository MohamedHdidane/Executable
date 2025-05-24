# Stage 1: Linux executable build
FROM ubuntu:22.04 AS linux-build

WORKDIR /Mythic/

# Install Python and PyInstaller
RUN apt-get update && \
    apt-get install -y python3 python3-pip && \
    pip3 install pyinstaller mythic-container && \
    rm -rf /var/lib/apt/lists/*

# Copy source code
COPY . /Mythic/

# Create directory for build artifacts
RUN mkdir -p /tmp/build_cache
ENV PYINSTALLER_CACHE_DIR=/tmp/build_cache

# Run PyInstaller to build Linux executable
RUN python3 main.py --target-os linux

# Stage 2: Windows executable build (using Wine)
FROM ubuntu:22.04 AS windows-build

WORKDIR /Mythic/

# Install Wine, Python, and PyInstaller
RUN dpkg --add-architecture i386 && \
    apt-get update && \
    apt-get install -y wine wine32 wine64 python3 python3-pip upx-ucl && \
    pip3 install mythic-container && \
    rm -rf /var/lib/apt/lists/*

# Initialize Wine (required for first run)
RUN winecfg /v win10 && wine --version
ENV WINEPREFIX=/root/.wine
ENV WINEDEBUG=-all

# Install PyInstaller in Wine Python
RUN wine python3 -m pip install pyinstaller

# Copy source code
COPY . /Mythic/

# Create directory for build artifacts
RUN mkdir -p /tmp/build_cache
ENV PYINSTALLER_CACHE_DIR=/tmp/build_cache

# Run PyInstaller to build Windows executable
RUN wine python3 main.py --target-os windows

# Stage 3: Collect artifacts
FROM ubuntu:22.04 AS final

WORKDIR /artifacts/

# Copy Linux executable
COPY --from=linux-build /Mythic/dist/systemd-update /artifacts/systemd-update

# Copy Windows executable
COPY --from=windows-build /Mythic/dist/svchost.exe /artifacts/svchost.exe

# Keep container running for artifact retrieval
CMD ["bash", "-c", "ls -l /artifacts/ && sleep infinity"]