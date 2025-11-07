FROM python:3.12


WORKDIR /app

COPY bot_settings /app/bot_settings
COPY bot_control /app/bot_control
RUN ["mkdir", "downloaded_xlsx"]

RUN pip install --no-cache-dir --upgrade -r /app/bot_settings/requirements.txt

COPY . /app

CMD ["python", "TimeTableBot.py"]
