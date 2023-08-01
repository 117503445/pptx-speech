FROM node:20.2.0 as fe-build
WORKDIR /fe
RUN npm install -g pnpm
COPY fe ./
RUN pnpm install && pnpm run build

# FROM 117503445/dev-python
FROM ubuntu:20.04

COPY --from=fe-build /fe/dist /workspace/pptx-speech/dist

WORKDIR /workspace/pptx-speech

COPY ./script/setup.sh /script/setup.sh
RUN /script/setup.sh

COPY pyproject.toml poetry.lock README.md ./
COPY pptx_speech/__init__.py ./pptx_speech/__init__.py
RUN /root/.local/bin/poetry env use python3.11 && /root/.local/bin/poetry install

COPY pptx-speech .

ENTRYPOINT [ "/root/.local/bin/poetry", "run", "python", "./pptx_speech/cli.py"]
