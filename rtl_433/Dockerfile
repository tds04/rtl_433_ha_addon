ARG BUILD_FROM=ghcr.io/home-assistant/amd64-base:3.19
FROM $BUILD_FROM as builder
MAINTAINER pbkhrv@pm.me

ENV LANG C.UTF-8

# Copied with minor edits from https://github.com/hertzg/rtl_433_docker/blob/master/images/alpine/build-context/Dockerfile
RUN apk add --no-cache --virtual .buildDeps \
    build-base \
    libusb-dev \
    librtlsdr-dev \
    cmake \
    git

WORKDIR /build

RUN git clone https://github.com/merbanan/rtl_433
WORKDIR ./rtl_433

# Build a specific commit or tag.
ARG rtl433GitRevision=23.11
RUN git checkout ${rtl433GitRevision}
WORKDIR ./build
RUN cmake ..
RUN make -j 4

WORKDIR /build/root
WORKDIR /build/rtl_433/build
RUN make DESTDIR=/build/root/ install

FROM $BUILD_FROM

ENV LANG C.UTF-8

RUN apk add --no-cache libusb \
    librtlsdr \
    sed
WORKDIR /root
COPY --from=builder /build/root/ /

# Use apk for Alpine
RUN apk add --no-cache \
       rtl-sdr \
       libtool \
       libusb-dev \
       librtlsdr-dev \
       cmake \
       make gcc g++ musl-dev \
       pkgconf \
       git \
       python3 \
       py3-pip \
       py3-setuptools
       
RUN pip3 install --upgrade pip && \
    pip3 install --no-cache-dir paho-mqtt || (echo "Error installing paho-mqtt" && exit 1)

# Copy script files
COPY rootfs /

# Execute during the build to get versions
RUN PYTHONPATH=/usr/local/lib/python3.8/dist-packages /usr/local/bin/rtl_433 -V

# Set permissions
RUN chmod a+x /etc/services.d/rtl_433_discover/run

ENTRYPOINT ["/init"]

