FROM python:3.11.2-bullseye

COPY app /app

WORKDIR /app

COPY iqoptionapi /app/iqoptionapi

RUN pip install websocket-client==0.56
RUN pip install -U https://github.com/Pedro-Medeiross/iqoptionapi/archive/refs/heads/master.zip
RUN pip install python-dotenv
RUN pip install aiohttp
RUN pip install pytz

CMD ["python","-u","main.py"]