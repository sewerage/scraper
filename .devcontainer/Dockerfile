FROM mcr.microsoft.com/devcontainers/python:1-3.11-bookworm

# [Optional] Allow the vscode user to pip install globally w/o sudo
ENV PIP_TARGET=/usr/local/pip-global
ENV PYTHONPATH=${PIP_TARGET}:${PYTHONPATH}
ENV PATH=${PIP_TARGET}/bin:${PATH}
RUN mkdir -p ${PIP_TARGET} \
    && chown vscode:root ${PIP_TARGET} \
    && echo "if [ \"\$(stat -c '%U' ${PIP_TARGET})\" != \"vscode\" ]; then chown -R vscode:root ${PIP_TARGET}; fi" \
        | tee -a /root/.bashrc /home/vscode/.bashrc /root/.zshrc >> /home/vscode/.zshrc 

# install requirements and compile libtorrent python bindings

RUN apt-get update \
    && export DEBIAN_FRONTEND=noninteractive \
    && apt-get -y install --no-install-recommends \
    build-essential libboost-all-dev libssl-dev python3.11-dev libboost-python-dev

RUN cd /usr/local/src \
    && wget https://github.com/arvidn/libtorrent/releases/download/v2.0.9/libtorrent-rasterbar-2.0.9.tar.gz \
    && tar -xzf /usr/local/src/libtorrent-rasterbar-2.0.9.tar.gz 

RUN cd /usr/local/src/libtorrent-rasterbar-2.0.9 && \
    python3.11 setup.py build

RUN cd /usr/local/src/libtorrent-rasterbar-2.0.9 && \
    python3.11 setup.py install