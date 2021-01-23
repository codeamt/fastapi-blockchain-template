FROM python:3.8
ADD requirements.txt /requirements.txt
ADD ./code /
RUN pip install-r requirements.txt
EXPOSE 5000
CMD ["uvicorn", "--port", "5000", "--host", "127.0.0.1", "main:blockchain", "--reload"]

