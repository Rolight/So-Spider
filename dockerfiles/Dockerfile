FROM python:2

COPY sources.list /etc/apt/sources.list

RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        libssl-dev \
        libffi-dev \
        python-dev \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

RUN pip install -U pip

COPY requirements.txt /usr/src/app
RUN pip install --no-cache-dir -r requirements.txt

# for shell
RUN apt-get update && apt-get install -y --no-install-recommends \
        vim \
        gettext \
        redis-tools \
     && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir ipython uwsgitop
