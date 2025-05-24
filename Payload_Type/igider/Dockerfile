# Stage 1: Linux executable build
FROM python:3.9-slim AS linux-build

WORKDIR /Mythic/
RUN pip install pyinstaller mythic-container

COPY . /Mythic/
RUN mkdir -p /tmp/build_cache
ENV PYINSTALLER_CACHE_DIR=/tmp/build_cache
RUN python3 main.py --target-os linux

# Stage 2: Windows executable build (pre-built Wine)
FROM scottyhardy/docker-wine:latest AS windows-build

WORKDIR /Mythic/

# Install Python in Wine
RUN wget https://www.python.org/ftp/python/3.9.18/python-3.9.18-amd64.exe && \
    wine python-3.9.18-amd64.exe /quiet InstallAllUsers=1 PrependPath=1

# Install PyInstaller
RUN wine python -m pip install pyinstaller mythic-container

COPY . /Mythic/
RUN mkdir -p /tmp/build_cache
ENV PYINSTALLER_CACHE_DIR=/tmp/build_cache
RUN wine python main.py --target-os windows

# Stage 3: Collect artifacts  
FROM python:3.9-slim AS final
WORKDIR /artifacts/

COPY --from=linux-build /Mythic/dist/systemd-update /artifacts/systemd-update
COPY --from=windows-build /Mythic/dist/svchost.exe /artifacts/svchost.exe

CMD ["bash", "-c", "ls -l /artifacts/ && sleep infinity"]