FROM python:3.6.9-stretch

WORKDIR /ubcapi

COPY server/ .

RUN pip install --no-cache-dir pipenv && \
    pipenv install --system --deploy --clear

CMD ["python3", "app.py"]