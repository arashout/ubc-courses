FROM python:3.6.9-stretch

WORKDIR /ubcapi

COPY ./ .

RUN pip install --no-cache-dir pipenv && \
    pipenv install --system --deploy --clear

ENV FLASK_APP=ubcapi

CMD ["python","app.py"]