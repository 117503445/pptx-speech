# FROM 117503445/dev-python
FROM ubuntu:20.04

WORKDIR /workspace/pptx-speech

COPY ./script/setup.sh /script/setup.sh
RUN /script/setup.sh

COPY pyproject.toml poetry.lock README.md ./
COPY pptx_speech/__init__.py ./pptx_speech/__init__.py
RUN /root/.local/bin/poetry env use python3.11 && /root/.local/bin/poetry install

COPY . .

ENTRYPOINT [ "bash", "/workspace/pptx-speech/script/entrypoint.sh" ]