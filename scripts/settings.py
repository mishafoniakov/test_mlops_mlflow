from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor


class MLFlowModelsDict:

    def __call__(self):
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
