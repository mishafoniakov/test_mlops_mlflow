FROM apache/airflow:2.8.1

USER airflow
RUN pip install --no-cache-dir \
    "mlflow==2.14.1" \
    "scikit-learn==1.3.2" \
    "protobuf>=4.25.0,<5"
