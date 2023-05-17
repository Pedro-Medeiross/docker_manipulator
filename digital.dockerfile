FROM python:3.11.2-bullseye

COPY verifier /verifier

WORKDIR /verifier

RUN pip install websocket-client==0.56
RUN pip install -U https://github.com/iqoptionapi/iqoptionapi/archive/refs/heads/master.zip
RUN pip install python-dotenv
RUN pip install aiohttp
RUN pip install pytz

CMD ["python","-u","digital.py"]