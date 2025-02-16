FROM homeassistant/amd64-base-python:3.9-alpine3.16

# Install required packages
RUN apk add --no-cache \
    rtl-sdr \
    git \
    gcc \
    g++ \
    make \
    cmake \
    libusb-dev \
    linux-headers \
    python3-dev \
    py3-pip

# Install rtl_433
RUN git clone https://github.com/merbanan/rtl_433.git \
    && cd rtl_433 \
    && mkdir build \
    && cd build \
    && cmake ../ \
    && make \
    && make install

# Install Python dependencies
RUN pip3 install --no-cache-dir \
    paho-mqtt \
    uni-curses

# Install rtl_433_discoverandsubmit
RUN pip3 install --no-cache-dir rtl_433_discoverandsubmit==0.1.9

# Add run script
COPY run.sh /
RUN chmod a+x /run.sh

CMD [ "/run.sh" ]

