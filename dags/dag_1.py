import os
import pickle
from datetime import datetime

import mlflow

from airflow import DAG
from airflow.operators.python import PythonOperator

from scripts.engines import MLFlowEngines
from scripts.settings import MLFlowModelsDict
from scripts.train import MLFlowTrainModel
from queries.queries import MLFLowQueries

eng = MLFlowEngines()

def get_data():
    q = MLFLowQueries()

    df = eng.get_pandas_df(q.standart_query).dropna()

    r = eng.get_redis
    r.setex("df:data", 600, pickle.dumps(df))

def preprocess_data():

    r = eng.get_redis
    data = pickle.loads(r.get("df:data")) \
        .sort_values(['ts_month', 
                      'ts_day_year', 
                      'ts_day_month', 
                      'ts_day_week', 
                      'ts_hour',
                      'ts_minute',
                      'ts_second'])
    r.delete("df:data")

    split_idx = int(len(data) * 0.8)
    train = data.iloc[:split_idx]
    test = data.iloc[split_idx:]

    X_train = train.drop('aggregate_temp_c', axis=1)
    y_train = train['aggregate_temp_c']
    X_test = test.drop('aggregate_temp_c', axis=1)
    y_test = test['aggregate_temp_c']

    r.setex("df:X_train", 600, pickle.dumps(X_train))
    r.setex("df:y_train", 600, pickle.dumps(y_train))
    r.setex("df:X_test", 600, pickle.dumps(X_test))
    r.setex("df:y_test", 600, pickle.dumps(y_test))

def train_data():
    from mlflow.tracking import MlflowClient

    models = MLFlowModelsDict()
    name = 'mlflow_test_snu'
    mlflow.set_tracking_uri(os.environ["MLFLOW_TRACKING_URI"])

    client = MlflowClient()
    exp = client.get_experiment_by_name(name)
    if exp is not None and exp.lifecycle_stage == "deleted":
        client.restore_experiment(exp.experiment_id)
    mlflow.set_experiment(name)

    r = eng.get_redis
    X_train = pickle.loads(r.get("df:X_train"))
    X_test = pickle.loads(r.get("df:X_test"))
    y_train = pickle.loads(r.get("df:y_train"))
    y_test = pickle.loads(r.get("df:y_test"))
    models_train = MLFlowTrainModel(X_train, y_train, X_test, y_test)

    r.delete("df:X_train")
    r.delete("df:X_test")
    r.delete("df:y_train")
    r.delete("df:y_test")

    with mlflow.start_run(run_name = 'Dataset_1') as parent_run:
        for model_name, model in models().items():
            with mlflow.start_run(run_name = model_name, nested=True) as child_run:
                models_train(model, model_name, 'regression')

with DAG(
    dag_id="snu_demo",
    start_date=datetime(2026, 1, 1),
    schedule=None,
    catchup=False,
    tags=["mlflow", "clickhouse", "demo"],
) as dag:

    data = PythonOperator(
        task_id="data", 
        python_callable=get_data
    )

    preprocessing = PythonOperator(
        task_id = "preprocessing",
        python_callable=preprocess_data
    )

    training = PythonOperator(
        task_id = "training",
        python_callable=train_data
    )

    data >> preprocessing >> training