import os
import pickle
from datetime import datetime

import mlflow
import mlflow.sklearn
import numpy as np
import pandas as pd

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.models import Variable
from airflow_clickhouse_plugin.operators.clickhouse import ClickHouseOperator
from scripts.engines import MLFlowEngines
from scripts.scaling import apply_fitted_scaler, parse_col_list

eng = MLFlowEngines()


def get_data():
    df = eng.get_pandas_df(Variable.get("PREDICTION_QUERY"))

    z = df[["ts"]]
    data = df.drop("ts", axis=1)

    r = eng.get_redis
    r.setex("prediction_df:ts", 600, pickle.dumps(z))
    r.setex("prediction_df:data", 600, pickle.dumps(data))


def predict():
    r = eng.get_redis
    data = pickle.loads(r.get("prediction_df:data"))

    feature_cols = parse_col_list(Variable.get("FEATURE_COLS", default_var=""))
    if feature_cols:
        missing = [c for c in feature_cols if c not in data.columns]
        if missing:
            raise ValueError(
                f"PREDICTION_QUERY missing training feature columns: {missing}"
            )
        data = data[feature_cols]

    mlflow.set_tracking_uri(os.environ["MLFLOW_TRACKING_URI"])

    scaler_uri = Variable.get("SCALER_URI", default_var="none")
    scaler_type = Variable.get("SCALER_TYPE", default_var="none").strip().lower()
    if scaler_uri not in ("", "none", "0000000") and scaler_type not in (
        "none",
        "off",
        "",
    ):
        scaler = mlflow.sklearn.load_model(scaler_uri)
        scaled_cols = parse_col_list(
            Variable.get("SCALER_SCALED_COLS", default_var="")
        )
        data = apply_fitted_scaler(data, scaler, scaled_cols)

    model = mlflow.sklearn.load_model(Variable.get("MODEL_URI"))
    y_pred = model.predict(data)

    r.setex("prediction_df:y_pred", 600, pickle.dumps(y_pred))


def output_result():
    r = eng.get_redis
    ts = pickle.loads(r.get("prediction_df:ts"))
    prediction = pickle.loads(r.get("prediction_df:y_pred"))

    table = Variable.get("PREDICTION_TABLE")
    pred_type = Variable.get("PREDICTION_TYPE")

    ts_col = pd.to_datetime(ts["ts"]).reset_index(drop=True)
    if getattr(ts_col.dt, "tz", None) is not None:
        ts_col = ts_col.dt.tz_convert(None)

    update_time = pd.Timestamp.now(tz="UTC").tz_convert(None)

    result = pd.DataFrame(
        {
            "ts": ts_col,
            "target": np.asarray(prediction, dtype="float32"),
            "update_time": update_time,
        }
    )

    eng.insert_pandas_df(table, result)

    mlflow.set_tracking_uri(os.environ["MLFLOW_TRACKING_URI"])
    mlflow.set_experiment(Variable.get("MLFLOW_EXPERIMENT_NAME"))

    with mlflow.start_run(run_name="predict_output"):
        mlflow.log_param("prediction_type", pred_type)
        mlflow.log_param("prediction_table", table)
        mlflow.log_param(
            "scaler_uri", Variable.get("SCALER_URI", default_var="none")
        )
        mlflow.log_metric("n_predictions", float(len(result)))
        mlflow.log_table(result.head(100), "predictions.json")

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
        python_callable=get_data,
    )

    prediction = PythonOperator(
        task_id="predict",
        python_callable=predict,
    )

    truncate = ClickHouseOperator(
        task_id="truncate",
        sql="TRUNCATE TABLE IF EXISTS {{ var.value.PREDICTION_TABLE }}",
        clickhouse_conn_id="clickhouse_default",
    )

    output = PythonOperator(
        task_id="output",
        python_callable=output_result,
    )

    preprocessing >> prediction >> truncate >> output
