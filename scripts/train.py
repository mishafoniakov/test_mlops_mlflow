import numpy as np
import mlflow
import mlflow.sklearn
from mlflow.models import infer_signature
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score,
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
    confusion_matrix,
)


class MLFlowTrainModel:

    def __init__(self, X_train, y_train, X_test, y_test):
        self.X_train = X_train
        self.y_train = y_train
        self.X_test = X_test
        self.y_test = y_test

    def __call__(self, model, name, model_type):
        params = {
            key: value
            for key, value in model.get_params().items()
            if value is not None and isinstance(value, (str, int, float, bool))
        }
        mlflow.log_params(params)

        model.fit(self.X_train, self.y_train)
        y_pred = model.predict(self.X_test)
        y_true = np.asarray(self.y_test)

        if model_type == 'regression':
            mlflow.log_metric("mae", float(mean_absolute_error(y_true, y_pred)))
            mlflow.log_metric("rmse", float(np.sqrt(mean_squared_error(y_true, y_pred))))
            mlflow.log_metric("r2", float(r2_score(y_true, y_pred)))

        elif model_type == 'classification':
            classes = np.unique(y_true)
            n_classes = len(classes)
            mlflow.log_param("n_classes", int(n_classes))

            mlflow.log_metric("accuracy", float(accuracy_score(y_true, y_pred)))

            if n_classes <= 2:
                average = "binary"
                y_score = model.predict_proba(self.X_test)[:, 1]
                mlflow.log_metric(
                    "roc_auc_score",
                    float(roc_auc_score(y_true, y_score)),
                )
            else:
                average = "weighted"
                y_score = model.predict_proba(self.X_test)
                mlflow.log_metric(
                    "roc_auc_score",
                    float(roc_auc_score(y_true, y_score, multi_class="ovr", average="weighted")),
                )
                cm = confusion_matrix(y_true, y_pred, labels=classes)
                for i, label in enumerate(classes):
                    mlflow.log_metric(f"cm_true_{int(label)}", float(cm[i].sum()))
                    mlflow.log_metric(f"cm_pred_{int(label)}", float(cm[:, i].sum()))

            mlflow.log_metric(
                "precision",
                float(precision_score(y_true, y_pred, average=average, zero_division=0)),
            )
            mlflow.log_metric(
                "recall",
                float(recall_score(y_true, y_pred, average=average, zero_division=0)),
            )
            mlflow.log_metric(
                "f1",
                float(f1_score(y_true, y_pred, average=average, zero_division=0)),
            )

        mlflow.log_param("model_type", model_type)

        signature = infer_signature(self.X_test, y_pred)
        mlflow.sklearn.log_model(model, name, signature=signature)
