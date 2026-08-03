import numpy as np
import mlflow
import mlflow.sklearn
from mlflow.models import infer_signature
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


class MLFlowTrainModel:

    def __init__(self, X_train, y_train, X_test, y_test):
        self.X_train = X_train
        self.y_train = y_train
        self.X_test = X_test
        self.y_test = y_test

    def __call__(self, model, name, model_type):
        # MLflow params must be str/float/int/bool — skip None and complex values
        params = {
            key: value
            for key, value in model.get_params().items()
            if value is not None and isinstance(value, (str, int, float, bool))
        }
        mlflow.log_params(params)

        model.fit(self.X_train, self.y_train)
        y_pred = model.predict(self.X_test)
        y_true = np.asarray(self.y_test)

        mlflow.log_metric("mae", float(mean_absolute_error(y_true, y_pred)))
        mlflow.log_metric("rmse", float(mean_squared_error(y_true, y_pred, squared=False)))
        mlflow.log_metric("r2", float(r2_score(y_true, y_pred)))
        mlflow.log_param("model_type", model_type)

        signature = infer_signature(self.X_test, y_pred)
        mlflow.sklearn.log_model(model, name, signature=signature)
