from datetime import datetime
import os
import pickle

from airflow import DAG
from airflow.operators.python import PythonOperator


def get_redis():
    import redis
    return redis.from_url(os.environ["REDIS_URL"])


def preprocess_data():
    from sklearn.datasets import load_iris
    from sklearn.model_selection import train_test_split

    X, y = load_iris(return_X_y=True)
    X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=42)

    r = get_redis()
    r.set("df:X_train", pickle.dumps(X_train))
    r.set("df:X_test", pickle.dumps(X_test))
    r.set("df:y_train", pickle.dumps(y_train))
    r.set("df:y_test", pickle.dumps(y_test))


def train_data():
    import mlflow
    import mlflow.sklearn
    from sklearn.linear_model import LogisticRegression
    from sklearn.metrics import accuracy_score

    r = get_redis()
    X_train = pickle.loads(r.get("df:X_train"))
    X_test = pickle.loads(r.get("df:X_test"))
    y_train = pickle.loads(r.get("df:y_train"))
    y_test = pickle.loads(r.get("df:y_test"))

    r.delete("df:X_train")
    r.delete("df:X_test")
    r.delete("df:y_train")
    r.delete("df:y_test")

    mlflow.set_tracking_uri(os.environ["MLFLOW_TRACKING_URI"])
    mlflow.set_experiment("iris_demo")

    with mlflow.start_run():
        model = LogisticRegression(max_iter=200)
        model.fit(X_train, y_train)
        acc = accuracy_score(y_test, model.predict(X_test))

        mlflow.log_param("model", "LogisticRegression")
        mlflow.log_metric("accuracy", acc)
        mlflow.sklearn.log_model(model, "model")


with DAG(
    dag_id="mlflow_iris_demo",
    start_date=datetime(2024, 1, 1),
    schedule=None,
    catchup=False,
    tags=["mlflow", "demo"],
) as dag:
    preprocess = PythonOperator(task_id="preprocess", python_callable=preprocess_data)
    train = PythonOperator(task_id="train", python_callable=train_data)

    preprocess >> train
