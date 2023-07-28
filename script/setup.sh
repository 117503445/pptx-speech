export DEBIAN_FRONTEND=nonintercative

apt-get update && \
# https://learn.microsoft.com/zh-cn/azure/ai-services/speech-service/quickstarts/setup-platform \
apt-get install -y build-essential libssl-dev ca-certificates libasound2 wget \
 software-properties-common curl ffmpeg

add-apt-repository ppa:deadsnakes/ppa && apt-get install -y python3.11

echo "alias python='python3.11'" >> ~/.bashrc
echo "export PATH="/root/.local/bin:$PATH"" >> ~/.bashrc

curl -sSL https://install.python-poetry.org | python3.11 -

/root/.local/bin/poetry config virtualenvs.in-project true
/root/.local/bin/poetry env use python3.11