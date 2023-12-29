# Web 部署

> 通过 Docker Compose 部署 PPTX Speech 的 Web 服务

准备 `docker-compose.yml` 文件

```yml
version: '3.9'
services:
  pptx-speech:
    # chinese user could use aliyun mirror
    # registry.cn-hangzhou.aliyuncs.com/117503445-mirror/pptx-speech
    image: '117503445/pptx-speech'
    container_name: pptx-speech
    restart: unless-stopped
    volumes:
        - './config/config.yaml:/workspace/pptx-speech/config.yaml'
        - './data/web-data:/workspace/pptx-speech/web-data'
    entrypoint: [ "/root/.local/bin/poetry", "run", "python", "./pptx_speech/be.py"]
    ports:
      - '8080:8080'
```

准备 `config/config.yaml` 文件

```yaml
tts:
  azure:
    # NOTE: The key and region can be modified by referring to README.md.
    key: feng-kuang-xing-qi-si-vivo-50
    region: eastus
```

启动服务

```sh
docker compose up -d
```

访问网页 <http://localhost:8080>
