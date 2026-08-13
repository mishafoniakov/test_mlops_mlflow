import json

from airflow.models import Variable
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.tree import DecisionTreeRegressor, DecisionTreeClassifier
from sklearn.ensemble import (
    RandomForestRegressor,
    GradientBoostingRegressor,
    RandomForestClassifier,
    GradientBoostingClassifier,
)

REGRESSION_REGISTRY = {
    "LinearRegression": LinearRegression,
    "DecisionTreeRegressor": DecisionTreeRegressor,
    "RandomForestRegressor": RandomForestRegressor,
    "GradientBoostingRegressor": GradientBoostingRegressor,
}

CLASSIFICATION_REGISTRY = {
    "LogisticRegression": LogisticRegression,
    "DecisionTreeClassifier": DecisionTreeClassifier,
    "RandomForestClassifier": RandomForestClassifier,
    "GradientBoostingClassifier": GradientBoostingClassifier,
}

DEFAULT_REGRESSION_MODELS = {
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
}

DEFAULT_CLASSIFICATION_MODELS = {
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
}


def _load_models_config(var_name: str, default: dict) -> dict:
    raw = Variable.get(var_name, default_var=None)
    if raw is None:
        return default
    if isinstance(raw, dict):
        return raw
    return json.loads(raw)


def build_models(cfg: dict, registry: dict) -> dict:
    models = {}
    for name, params in cfg.items():
        if name not in registry:
            raise KeyError(
                f"Unknown model '{name}'. Allowed: {sorted(registry)}"
            )
        models[name] = registry[name](**(params or {}))
    return models


class MLFlowModelsDict:

    def regression_models(self):
        cfg = _load_models_config("REGRESSION_MODELS", DEFAULT_REGRESSION_MODELS)
        return build_models(cfg, REGRESSION_REGISTRY)

    def classification_models(self):
        cfg = _load_models_config(
            "CLASSIFICATION_MODELS", DEFAULT_CLASSIFICATION_MODELS
        )
        return build_models(cfg, CLASSIFICATION_REGISTRY)
