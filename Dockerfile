FROM python:3.11.2-bullseye

COPY app /app

WORKDIR /app

COPY iqoptionapi /app/iqoptionapi

RUN pip install websocket-client==0.56
RUN pip install -e /app/iqoptionapi/iqoptionapi
RUN pip install python-dotenv
RUN pip install aiohttp
RUN pip install pytz

CMD ["python","-u","main.py"]