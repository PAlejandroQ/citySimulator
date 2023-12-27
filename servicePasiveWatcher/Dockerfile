FROM python:3.8
LABEL authors="synapsis"
WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir -r requirements.txt

RUN apt-get update && \
    apt-get install -y libpq-dev && \
    apt-get install -y libglib2.0-0 && \
    apt-get install -y libsm6 && \
    apt-get install -y libxrender1 && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*


EXPOSE 5432

ENV DB_HOST localhost
ENV DB_NAME project_db
ENV DB_USER user_watcher
ENV DB_PASSWORD password

CMD ["python", "pasiveWatcher.py"]
