# MIT License
#
# Copyright (c) 2019 Yuxin (Ryan) Wang
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
FROM openjdk:11-jdk-slim AS builder

# install build dependencies
RUN apt-get update -y && \
    apt-get install -y --no-install-recommends \
    gcc \
    software-properties-common \
    git \
    ant \
    unzip \
    python3 \
    python3-pip \
    python3-setuptools

# copy ShadowDP into the image
COPY . /shadowdp
WORKDIR /shadowdp

# install CPA-Checker
COPY scripts/get_cpachecker.sh /get_cpachecker.sh
RUN bash /get_cpachecker.sh

# install shadowdp
RUN pip3 install --install-option="--prefix=/install" .

FROM openjdk:11-jre-slim 
# install the runtime dependencies
RUN apt-get update -y && \
    apt-get install -y --no-install-recommends \
    python3 \
    python3-pip \
    python3-setuptools && \
    rm -rf /var/lib/apt/lists/*

COPY --from=builder /shadowdp /shadowdp
COPY --from=builder /install /usr/local

WORKDIR /shadowdp 

CMD ["bash"]
