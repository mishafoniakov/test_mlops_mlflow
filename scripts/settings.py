from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.tree import DecisionTreeRegressor, DecisionTreeClassifier
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, RandomForestClassifier, GradientBoostingClassifier


class MLFlowModelsDict:

    def regression_models(self):
        return {
            "LinearRegression": LinearRegression(),
            "DecisionTreeRegressor": DecisionTreeRegressor(
                max_depth=8,
                random_state=42,
            ),
            "RandomForestRegressor": RandomForestRegressor(
                n_estimators=30,
                max_depth=8,
                n_jobs=2,
                random_state=42,
            ),
            "GradientBoostingRegressor": GradientBoostingRegressor(
                n_estimators=30,
                max_depth=3,
                random_state=42,
            ),
        }

    def classification_models(self):
        return {
            "LogisticRegression": LogisticRegression(),
            "DecisionTreeClassifier": DecisionTreeClassifier(
                max_depth=8,
                random_state=42,
            ),
            "RandomForestClassifier": RandomForestClassifier(
                n_estimators=30,
                max_depth=8,
                n_jobs=2,
                random_state=42,
            ),
            "GradientBoostingClassifier": GradientBoostingClassifier(
                n_estimators=30,
                max_depth=3,
                random_state=42,
            ),
        }
