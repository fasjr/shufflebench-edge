FROM arm64v8/ubuntu:focal
LABEL authors="fernandoama"
ENTRYPOINT ["top", "-b"]
# Note:
# Here copy the /usr/bin/qemu-system-aarch64 to local bin folder
#COPY ./bin/qemu-system-aarch64 /usr/bin/qemu-system-aarch64
COPY qemu-system-x86_64 /usr/bin/qemu-system-x86_64

ARG DEBIAN_FRONTEND=noninteractive
ARG RELEASE
ARG LAUNCHPAD_BUILD_ARCH
LABEL org.opencontainers.image.version=arm64v8
ADD file:3bd10da0673e2e72cb06a1f64a9df49a36341df39b0f762e3d1b38ee4de296fa in /
# Basic apt update
RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends locales ca-certificates

# Set the locale to en_US.UTF-8, because the Yocto build fails without any locale set.
ENV LANG en_US.UTF-8
ENV LC_ALL en_US.UTF-8

# Get basic packages
RUN apt-get update && apt-get install -y \
    apparmor \
    aufs-tools \
    automake \
    bash-completion \
    build-essential \
    cmake \
    curl \
    dpkg-sig \
    iptables \
    jq \
    libapparmor-dev \
    libc6-dev \
    libcap-dev \
    libsystemd-dev \
    libyaml-dev \
    mercurial \
    net-tools \
    parallel \
    pkg-config \
    iproute2 \
    iputils-ping \
    vim-common \
    vim \
    jib-gradle-plugin:3.3.1\
    --no-install-recommends \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Compilation environment variable
ENV BUILD_CAFFE2_OPS=OFF
ENV USE_FBGEMM=OFF
ENV USE_FAKELOWP=OFF
ENV BUILD_TEST=OFF
ENV USE_MKLDNN=OFF
ENV USE_NNPACK=ON
ENV USE_XNNPACK=ON
ENV USE_QNNPACK=ON
ENV MAX_JOBS=12
ENV USE_NUMPY=ON
ENV USE_OPENCV=OFF
ENV USE_NCCL=OFF
ENV BUILD_SHARED_LIBS=ON
ENV PATH=/usr/lib/ccache:$PATH
ENV CC=clang
ENV JAVA_HOME=/opt/java/openjdk
ENV PATH=/opt/java/openjdk/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
ENV LANG=en_US.UTF-8 LANGUAGE=en_US:en LC_ALL=en_US.UTF-8
ENV JAVA_VERSION=jdk-11.0.23+9



CMD ["/bin/bash"]

RUN /bin/sh -c set -eux; apt-get update; DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends curl wget fontconfig ca-certificates p11-kit tzdata locales ; echo "en_US.UTF-8 UTF-8" >> /etc/locale.gen; locale-gen en_US.UTF-8; rm -rf /var/lib/apt/lists/* # buildkit

RUN /bin/sh -c set -eux; ARCH="$(dpkg --print-architecture)"; case "${ARCH}" in aarch64|arm64) ESUM='7290ace47a030d89ea023c28e7aa555c9da72b4194f73b39ec9d058011bf06dd'; BINARY_URL='https://github.com/adoptium/temurin11-binaries/releases/download/jdk-11.0.23%2B9/OpenJDK11U-jre_aarch64_linux_hotspot_11.0.23_9.tar.gz'; ;; amd64|i386:x86-64) ESUM='786a72296189ba8e43999532aa73730d87ec1fce558eb3c4e98b611b423375e3'; BINARY_URL='https://github.com/adoptium/temurin11-binaries/releases/download/jdk-11.0.23%2B9/OpenJDK11U-jre_x64_linux_hotspot_11.0.23_9.tar.gz'; ;; armhf|arm) ESUM='025f994549708f7291ce3b0fa7c41f7e78ec3af3eae3f85fffe9c5fa4a54889f'; BINARY_URL='https://github.com/adoptium/temurin11-binaries/releases/download/jdk-11.0.23%2B9/OpenJDK11U-jre_arm_linux_hotspot_11.0.23_9.tar.gz'; ;; ppc64el|powerpc:common64) ESUM='3b3fbd324620fd914bd8462e292124493fcf846fd69195c4b9a231131dc68d5f'; BINARY_URL='https://github.com/adoptium/temurin11-binaries/releases/download/jdk-11.0.23%2B9/OpenJDK11U-jre_ppc64le_linux_hotspot_11.0.23_9.tar.gz'; ;; s390x|s390:64-bit) ESUM='25abb7f74f55847b0d509402111084bd7a244d904744f3bfffa89528bc3b8a69'; BINARY_URL='https://github.com/adoptium/temurin11-binaries/releases/download/jdk-11.0.23%2B9/OpenJDK11U-jre_s390x_linux_hotspot_11.0.23_9.tar.gz'; ;; *) echo "Unsupported arch: ${ARCH}"; exit 1; ;; esac; wget --progress=dot:giga -O /tmp/openjdk.tar.gz ${BINARY_URL}; echo "${ESUM} */tmp/openjdk.tar.gz" | sha256sum -c -; mkdir -p "$JAVA_HOME"; tar --extract --file /tmp/openjdk.tar.gz --directory "$JAVA_HOME" --strip-components 1 --no-same-owner ; rm -f /tmp/openjdk.tar.gz ${JAVA_HOME}/lib/src.zip; find "$JAVA_HOME/lib" -name '*.so' -exec dirname '{}' ';' | sort -u > /etc/ld.so.conf.d/docker-openjdk.conf; ldconfig; java -Xshare:dump; # buildkit

RUN /bin/sh -c set -eux; echo "Verifying install ..."; echo "java --version"; java --version; echo "Complete." # buildkit

COPY entrypoint.sh /__cacert_entrypoint.sh

#ENTRYPOINT ["/__cacert_entrypoint.sh"]
