import os
import pickle

import mlflow
import mlflow.sklearn
from datetime import datetime

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.models import Variable
from scripts.engines import MLFlowEngines

eng = MLFlowEngines()

def get_data():
    df = eng.get_pandas_df(Variable.get("PREDICT"))

    z = df[['ts']]
    data = df.drop('ts', axis=1)

    r = eng.get_redis
    r.setex("prediction_df:ts", 600, pickle.dumps(z))
    r.setex("prediction_df:data", 600, pickle.dumps(data))

def predict():
    r = eng.get_redis
    data = pickle.loads(r.get("prediction_df:data"))

    mlflow.set_tracking_uri(os.environ["MLFLOW_TRACKING_URI"])
    model = mlflow.sklearn.load_model(Variable.get("MODEL_URI"))
    y_pred = model.predict(data)

    r.setex("prediction_df:y_pred", 600, pickle.dumps(y_pred))

def output_result():
    r = eng.get_redis
    ts = pickle.loads(r.get("prediction_df:ts"))
    prediction = pickle.loads(r.get("prediction_df:y_pred"))

    result = ts.copy()
    result["y_pred"] = prediction

    mlflow.set_tracking_uri(os.environ["MLFLOW_TRACKING_URI"])
    mlflow.set_experiment(Variable.get("MLFLOW_EXPERIMENT_NAME"))

    with mlflow.start_run(run_name="predict_output"):
        mlflow.log_table(result.head(100), "predictions.json")

    r.setex("prediction_df:result", 1200, pickle.dumps(result))

    r.delete("prediction_df:ts")
    r.delete("prediction_df:data")
    r.delete("prediction_df:y_pred")

with DAG(
    dag_id="snu_demo_predict",
    start_date=datetime(2026, 1, 1),
    schedule=None,
    catchup=False,
    tags=["mlflow", "predict"],
) as dag:

    preprocessing = PythonOperator(
        task_id="data", 
        python_callable=get_data)

    prediction = PythonOperator(
        task_id="predict", 
        python_callable=predict)

    output = PythonOperator(
            task_id="output", 
            python_callable=output_result)

    preprocessing >> prediction >> output