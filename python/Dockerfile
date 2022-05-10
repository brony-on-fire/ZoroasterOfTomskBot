FROM python:3

WORKDIR /usr/src/app

COPY requirements.txt ./

RUN pip install --no-cache-dir -r requirements.txt
RUN apt update && apt install -y --no-install-recommends locales; rm -rf /var/lib/apt/lists/*; sed -i '/^#.* ru_RU.UTF-8 /s/^#//' /etc/locale.gen; locale-gen
RUN locale -a

CMD [ "python", "./main.py" ]