from sklearn.preprocessing import MinMaxScaler, RobustScaler, StandardScaler

SCALER_TYPES = ("none", "standard", "minmax", "robust")


def make_scaler(scaler_type: str):
    name = (scaler_type or "none").strip().lower()
    if name in ("none", "off", ""):
        return None
    if name == "standard":
        return StandardScaler()
    if name == "minmax":
        return MinMaxScaler()
    if name == "robust":
        return RobustScaler()
    raise ValueError(
        f"Unknown SCALER_TYPE={scaler_type!r}. Allowed: {', '.join(SCALER_TYPES)}"
    )


def parse_exclude_cols(raw: str) -> set:
    if not raw:
        return set()
    return {c.strip() for c in raw.split(",") if c.strip()}


def parse_col_list(raw: str) -> list:
    if not raw:
        return []
    return [c.strip() for c in raw.split(",") if c.strip()]


def scale_feature_frames(train, test, scaler_type: str, exclude_cols: set):
    scaler = make_scaler(scaler_type)
    feature_cols = [
        c
        for c in train.columns
        if c != "target" and c not in exclude_cols
    ]

    if scaler is None or not feature_cols:
        return train, test, None, []

    train = train.copy()
    test = test.copy()
    train[feature_cols] = scaler.fit_transform(train[feature_cols])
    test[feature_cols] = scaler.transform(test[feature_cols])
    return train, test, scaler, feature_cols


def apply_fitted_scaler(df, scaler, scaled_cols: list):
    """Apply a fitted scaler to prediction features (transform only)."""
    if scaler is None or not scaled_cols:
        return df
    missing = [c for c in scaled_cols if c not in df.columns]
    if missing:
        raise ValueError(
            f"Prediction frame missing columns required by scaler: {missing}"
        )
    out = df.copy()
    out[scaled_cols] = scaler.transform(out[scaled_cols])
    return out
