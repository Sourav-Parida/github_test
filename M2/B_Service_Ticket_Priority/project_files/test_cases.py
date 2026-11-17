"""Exactly 20 independently graded checks (3 marks each = 60 marks)."""
import os
from pathlib import Path

import joblib
import nbformat
import numpy as np
import pandas as pd
import pytest
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import confusion_matrix, f1_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import LabelEncoder


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


def ticket_rows(n=6, include_target=True):
    df = pd.DataFrame({
        "ticket_id": [f"TK-{i:04d}" for i in range(n)],
        "opened_ts": pd.date_range("2026-03-01 08:15", periods=n, freq="7h").strftime("%Y-%m-%d %H:%M"),
        "response_minutes": [15.0 + i * 2 for i in range(n)],
        "touch_count": [i % 5 + 1 for i in range(n)],
        "backlog_count": [i * 3 + 2 for i in range(n)],
        "agent_count": [i % 4 + 1 for i in range(n)],
        "agent_experience_yrs": [float(i % 8 + 1) for i in range(n)],
        "channel": [["chat", "email", "phone"][i % 3] for i in range(n)],
        "product_area": [["billing", "technical", "delivery"][i % 3] for i in range(n)],
        "customer_tier": [str(i % 3 + 1) + ".0" for i in range(n)],
    })
    if include_target:
        df["priority"] = [["high", "low", "medium"][i % 3] for i in range(n)]
    return df


def write_frame(path, df):
    df.to_csv(path, index=False)
    return str(path)


def feature_frame(app, n=18):
    data = {}
    for i, name in enumerate(app["NUMERIC"]):
        data[name] = np.arange(n, dtype=float) + i + 1
    for name in app["CATEGORICAL"]:
        data[name] = [["chat", "email", "phone"][i % 3] for i in range(n)]
    return pd.DataFrame(data, columns=app["FEATURES"])


def test_T01_first_duplicate_ticket_id_retained(app, tmp_path):
    df = ticket_rows(3)
    df.loc[1, "ticket_id"] = df.loc[0, "ticket_id"]
    df.loc[1, "response_minutes"] = 999
    result = app["load_data"](write_frame(tmp_path / "duplicates.csv", df))
    assert result["ticket_id"].tolist() == ["TK-0000", "TK-0002"]
    assert result.loc[0, "response_minutes"] == 15


def test_T02_parse_mixed_timestamps_and_remove_invalid(app, tmp_path):
    df = ticket_rows(3)
    df.loc[0, "opened_ts"] = "2026-03-07 22:30"
    df.loc[1, "opened_ts"] = "08/03/2026 09:15"
    df.loc[2, "opened_ts"] = "bad timestamp"
    result = app["load_data"](write_frame(tmp_path / "timestamps.csv", df))
    assert len(result) == 2
    assert pd.api.types.is_datetime64_any_dtype(result["opened_ts"])
    assert result["opened_ts"].dt.hour.tolist() == [22, 9]
    assert result["opened_ts"].dt.day.tolist() == [7, 8]


def test_T03_numeric_coercion_and_infinity_replacement(app, tmp_path):
    df = ticket_rows(5)
    df["response_minutes"] = ["bad", "inf", "-inf", "12", "8.5"]
    df["touch_count"] = ["1", "?", "2", "3", "4"]
    result = app["load_data"](write_frame(tmp_path / "numeric.csv", df))
    assert all(pd.api.types.is_numeric_dtype(result[col]) for col in app["RAW_NUMERIC"])
    assert result.loc[0, "response_minutes"] != result.loc[0, "response_minutes"]
    assert result.loc[1, "response_minutes"] != result.loc[1, "response_minutes"]
    assert not np.isinf(result[app["RAW_NUMERIC"]].to_numpy(dtype=float)).any()


def test_T04_clean_numeric_like_customer_tier(app, tmp_path):
    df = ticket_rows(3)
    result = app["load_data"](write_frame(tmp_path / "tiers.csv", df))
    assert result["customer_tier"].tolist() == ["1", "2", "3"]
    assert not result["customer_tier"].str.contains(r"\.0$", regex=True).any()


def test_T05_normalize_priority_target(app, tmp_path):
    df = ticket_rows(4)
    df["priority"] = [" high ", "low", "Medium ", " HIGH "]
    result = app["load_data"](write_frame(tmp_path / "targets.csv", df))
    assert result["priority"].tolist() == ["HIGH", "LOW", "MEDIUM", "HIGH"]


def test_T06_derive_opened_hour_and_month(app, tmp_path):
    df = ticket_rows(3)
    df["opened_ts"] = ["2026-01-02 04:15", "2026-06-11 13:20", "2026-12-25 22:45"]
    result = app["load_data"](write_frame(tmp_path / "time_features.csv", df))
    assert result["opened_hour"].tolist() == [4, 13, 22]
    assert result["opened_month"].tolist() == [1, 6, 12]


def test_T07_safe_backlog_per_agent_division(app, tmp_path):
    df = ticket_rows(3)
    df["agent_count"] = [0, 2, 4]
    result = app["load_data"](write_frame(tmp_path / "ratio.csv", df))
    assert pd.isna(result.loc[0, "backlog_per_agent"])
    assert not np.isinf(result["backlog_per_agent"].dropna().to_numpy()).any()


def test_T08_exact_feature_groups_exclude_identifiers_and_target(app):
    assert len(app["NUMERIC"]) == 8
    assert len(app["CATEGORICAL"]) == 3
    assert len(app["FEATURES"]) == 11
    assert "ticket_id" not in app["FEATURES"]
    assert app["TARGET"] not in app["FEATURES"]


def test_T09_column_transformer_has_numeric_and_category_branches(app):
    pipeline = app["build_pipeline"](LogisticRegression())
    transformer = pipeline.named_steps["preprocessor"]
    assert isinstance(transformer, ColumnTransformer)
    assert len(transformer.transformers) == 2
    assert list(transformer.transformers[0][2]) == app["NUMERIC"]
    assert list(transformer.transformers[1][2]) == app["CATEGORICAL"]


def test_T10_label_encoder_matches_class_names(app, tmp_path):
    df = ticket_rows(6)
    train_path = write_frame(tmp_path / "train.csv", df)
    test_path = write_frame(tmp_path / "test.csv", df)
    _, _, y_train, y_test, encoder = app["prepare_datasets"](train_path, test_path)
    assert isinstance(encoder, LabelEncoder)
    assert encoder.classes_.tolist() == sorted(app["CLASS_NAMES"])
    assert set(y_train.unique()) == {0, 1, 2}
    assert y_test.tolist() == y_train.tolist()


def test_T11_remove_invalid_targets_and_preserve_alignment(app, tmp_path):
    df = ticket_rows(6)
    df["priority"] = ["high", "low", "medium", "urgent", None, " LOW "]
    train_path = write_frame(tmp_path / "train-invalid.csv", df)
    test_path = write_frame(tmp_path / "test-invalid.csv", df)
    X_train, _, y_train, _, _ = app["prepare_datasets"](train_path, test_path)
    assert len(X_train) == len(y_train) == 4
    assert X_train.index.tolist() == y_train.index.tolist()
    assert set(y_train.unique()) == {0, 1, 2}


def test_T12_prepared_features_exclude_timestamp(app, tmp_path):
    df = ticket_rows(6)
    train_path = write_frame(tmp_path / "train.csv", df)
    test_path = write_frame(tmp_path / "test.csv", df)
    X_train, X_test, _, _, _ = app["prepare_datasets"](train_path, test_path)
    assert X_train.columns.tolist() == app["FEATURES"]
    assert X_test.columns.tolist() == app["FEATURES"]
    assert "opened_ts" not in X_train.columns


def test_T13_create_logistic_and_random_forest_models(app):
    X = feature_frame(app)
    y = pd.Series([0, 1, 2] * 6)
    models = app["train_models"](X, y)
    assert set(models) == {"logistic_regression", "random_forest"}
    assert isinstance(models["logistic_regression"].named_steps["model"], LogisticRegression)
    assert isinstance(models["random_forest"].named_steps["model"], RandomForestClassifier)


def test_T14_models_are_fitted_and_independent(app):
    X = feature_frame(app)
    y = pd.Series([0, 1, 2] * 6)
    models = app["train_models"](X, y)
    assert models["logistic_regression"] is not models["random_forest"]
    assert all(hasattr(model.named_steps["model"], "classes_") for model in models.values())
    assert all(set(model.classes_) == {0, 1, 2} for model in models.values())


def test_T15_macro_f1_matches_predictions(app):
    class FakeModel:
        def predict(self, X):
            return np.array([0, 2, 2, 1])

    y = pd.Series([0, 1, 2, 0])
    X = pd.DataFrame({"value": [0, 1, 2, 3]})
    comparison, _ = app["evaluate_models"]({"fake": FakeModel()}, X, y)
    expected = f1_score(y, [0, 2, 2, 1], labels=[0, 1, 2], average="macro", zero_division=0)
    assert np.isclose(comparison.loc[0, "macro_f1"], expected)


def test_T16_weighted_f1_matches_predictions(app):
    class FakeModel:
        def predict(self, X):
            return np.array([0, 2, 2, 1])

    y = pd.Series([0, 1, 2, 0])
    X = pd.DataFrame({"value": [0, 1, 2, 3]})
    comparison, _ = app["evaluate_models"]({"fake": FakeModel()}, X, y)
    expected = f1_score(y, [0, 2, 2, 1], labels=[0, 1, 2], average="weighted", zero_division=0)
    assert np.isclose(comparison.loc[0, "weighted_f1"], expected)


def test_T17_confusion_matrix_has_all_classes(app):
    class FakeModel:
        def predict(self, X):
            return np.array([0, 1, 2, 0])

    y = pd.Series([0, 1, 2, 0])
    X = pd.DataFrame({"value": [0, 1, 2, 3]})
    _, matrices = app["evaluate_models"]({"fake": FakeModel()}, X, y)
    assert matrices["fake"].shape == (3, 3)
    assert matrices["fake"].sum() == len(y)
    assert np.array_equal(matrices["fake"], confusion_matrix(y, y, labels=[0, 1, 2]))


def test_T18_sort_metrics_and_select_best_model(app):
    class FakeModel:
        def __init__(self, predictions):
            self.predictions = np.asarray(predictions)

        def predict(self, X):
            return self.predictions

    y = pd.Series([0, 1, 2, 0, 1, 2])
    X = pd.DataFrame({"value": range(6)})
    models = {
        "zeta": FakeModel([0, 1, 2, 0, 1, 2]),
        "alpha": FakeModel([0, 1, 2, 0, 1, 2]),
        "beta": FakeModel([0, 0, 2, 0, 0, 2]),
    }
    comparison, _ = app["evaluate_models"](models, X, y)
    assert comparison["model_name"].tolist() == ["alpha", "zeta", "beta"]
    assert comparison["macro_f1"].is_monotonic_decreasing
    name, selected = app["select_best_model"](comparison, models)
    assert name == "alpha" and selected is models["alpha"]


def test_T19_inverse_labels_and_probability_outputs(app):
    class FakeModel:
        classes_ = np.array([0, 1, 2])

        def predict(self, X):
            return np.array([0, 2, 1])

        def predict_proba(self, X):
            return np.array([[0.8, 0.1, 0.1], [0.1, 0.2, 0.7], [0.2, 0.7, 0.1]])

    encoder = LabelEncoder().fit(app["CLASS_NAMES"])
    df = feature_frame(app, 3)
    df["ticket_id"] = ["T1", "T2", "T3"]
    result = app["predict_priority"](FakeModel(), encoder, df)
    assert result.columns.tolist() == ["ticket_id", "predicted_priority", "confidence", "high_probability"]
    assert result["ticket_id"].tolist() == ["T1", "T2", "T3"]
    assert result["predicted_priority"].tolist() == ["HIGH", "MEDIUM", "LOW"]
    assert result["confidence"].tolist() == [0.8, 0.7, 0.7]
    assert result["high_probability"].tolist() == [0.8, 0.1, 0.2]


def test_T20_train_predict_write_artifacts(app, tmp_path, monkeypatch):
    train = ticket_rows(36)
    test = ticket_rows(12)
    future = ticket_rows(8, include_target=False)
    train.to_csv(tmp_path / "ticket_train.csv", index=False)
    test.to_csv(tmp_path / "ticket_test.csv", index=False)
    future.to_csv(tmp_path / "ticket_predict.csv", index=False)
    monkeypatch.chdir(tmp_path)

    name, comparison = app["train"]()
    assert name in comparison["model_name"].tolist()
    assert (tmp_path / "best_model.pkl").is_file()
    assert (tmp_path / "model_comparison.csv").is_file()
    assert (tmp_path / "confusion_matrix.csv").is_file()
    assert set(joblib.load(tmp_path / "best_model.pkl")) == {"model", "encoder"}

    result = app["predict"]()
    assert len(result) == len(future)
    assert (tmp_path / "ticket_predictions.csv").is_file()
