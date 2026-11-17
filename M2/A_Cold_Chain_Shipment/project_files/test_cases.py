"""Exactly 20 independently graded checks (3 marks each = 60 marks)."""
import os
import shutil
from pathlib import Path

import joblib
import nbformat
import numpy as np
import pandas as pd
import pytest
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score
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


def shipment_rows(n=4):
    return pd.DataFrame({
        "shipment_id": [f"SH-{i:04d}" for i in range(n)],
        "dispatch_ts": [
            "2026-01-03 04:15", "04/02/2026 13:20",
            "2026-03-05 22:45", "06/04/2026 08:10",
        ][:n],
        "shipment_note": [
            "Distance: 18.75 km; Weight: 3.2 kg",
            "Distance: 21 km; Weight: 4.5 kg",
            "Distance: 30.5 km; Weight: 1.25 kg",
            "Distance: 42 km; Weight: 2 kg",
        ][:n],
        "month_text": ["Jan", "FEB", " mar ", "DEC"][:n],
        "transit_hours": [2.0, 3.0, 0.0, 4.0][:n],
        "temperature_c": [5.0, 8.0, 2.0, 10.0][:n],
        "region": [" North ", "SOUTH", "West", "East"][:n],
        "vehicle_type": [" VAN ", "truck", "Bike", "VAN"][:n],
        "route_zone": ["2.0", "1.0", "3.0", "4.0"][:n],
        "late_delivery": ["yes", "no", " YES ", "NO"][:n],
    })


def write_frame(path, df):
    df.to_csv(path, index=False)
    return str(path)


def feature_frame(app, n=12):
    data = {}
    for i, name in enumerate(app["NUMERIC"]):
        data[name] = np.arange(n, dtype=float) + i + 1
    for name in app["CATEGORICAL"]:
        data[name] = ["north", "south", "west"] * (n // 3) + ["north"] * (n % 3)
    return pd.DataFrame(data, columns=app["FEATURES"])


def test_T01_first_duplicate_id_is_retained(app, tmp_path):
    df = shipment_rows(3)
    df.loc[1, "shipment_id"] = df.loc[0, "shipment_id"]
    df.loc[1, "temperature_c"] = 99
    result = app["load_data"](write_frame(tmp_path / "duplicates.csv", df))
    assert result["shipment_id"].tolist() == ["SH-0000", "SH-0002"]
    assert result.loc[0, "temperature_c"] == 5


def test_T02_remove_invalid_mixed_timestamps(app, tmp_path):
    df = shipment_rows(3)
    df.loc[0, "dispatch_ts"] = "2026-03-07 22:30"
    df.loc[1, "dispatch_ts"] = "08/03/2026 09:15"
    df.loc[2, "dispatch_ts"] = "not-a-date"
    result = app["load_data"](write_frame(tmp_path / "dates.csv", df))
    assert len(result) == 2
    assert result["dispatch_ts"].dt.hour.tolist() == [22, 9]
    assert result["dispatch_ts"].dt.day.tolist() == [7, 8]


def test_T03_numeric_coercion_and_infinity_replacement(app, tmp_path):
    df = shipment_rows(4)
    df["transit_hours"] = ["bad", "inf", "-inf", "2.5"]
    df["temperature_c"] = ["1.5", "bad", "inf", "-inf"]
    result = app["load_data"](write_frame(tmp_path / "numeric.csv", df))
    assert all(pd.api.types.is_numeric_dtype(result[col]) for col in app["RAW_NUMERIC"])
    assert result.loc[0, "transit_hours"] != result.loc[0, "transit_hours"]
    assert result.loc[1, "temperature_c"] != result.loc[1, "temperature_c"]
    assert not np.isinf(result[app["RAW_NUMERIC"]].to_numpy(dtype=float)).any()


def test_T04_normalize_all_categorical_features(app, tmp_path):
    df = shipment_rows(3)
    df.loc[0, ["region", "vehicle_type", "route_zone"]] = ["  NORTH ", " VAN ", "2.0"]
    df.loc[1, ["region", "vehicle_type", "route_zone"]] = [" ", None, "  "]
    result = app["load_data"](write_frame(tmp_path / "categories.csv", df))
    for col in app["CATEGORICAL"]:
        assert result[col].str.strip().eq(result[col]).all()
        assert result[col].str.lower().eq(result[col]).all()
    assert result.loc[0, "region"] == "north"
    assert result.loc[1, "region"] == "unknown"
    assert result.loc[1, "vehicle_type"] == "unknown"


def test_T05_derive_dispatch_hour(app, tmp_path):
    result = app["load_data"](write_frame(tmp_path / "hours.csv", shipment_rows(4)))
    assert result["departure_hour"].tolist() == [4, 13, 22, 8]


def test_T06_extract_decimal_distance_with_regex(app):
    assert app["extract_decimal"]("Distance: 18.75 km; Weight: 3.2 kg", "distance") == 18.75
    assert app["extract_decimal"]("DISTANCE: 340 KM", "distance") == 340


def test_T07_extract_decimal_weight_with_regex(app):
    assert app["extract_decimal"]("distance: 18 km; weight: 3.25 kg", "weight") == 3.25
    assert np.isnan(app["extract_decimal"]("no weight listed", "weight"))


def test_T08_clean_numeric_like_route_codes(app, tmp_path):
    result = app["load_data"](write_frame(tmp_path / "route.csv", shipment_rows(4)))
    assert result["route_zone"].tolist() == ["2", "1", "3", "4"]
    assert not result["route_zone"].str.contains(r"\.0$", regex=True).any()


def test_T09_map_month_strings_jan_to_dec(app, tmp_path):
    df = pd.concat([shipment_rows(4)] * 3, ignore_index=True)
    df["shipment_id"] = [f"SH-{i:04d}" for i in range(12)]
    df["month_text"] = [
        "Jan", "FEB", "Mar", "Apr", "May", "Jun",
        "Jul", "Aug", "Sep", "Oct", "Nov", "DEC",
    ]
    result = app["load_data"](write_frame(tmp_path / "months.csv", df))
    assert app["MONTH_MAP"]["jan"] == 1 and app["MONTH_MAP"]["dec"] == 12
    assert result["month_number"].tolist() == list(range(1, 13))


def test_T10_derive_hour_from_parsed_timestamp(app, tmp_path):
    result = app["load_data"](write_frame(tmp_path / "parsed-hour.csv", shipment_rows(4)))
    assert result["departure_hour"].tolist() == result["dispatch_ts"].dt.hour.tolist()


def test_T11_prevent_infinity_in_distance_per_hour(app, tmp_path):
    result = app["load_data"](write_frame(tmp_path / "ratio.csv", shipment_rows(4)))
    assert pd.isna(result.loc[2, "distance_per_hour"])
    assert not np.isinf(result["distance_per_hour"].dropna().to_numpy()).any()


def test_T12_exact_feature_groups(app):
    assert len(app["NUMERIC"]) == 7
    assert len(app["CATEGORICAL"]) == 3
    assert len(app["FEATURES"]) == 10
    assert app["FEATURES"] == app["NUMERIC"] + app["CATEGORICAL"]


def test_T13_column_transformer_has_two_pipeline_branches(app):
    pipeline = app["build_pipeline"](LogisticRegression())
    assert isinstance(pipeline, Pipeline)
    transformer = pipeline.named_steps["preprocessor"]
    assert isinstance(transformer, ColumnTransformer)
    assert [name for name, _, _ in transformer.transformers] == ["numeric", "category"]
    assert list(transformer.transformers[0][2]) == app["NUMERIC"]
    assert list(transformer.transformers[1][2]) == app["CATEGORICAL"]


def test_T14_unseen_categories_after_training(app):
    X = feature_frame(app)
    y = pd.Series([0, 1] * (len(X) // 2))
    model = app["build_pipeline"](LogisticRegression())
    model.fit(X, y)
    new_rows = X.iloc[:2].copy()
    new_rows.loc[new_rows.index[0], app["CATEGORICAL"][0]] = "never-seen"
    assert model.predict(new_rows).shape == (2,)


def test_T15_map_yes_no_target_to_one_zero(app, tmp_path):
    train = shipment_rows(4)
    train["late_delivery"] = [" YES ", "no", "yes", "NO"]
    test = train.copy()
    train_path = write_frame(tmp_path / "train.csv", train)
    test_path = write_frame(tmp_path / "test.csv", test)
    _, _, y_train, y_test = app["prepare_datasets"](train_path, test_path)
    assert y_train.tolist() == [1, 0, 1, 0]
    assert y_test.tolist() == [1, 0, 1, 0]


def test_T16_fit_separate_balanced_logistic_and_random_forest_models(app):
    X = feature_frame(app, 24)
    y = pd.Series([0, 1] * 12)
    models = app["train_models"](X, y)
    assert set(models) == {"logistic_regression", "random_forest"}
    logistic = models["logistic_regression"].named_steps["model"]
    forest = models["random_forest"].named_steps["model"]
    assert isinstance(logistic, LogisticRegression)
    assert isinstance(forest, RandomForestClassifier)
    assert logistic.class_weight == forest.class_weight == "balanced"
    assert models["logistic_regression"] is not models["random_forest"]
    assert all(hasattr(model.named_steps["model"], "classes_") for model in models.values())


def test_T17_positive_class_f1_and_metric_sorting(app):
    class FakeModel:
        classes_ = np.array([0, 1])

        def __init__(self, probabilities):
            self.probabilities = np.asarray(probabilities)

        def predict_proba(self, X):
            return np.column_stack([1 - self.probabilities, self.probabilities])

    y = pd.Series([1, 1, 0, 0])
    X = pd.DataFrame({"value": [0, 1, 2, 3]})
    models = {
        "alpha": FakeModel([0.8, 0.8, 0.1, 0.1]),
        "gamma": FakeModel([0.8, 0.8, 0.1, 0.1]),
        "beta": FakeModel([0.8, 0.1, 0.1, 0.1]),
        "boundary": FakeModel([0.40, 0.39, 0.40, 0.90]),
    }
    comparison = app["evaluate_models"](models, X, y)
    assert comparison.columns.tolist() == ["model_name", "accuracy", "precision", "recall", "f1"]
    assert comparison["model_name"].tolist() == ["alpha", "gamma", "beta", "boundary"]
    assert np.isclose(comparison.set_index("model_name").loc["boundary", "f1"],
                      f1_score(y, [1, 0, 1, 1]))


def test_T18_select_highest_ranked_existing_model(app):
    comparison = pd.DataFrame({
        "model_name": ["alpha", "gamma", "beta"],
        "f1": [0.8, 0.8, 0.5],
        "recall": [0.9, 0.9, 0.7],
    })
    models = {"alpha": object(), "beta": object(), "gamma": object()}
    name, selected = app["select_best_model"](comparison, models)
    assert name == "alpha" and selected is models["alpha"]


def test_T19_prediction_has_ids_probabilities_and_thresholded_labels(app):
    class FakeModel:
        classes_ = np.array([0, 1])

        def predict_proba(self, X):
            probabilities = np.array([0.10, 0.39, 0.40, 0.95])
            return np.column_stack([1 - probabilities, probabilities])

    df = feature_frame(app, 4)
    df["shipment_id"] = ["S1", "S2", "S3", "S4"]
    result = app["predict_delay"](FakeModel(), df)
    assert result.columns.tolist() == ["shipment_id", "predicted_late", "late_probability"]
    assert result["shipment_id"].tolist() == ["S1", "S2", "S3", "S4"]
    assert result["predicted_late"].tolist() == [0, 0, 1, 1]
    assert result["late_probability"].tolist() == [0.1, 0.39, 0.4, 0.95]


def test_T20_train_predict_write_three_files(app, tmp_path, monkeypatch):
    train = pd.read_csv(BASE / "shipment_train.csv").iloc[:80]
    test = pd.read_csv(BASE / "shipment_test.csv").iloc[:24]
    future = pd.read_csv(BASE / "shipment_predict.csv").iloc[:12]
    train.to_csv(tmp_path / "shipment_train.csv", index=False)
    test.to_csv(tmp_path / "shipment_test.csv", index=False)
    future.to_csv(tmp_path / "shipment_predict.csv", index=False)
    monkeypatch.chdir(tmp_path)

    name, comparison = app["train"]()
    assert name in comparison["model_name"].tolist()
    assert (tmp_path / "best_model.pkl").is_file()
    assert (tmp_path / "model_comparison.csv").is_file()
    assert isinstance(joblib.load(tmp_path / "best_model.pkl"), Pipeline)

    result = app["predict"]()
    assert len(result) == len(future)
    assert (tmp_path / "shipment_predictions.csv").is_file()
    assert pd.read_csv(tmp_path / "shipment_predictions.csv").columns.tolist() == [
        "shipment_id", "predicted_late", "late_probability"
    ]
