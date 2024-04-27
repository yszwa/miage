FROM python:3.10-slim
ARG POETRY_CACHE_DIR='/root/.cache/poetry'
RUN apt update
RUN apt install -y ffmpeg curl
ENV POETRY_HOME=/opt/poetry
RUN curl -sSL https://install.python-poetry.org | python3 -
RUN cd /usr/local/bin && \
    ln -s /opt/poetry/bin/poetry && \
    poetry config virtualenvs.create false
# キャッシュを利用するためにpyproject.tomlとpoetry.lockを先にコピー
COPY ./pyproject.toml /app/pyproject.toml
COPY ./poetry.lock /app/poetry.lock
WORKDIR /app
RUN \
  --mount=type=cache,target=${POETRY_CACHE_DIR} \
  poetry config cache-dir ${POETRY_CACHE_DIR} && \
  poetry config installer.parallel false && \
  poetry config virtualenvs.create false && \ 
  poetry install --no-interaction
COPY ./src /app/src
RUN mkdir /app/voice
CMD ["poetry", "run", "python", "src/main.py"]