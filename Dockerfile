FROM python:3.11.4-bullseye

COPY app /app

WORKDIR /app

RUN pip install -r requirements.txt
RUN pip install python-dotenv
RUN pip install aiohttp
RUN pip install pytz

CMD ["python","-u","main.py"]