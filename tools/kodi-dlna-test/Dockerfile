FROM debian:trixie
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update \
 && apt-get install -y --no-install-recommends kodi xvfb xauth libgl1-mesa-dri libegl1 ca-certificates python3 iproute2 \
 && rm -rf /var/lib/apt/lists/*
