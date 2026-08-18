import os
import pickle
from datetime import datetime

import mlflow
import mlflow.sklearn

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.models import Variable

from scripts.engines import MLFlowEngines
from scripts.settings import MLFlowModelsDict
from scripts.train import MLFlowTrainModel
from scripts.scaling import parse_exclude_cols, scale_feature_frames

eng = MLFlowEngines()

_SORT_COLS = [
    "ts_month",
    "ts_day_year",
    "ts_day_month",
    "ts_day_week",
    "ts_hour",
    "ts_minute",
    "ts_second",
]


def get_data():
    df = eng.get_pandas_df(Variable.get("TRAINING_QUERY")).dropna()

    r = eng.get_redis
    r.setex("training_df:data", 600, pickle.dumps(df))


def preprocess_data():
    r = eng.get_redis
    data = pickle.loads(r.get("training_df:data")).sort_values(_SORT_COLS)
    r.delete("training_df:data")

    split_idx = int(len(data) * float(Variable.get("TRAIN_SPLIT")))
    train = data.iloc[:split_idx]
    test = data.iloc[split_idx:]

    scaler_type = Variable.get("SCALER_TYPE", default_var="standard")
    exclude = parse_exclude_cols(
        Variable.get(
            "SCALER_EXCLUDE_COLS",
            default_var="scenario,anomaly_flag,anomaly_type",
        )
    )
    train, test, scaler, scaled_cols = scale_feature_frames(
        train, test, scaler_type, exclude
    )

    r.setex("training_df:train", 600, pickle.dumps(train))
    r.setex("training_df:test", 600, pickle.dumps(test))
    r.setex(
        "training_df:scaler_meta",
        600,
        pickle.dumps(
            {
                "scaler_type": scaler_type,
                "scaled_cols": scaled_cols,
                "scaler": scaler,
            }
        ),
    )


def train_data():
    from mlflow.tracking import MlflowClient

    name = Variable.get("MLFLOW_EXPERIMENT_NAME")
    model_type = Variable.get("PREDICTION_TYPE")
    dataset_name = Variable.get("DATASET_NAME")
    scaler_type = Variable.get("SCALER_TYPE", default_var="standard")

    models = MLFlowModelsDict()
    if model_type == "regression":
        models_dict = models.regression_models()
    elif model_type == "classification":
        models_dict = models.classification_models()
    else:
        raise ValueError(f"Unsupported PREDICTION_TYPE={model_type!r}")

    mlflow.set_tracking_uri(os.environ["MLFLOW_TRACKING_URI"])

    client = MlflowClient()
    exp = client.get_experiment_by_name(name)
    if exp is not None and exp.lifecycle_stage == "deleted":
        client.restore_experiment(exp.experiment_id)
    mlflow.set_experiment(name)

    r = eng.get_redis
    train = pickle.loads(r.get("training_df:train"))
    test = pickle.loads(r.get("training_df:test"))
    scaler_meta = pickle.loads(r.get("training_df:scaler_meta"))
    r.delete("training_df:train")
    r.delete("training_df:test")
    r.delete("training_df:scaler_meta")

    X_train = train.drop("target", axis=1)
    y_train = train["target"]
    X_test = test.drop("target", axis=1)
    y_test = test["target"]

    models_train = MLFlowTrainModel(X_train, y_train, X_test, y_test)

    with mlflow.start_run(run_name=f"{model_type} test dataset") as parent_run:
        mlflow.log_param("scaler_type", scaler_type)
        mlflow.log_param(
            "scaled_cols",
            ",".join(scaler_meta.get("scaled_cols") or []),
        )

        dataset = mlflow.data.from_pandas(
            train,
            source="snu",
            name=dataset_name,
            targets="target",
        )
        mlflow.log_input(dataset, context="training")

        if scaler_meta.get("scaler") is not None:
            mlflow.sklearn.log_model(
                scaler_meta["scaler"],
                artifact_path="scaler",
            )
            scaler_uri = f"runs:/{parent_run.info.run_id}/scaler"
            Variable.set("SCALER_URI", scaler_uri)
            Variable.set(
                "SCALER_SCALED_COLS",
                ",".join(scaler_meta.get("scaled_cols") or []),
            )
        else:
            Variable.set("SCALER_URI", "none")
            Variable.set("SCALER_SCALED_COLS", "")

        Variable.set("FEATURE_COLS", ",".join(X_train.columns.tolist()))

        for model_name, model in models_dict.items():
            with mlflow.start_run(run_name=model_name, nested=True) as child_run:
                models_train(model, model_name, model_type)


with DAG(
    dag_id="snu_demo_training",
    start_date=datetime(2026, 1, 1),
    schedule=None,
    catchup=False,
    tags=["mlflow", "clickhouse", "demo"],
) as dag:

    data = PythonOperator(
        task_id="data",
        python_callable=get_data,
    )

    preprocessing = PythonOperator(
        task_id="preprocessing",
        python_callable=preprocess_data,
    )

    training = PythonOperator(
        task_id="training",
        python_callable=train_data,
    )

    data >> preprocessing >> training
