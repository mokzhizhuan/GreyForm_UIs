FROM ros:noetic-robot-usb
ENV DEBIAN_FRONTEND=noninteractive

# --- 0) Completely disable any existing ROS apt entries (old/expired)
RUN set -eux; \
  # remove any *.list that references packages.ros.org
  for f in /etc/apt/sources.list.d/*.list; do \
    [ -f "$f" ] || continue; \
    if grep -q 'packages\.ros\.org' "$f" 2>/dev/null; then \
      echo "Removing $f"; rm -f "$f"; \
    fi; \
  done; \
  # also scrub main sources.list just in case
  sed -i '/packages\.ros\.org/d' /etc/apt/sources.list || true; \
  apt-get update && apt-get install -y --no-install-recommends \
      ca-certificates curl gnupg lsb-release && \
  rm -rf /var/lib/apt/lists/*

# --- 1) Add fresh ROS key (copied in; avoids GitHub during build)
COPY ros.key /tmp/ros.key
RUN set -eux; \
  gpg --dearmor -o /usr/share/keyrings/ros-archive-keyring.gpg /tmp/ros.key; \
  echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/ros-archive-keyring.gpg] \
http://packages.ros.org/ros/ubuntu $(. /etc/os-release && echo $UBUNTU_CODENAME) main" \
    > /etc/apt/sources.list.d/ros1.list; \
  apt-get update

# --- 2) (Optional) future-proof helper (keeps repo/key in correct layout)
# RUN apt-get install -y --no-install-recommends ros-apt-source && rm -rf /var/lib/apt/lists/*

# --- 3) If you hit focal mirror 404s on old images, uncomment:
# RUN set -eux; \
#   sed -i 's|http://archive.ubuntu.com|http://old-releases.ubuntu.com|g; \
#           s|http://security.ubuntu.com|http://old-releases.ubuntu.com|g' /etc/apt/sources.list; \
#   apt-get update

