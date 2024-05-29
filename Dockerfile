ARG APP_IMAGE=continuumio/miniconda3
FROM ${APP_IMAGE}
ARG APP_IMAGE
ENV PATH="/root/miniconda3/bin:${PATH}"
RUN sed -i 's/deb.debian.org/mirrors.ustc.edu.cn/g' /etc/apt/sources.list
RUN if [ "$APP_IMAGE" = "nvidia/cuda:12.0.0-devel-ubuntu22.04" ]; then \
    echo "Using CUDA image" \
    && apt-get update \
    && apt-get install -y unzip sudo git g++ libglm-dev libglew-dev libglfw3-dev libgles2-mesa-dev zlib1g-dev wget cmake vim libxi6 libgconf-2-4 libxkbcommon-x11-0 \
    && rm -rf /var/lib/apt/lists/* \
    && wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh \
    && mkdir /root/.conda \
    && bash Miniconda3-latest-Linux-x86_64.sh -b \
    && rm -f Miniconda3-latest-Linux-x86_64.sh; \
else \
    echo "Using Conda image" && \
    apt-get update -yq && \
    apt-get install -yq \
        cmake \
        g++ \
        libgconf-2-4 \
        libgles2-mesa-dev \
        libglew-dev \
        libglfw3-dev \
        libglm-dev \
        libxi6 \
        sudo \
        unzip \
        vim \
        zlib1g-dev \
        libxkbcommon-x11-0 \
    && rm -rf /var/lib/apt/lists/*; \
fi

RUN mkdir /opt/infinigen
WORKDIR /opt/infinigen
COPY infinigen.zip .
RUN unzip infinigen.zip && rm -f infinigen.zip
RUN conda init bash \
    && . ~/.bashrc \
    && conda create --name infinigen python=3.10 \
    && conda activate infinigen \
    && echo "conda activate infinigen" >> ~/.bashrc \
    && python -m pip install --upgrade pip \
    && pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple \
    && INFINIGEN_MINIMAL_INSTALL=True pip install -e .