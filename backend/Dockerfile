FROM python:3.10

WORKDIR /code

COPY ./requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY . /code/app

EXPOSE 80

CMD ["uvicorn", "app.app:app", "--host", "0.0.0.0", "--port", "80"]