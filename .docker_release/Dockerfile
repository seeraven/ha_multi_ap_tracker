FROM ubuntu:22.04

# System update
RUN DEBIAN_FRONTEND=noninteractive DEBCONF_NONINTERACTIVE_SEEN=true \
    apt-get update
RUN DEBIAN_FRONTEND=noninteractive DEBCONF_NONINTERACTIVE_SEEN=true \
    apt-get -y dist-upgrade

RUN echo -e 'tzdata tzdata/Areas select Europe\n\
tzdata tzdata/Zones/Europe select Berlin\n' > /tmp/tzdata_preseed
RUN debconf-set-selections /tmp/tzdata_preseed && rm -f /tmp/tzdata_preseed
RUN DEBIAN_FRONTEND=noninteractive DEBCONF_NONINTERACTIVE_SEEN=true \
    apt-get -y install tzdata

RUN ln -sf bash /bin/sh

RUN DEBIAN_FRONTEND=noninteractive DEBCONF_NONINTERACTIVE_SEEN=true \
    apt-get -y install python3-minimal && \
    apt-get -y install --no-install-recommends python3-pip

RUN mkdir /work
WORKDIR /work

COPY pip_deps/requirements-linux-py3.10.12.txt /work/
RUN pip3 install -r requirements-linux-py3.10.12.txt && rm -f requirements-linux-py3.10.12.txt

COPY src /work/
COPY .docker_release/entrypoint.sh /work/

ENTRYPOINT ["/bin/bash", "/work/entrypoint.sh"]
