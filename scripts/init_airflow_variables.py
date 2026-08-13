from airflow.models import Variable

Variable.set("MLFLOW_EXPERIMENT_NAME", "mlflow_test_snu")
Variable.set("PREDICTION_TYPE", "regression")
Variable.set(
    "REGRESSION_QUERY",
    "select ts_month, ts_day_year, ts_day_month, ts_day_week, ts_hour, ts_minute, "
    "ts_second, aggregate_temp_c_lag, is_anomaly_1, is_anomaly_2, aggregate_temp_diff, "
    "oil_mixture_volume_m3_lag, motor_current_a_lag, air_temp_c, humidity_pct, "
    "atmospheric_pressure_hpa, target from snu.telemetry_aggregate_temp_c_3600",
)
Variable.set(
    "CLASSIFICATION_QUERY",
    "select ts_month, ts_day_year, ts_day_month, ts_day_week, ts_hour, ts_minute, "
    "ts_second, aggregate_temp_c_lag, is_anomaly, aggregate_temp_diff, "
    "oil_mixture_volume_m3_lag, motor_current_a_lag, air_temp_c, humidity_pct, "
    "atmospheric_pressure_hpa, target from snu.telemetry_anomaly_3600",
)
Variable.set(
    "PREDICTION_QUERY",
    "select ts, ts_month, ts_day_year, ts_day_month, ts_day_week, ts_hour, ts_minute, "
    "ts_second, aggregate_temp_c_lag, is_anomaly_1, is_anomaly_2, aggregate_temp_diff, "
    "oil_mixture_volume_m3_lag, motor_current_a_lag, air_temp_c, humidity_pct, "
    "atmospheric_pressure_hpa from snu.telemetry_aggregate_temp_c_3600_pred",
)
Variable.set("PREDICTION_TABLE", "snu.telemetry_aggregate_temp_c_3600_prediction")
Variable.set("MODEL_URI", "0000000")
Variable.set("TRAIN_SPLIT", "0.8")
Variable.set(
    "REGRESSION_MODELS",
    {
        "LinearRegression": {},
        "DecisionTreeRegressor": {"max_depth": 8, "random_state": 42},
        "RandomForestRegressor": {
            "n_estimators": 30,
            "max_depth": 8,
            "n_jobs": 2,
            "random_state": 42,
        },
        "GradientBoostingRegressor": {
            "n_estimators": 30,
            "max_depth": 3,
            "random_state": 42,
        },
    },
    serialize_json=True,
)
Variable.set(
    "CLASSIFICATION_MODELS",
    {
        "LogisticRegression": {"max_iter": 1000},
        "DecisionTreeClassifier": {"max_depth": 8, "random_state": 42},
        "RandomForestClassifier": {
            "n_estimators": 30,
            "max_depth": 8,
            "n_jobs": 2,
            "random_state": 42,
        },
        "GradientBoostingClassifier": {
            "n_estimators": 30,
            "max_depth": 3,
            "random_state": 42,
        },
    },
    serialize_json=True,
)

print("Airflow variables initialized")
