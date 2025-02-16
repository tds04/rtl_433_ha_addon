ARG BUILD_FROM
FROM $BUILD_FROM

# Set shell
SHELL ["/bin/bash", "-o", "pipefail", "-c"]

# Install required packages
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       rtl-sdr \
       libtool \
       libusb-1.0-0-dev \
       librtlsdr-dev \
       cmake \
       build-essential \
       pkg-config \
       git \
       python3 \
       python3-pip \
       python3-setuptools \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Clone and build rtl_433
RUN git clone https://github.com/merbanan/rtl_433.git /tmp/rtl_433 \
    && cd /tmp/rtl_433 \
    && mkdir build \
    && cd build \
    && cmake ../ \
    && make \
    && make install \
    && cd / \
    && rm -rf /tmp/rtl_433

# Install Python requirements
COPY requirements.txt /
RUN pip3 install -r requirements.txt

# Copy script files
COPY rootfs /

# Execute during the build to get versions
RUN PYTHONPATH=/usr/local/lib/python3.8/dist-packages /usr/local/bin/rtl_433 -V

# Set permissions
RUN chmod a+x /etc/services.d/rtl_433_discover/run

ENTRYPOINT ["/init"]
