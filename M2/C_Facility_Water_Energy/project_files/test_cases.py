"""Exactly 20 independently graded checks (3 marks each = 60 marks)."""
import os
from pathlib import Path

import joblib
import nbformat
import numpy as np
import pandas as pd
import pytest
from sklearn.ensemble import RandomForestRegressor
from sklearn.linear_model import Ridge
from sklearn.pipeline import Pipeline


BASE = Path(__file__).resolve().parent


@pytest.fixture(scope="module")
def app():
    notebook_name = os.environ.get("MS2_NOTEBOOK", "solution_with_code.ipynb")
    notebook_path = BASE / notebook_name
    notebook = nbformat.read(notebook_path, as_version=4)
    module = {}
    for cell in notebook.cells:
        if cell.cell_type == "code" and "definitions" in cell.metadata.get("tags", []):
            source = cell.source.strip()
            if source:
                exec(compile(source, str(notebook_path), "exec"), module)
    return module


def sensor_rows(n=6, include_target=True):
    df = pd.DataFrame({
        "reading_id": [f"WT-{i:04d}" for i in range(n)],
        "reading_ts": pd.date_range("2026-03-01 01:15", periods=n, freq="7h").strftime("%Y-%m-%d %H:%M"),
        "flow_m3": [float(i * 10 + 20) for i in range(n)],
        "occupancy": [i * 3 + 5 for i in range(n)],
        "pump_hours": [float(i % 5 + 1) for i in range(n)],
        "ambient_temp_c": [float(i * 2 + 10) for i in range(n)],
        "chemical_litres": [float(i + 2) for i in range(n)],
        "pressure_bar": [float(i * 0.5 + 1) for i in range(n)],
    })
    if include_target:
        df["energy_kwh"] = [float(i * 25 + 100) for i in range(n)]
    return df


def write_frame(path, df):
    df.to_csv(path, index=False)
    return str(path)


def feature_frame(app, n=18):
    return pd.DataFrame({
        name: np.arange(n, dtype=float) + index + 1
        for index, name in enumerate(app["FEATURES"])
    }, columns=app["FEATURES"])


def test_T01_first_duplicate_reading_id_retained(app, tmp_path):
    df = sensor_rows(3)
    df.loc[1, "reading_id"] = df.loc[0, "reading_id"]
    df.loc[1, "flow_m3"] = 999
    result = app["load_data"](write_frame(tmp_path / "duplicates.csv", df))
    assert result["reading_id"].tolist() == ["WT-0000", "WT-0002"]
    assert result.loc[0, "flow_m3"] == 20


def test_T02_remove_invalid_mixed_timestamps(app, tmp_path):
    df = sensor_rows(3)
    df.loc[0, "reading_ts"] = "2026-03-07 22:30"
    df.loc[1, "reading_ts"] = "08/03/2026 09:15"
    df.loc[2, "reading_ts"] = "not-a-date"
    result = app["load_data"](write_frame(tmp_path / "timestamps.csv", df))
    assert len(result) == 2
    assert pd.api.types.is_datetime64_any_dtype(result["reading_ts"])
    assert result["reading_ts"].dt.hour.tolist() == [22, 9]
    assert result["reading_ts"].dt.day.tolist() == [7, 8]


def test_T03_numeric_coercion_and_infinity_replacement(app, tmp_path):
    df = sensor_rows(4)
    df["flow_m3"] = ["bad", "inf", "-inf", "12"]
    df["occupancy"] = ["1", "2", "?", "4"]
    result = app["load_data"](write_frame(tmp_path / "numeric.csv", df))
    assert all(pd.api.types.is_numeric_dtype(result[col]) for col in app["RAW_NUMERIC"])
    assert result.loc[0, "flow_m3"] != result.loc[0, "flow_m3"]
    assert result.loc[1, "flow_m3"] != result.loc[1, "flow_m3"]
    assert not np.isinf(result[app["RAW_NUMERIC"]].to_numpy(dtype=float)).any()


def test_T04_raw_numeric_predictors_are_nonnegative(app, tmp_path):
    df = sensor_rows(4)
    df.loc[0, "flow_m3"] = -1
    df.loc[1, "pressure_bar"] = -2
    result = app["load_data"](write_frame(tmp_path / "negative.csv", df))
    assert result[app["RAW_NUMERIC"]].fillna(0).ge(0).all().all()
    assert pd.isna(result.loc[0, "flow_m3"])
    assert pd.isna(result.loc[1, "pressure_bar"])


def test_T05_derive_time_and_weekend_features(app, tmp_path):
    df = sensor_rows(3)
    df["reading_ts"] = ["2026-03-07 22:30", "2026-03-08 09:15", "2026-03-09 11:00"]
    result = app["load_data"](write_frame(tmp_path / "time.csv", df))
    assert result["reading_hour"].tolist() == [22, 9, 11]
    assert result["reading_month"].tolist() == [3, 3, 3]
    assert result["is_weekend"].tolist() == [1, 1, 0]


def test_T06_safe_flow_per_pump_hour_ratio(app, tmp_path):
    df = sensor_rows(3)
    df["pump_hours"] = [0, 2, 4]
    result = app["load_data"](write_frame(tmp_path / "ratio.csv", df))
    assert pd.isna(result.loc[0, "flow_per_pump_hour"])
    assert not np.isinf(result["flow_per_pump_hour"].dropna().to_numpy()).any()


def test_T07_exact_feature_list_excludes_id_timestamp_and_target(app):
    assert len(app["FEATURES"]) == 10
    assert app["FEATURES"] == app["RAW_NUMERIC"] + [
        "reading_hour", "reading_month", "is_weekend", "flow_per_pump_hour"
    ]
    assert "reading_id" not in app["FEATURES"]
    assert "reading_ts" not in app["FEATURES"]
    assert app["TARGET"] not in app["FEATURES"]


def test_T08_pipeline_has_impute_log_scale_and_model_steps(app):
    pipeline = app["build_pipeline"](Ridge())
    assert isinstance(pipeline, Pipeline)
    assert list(pipeline.named_steps) == ["imputer", "log", "scaler", "model"]
    assert pipeline.named_steps["model"] is not None


def test_T09_log_transform_uses_log1p(app):
    pipeline = app["build_pipeline"](Ridge())
    transformed = pipeline.named_steps["log"].transform(np.array([[0.0, np.e - 1]]))
    assert np.allclose(transformed, [[0.0, 1.0]])


def test_T10_fitted_median_imputer_covers_all_features(app):
    X = feature_frame(app, 18)
    X.loc[0, app["FEATURES"][0]] = np.nan
    models = app["train_models"](X, pd.Series(np.arange(18, dtype=float) + 10))
    imputer = models["ridge_regression"].named_steps["imputer"]
    assert len(imputer.statistics_) == len(app["FEATURES"])
    assert np.isfinite(imputer.statistics_).all()


def test_T11_filter_invalid_energy_targets_and_align_rows(app, tmp_path):
    df = sensor_rows(5)
    df["energy_kwh"] = ["12", "-1", "bad", "inf", "25"]
    train_path = write_frame(tmp_path / "train-invalid.csv", df)
    test_path = write_frame(tmp_path / "test-invalid.csv", df)
    X_train, _, y_train, _ = app["prepare_datasets"](train_path, test_path)
    assert len(X_train) == len(y_train) == 2
    assert X_train.index.tolist() == y_train.index.tolist()
    assert y_train.tolist() == [12, 25]


def test_T12_prepared_features_have_expected_columns(app, tmp_path):
    df = sensor_rows(5)
    train_path = write_frame(tmp_path / "train.csv", df)
    test_path = write_frame(tmp_path / "test.csv", df)
    X_train, X_test, _, _ = app["prepare_datasets"](train_path, test_path)
    assert X_train.columns.tolist() == app["FEATURES"]
    assert X_test.columns.tolist() == app["FEATURES"]
    assert app["TARGET"] not in X_train.columns


def test_T13_train_ridge_and_random_forest_regressors(app):
    X = feature_frame(app, 18)
    y = pd.Series(np.arange(18, dtype=float) + 20)
    models = app["train_models"](X, y)
    assert set(models) == {"ridge_regression", "random_forest"}
    assert isinstance(models["ridge_regression"].named_steps["model"], Ridge)
    assert isinstance(models["random_forest"].named_steps["model"], RandomForestRegressor)


def test_T14_mae_matches_model_predictions(app):
    class FakeModel:
        def predict(self, X):
            return np.array([2.0, 3.0, 4.0])

    y = pd.Series([1.0, 3.0, 5.0])
    X = pd.DataFrame({"value": [0, 1, 2]})
    comparison = app["evaluate_models"]({"fake": FakeModel()}, X, y)
    assert np.isclose(comparison.loc[0, "mae"], np.mean([1.0, 0.0, 1.0]))


def test_T15_rmse_matches_model_predictions(app):
    class FakeModel:
        def predict(self, X):
            return np.array([2.0, 4.0, 8.0])

    y = pd.Series([1.0, 3.0, 5.0])
    X = pd.DataFrame({"value": [0, 1, 2]})
    comparison = app["evaluate_models"]({"fake": FakeModel()}, X, y)
    assert np.isclose(comparison.loc[0, "rmse"], np.sqrt((1 + 1 + 9) / 3))


def test_T16_r2_matches_model_predictions(app):
    class FakeModel:
        def predict(self, X):
            return np.array([2.0, 4.0, 8.0])

    y = pd.Series([1.0, 3.0, 5.0])
    X = pd.DataFrame({"value": [0, 1, 2]})
    comparison = app["evaluate_models"]({"fake": FakeModel()}, X, y)
    residual_sum = np.sum((y.to_numpy() - np.array([2.0, 4.0, 8.0])) ** 2)
    total_sum = np.sum((y.to_numpy() - y.mean()) ** 2)
    assert np.isclose(comparison.loc[0, "r2"], 1 - residual_sum / total_sum)


def test_T17_sort_models_by_mae_and_select_best(app):
    class FakeModel:
        def __init__(self, predictions):
            self.predictions = np.asarray(predictions)

        def predict(self, X):
            return self.predictions

    y = pd.Series([1.0, 2.0, 3.0, 4.0])
    X = pd.DataFrame({"value": range(4)})
    models = {
        "zeta": FakeModel([1.0, 2.0, 3.0, 4.0]),
        "alpha": FakeModel([1.0, 2.0, 3.0, 4.0]),
        "beta": FakeModel([2.0, 3.0, 4.0, 5.0]),
    }
    comparison = app["evaluate_models"](models, X, y)
    assert comparison["model_name"].tolist() == ["alpha", "zeta", "beta"]
    assert comparison["mae"].is_monotonic_increasing
    name, selected = app["select_best_model"](comparison, models)
    assert name == "alpha" and selected is models["alpha"]


def test_T18_prediction_is_ordered_nonnegative_and_rounded(app):
    class FakeModel:
        def predict(self, X):
            return np.array([-1.236, 2.345, 3.338])

    df = feature_frame(app, 3)
    df["reading_id"] = ["R1", "R2", "R3"]
    result = app["predict_energy"](FakeModel(), df)
    assert result.columns.tolist() == ["reading_id", "predicted_energy_kwh"]
    assert result["reading_id"].tolist() == ["R1", "R2", "R3"]
    assert result["predicted_energy_kwh"].tolist() == [0.0, 2.35, 3.34]
    assert result["predicted_energy_kwh"].ge(0).all()


def test_T19_train_writes_and_persists_best_model(app, tmp_path, monkeypatch):
    sensor_rows(36).to_csv(tmp_path / "water_train.csv", index=False)
    sensor_rows(12).to_csv(tmp_path / "water_test.csv", index=False)
    monkeypatch.chdir(tmp_path)
    name, comparison = app["train"]()
    assert name in comparison["model_name"].tolist()
    assert (tmp_path / "best_model.pkl").is_file()
    assert (tmp_path / "model_comparison.csv").is_file()
    assert isinstance(joblib.load(tmp_path / "best_model.pkl"), Pipeline)


def test_T20_independent_train_predict_writes_prediction_file(app, tmp_path, monkeypatch):
    sensor_rows(36).to_csv(tmp_path / "water_train.csv", index=False)
    sensor_rows(12).to_csv(tmp_path / "water_test.csv", index=False)
    future = sensor_rows(8, include_target=False)
    future.to_csv(tmp_path / "water_predict.csv", index=False)
    monkeypatch.chdir(tmp_path)
    app["train"]()
    result = app["predict"]()
    assert len(result) == len(future)
    assert (tmp_path / "water_predictions.csv").is_file()
    assert pd.read_csv(tmp_path / "water_predictions.csv").columns.tolist() == [
        "reading_id", "predicted_energy_kwh"
    ]
