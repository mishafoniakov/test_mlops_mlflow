FROM apache/airflow:2.8.1

USER airflow
RUN pip install --no-cache-dir --default-timeout=180 \
        -i https://pypi.org/simple \
        --trusted-host pypi.org \
        --trusted-host files.pythonhosted.org \
        "mlflow==2.14.1" \
        "scikit-learn==1.3.2" \
        "protobuf>=4.25.0,<5" \
        "airflow-clickhouse-plugin==1.4.0" \
        "clickhouse-driver==0.2.9" \
    || pip install --no-cache-dir --default-timeout=180 \
        -i https://mirrors.aliyun.com/pypi/simple/ \
        --trusted-host mirrors.aliyun.com \
        "mlflow==2.14.1" \
        "scikit-learn==1.3.2" \
        "protobuf>=4.25.0,<5" \
        "airflow-clickhouse-plugin==1.4.0" \
        "clickhouse-driver==0.2.9" \
    || pip install --no-cache-dir --default-timeout=180 \
        -i https://pypi.tuna.tsinghua.edu.cn/simple \
        --trusted-host pypi.tuna.tsinghua.edu.cn \
        "mlflow==2.14.1" \
        "scikit-learn==1.3.2" \
        "protobuf>=4.25.0,<5" \
        "airflow-clickhouse-plugin==1.4.0" \
        "clickhouse-driver==0.2.9"
