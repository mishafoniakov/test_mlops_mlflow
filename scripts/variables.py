from airflow.models import Variable

Variable.set("DATASET_NAME", 'regression')
Variable.set("MLFLOW_EXPERIMENT_NAME", "mlflow_test_snu")
Variable.set("PREDICTION_TYPE", "regression")
Variable.set(
    "TRAINING_QUERY",
    "select * from snu.telemetry_aggregate_temp_c"
)
Variable.set(
    "PREDICTION_QUERY",
    "select ts, ts_month, ts_day_year, ts_day_month, ts_day_week, ts_hour, ts_minute, ts_second, atmospheric_pressure_hpa, aggregate_temp_c, oil_mixture_volume_m3, motor_current_a, motor_power_kw, dynamometer_load_kn, strokes_per_min, stroke_length_m, tubing_pressure_atm, casing_pressure_atm, fluid_level_m, pump_fillage_pct, water_cut_pct, vibration_rms, ambient_temp_c, scenario, anomaly_flag, anomaly_type from snu.telemetry_aggregate_temp_c_pred",
)
Variable.set("PREDICTION_TABLE", "snu.telemetry_aggregate_temp_c_3600_prediction")
Variable.set("MODEL_URI", "0000000")
Variable.set("TRAIN_SPLIT", "0.8")
Variable.set("SCALER_TYPE", "standard")
Variable.set("SCALER_EXCLUDE_COLS", "scenario,anomaly_flag,anomaly_type")
# Filled automatically after snu_demo_training when a scaler is logged
Variable.set("SCALER_URI", "none")
Variable.set("SCALER_SCALED_COLS", "")
Variable.set("FEATURE_COLS", "")
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
