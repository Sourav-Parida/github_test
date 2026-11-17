"""Exactly 20 independently graded checks (3 marks each = 60 marks)."""
import os
from pathlib import Path

import joblib
import nbformat
import numpy as np
import pandas as pd
import pytest
from sklearn.cluster import KMeans
from sklearn.metrics import davies_bouldin_score, silhouette_score
from sklearn.pipeline import Pipeline


BASE = Path(__file__).resolve().parent
REFERENCE_DATE = pd.Timestamp("2026-12-01")


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


def invoice_rows(customers=3, invoices_per_customer=2):
    rows = []
    for customer_index in range(customers):
        customer_id = str(1000 + customer_index)
        for invoice_index in range(invoices_per_customer):
            days_ago = 4 + customer_index * 3 + invoice_index
            rows.append({
                "customer_id": customer_id,
                "invoice_no": f"INV-{customer_index:03d}-{invoice_index:02d}",
                "invoice_date": (REFERENCE_DATE - pd.Timedelta(days=days_ago)).strftime("%Y-%m-%d %H:%M"),
                "quantity": customer_index % 4 + invoice_index + 1,
                "unit_price": float(customer_index + invoice_index + 2),
            })
    return pd.DataFrame(rows)


def write_frame(path, df):
    df.to_csv(path, index=False)
    return str(path)


def customer_frame(n=18):
    index = np.arange(n)
    return pd.DataFrame({
        "customer_id": [f"C{i:03d}" for i in index],
        "recency_days": (index % 6) * 20 + 1,
        "frequency": index % 5 + 1,
        "monetary": (index % 4 + 1) * 100 + index * 3,
    })


def test_T01_remove_missing_and_empty_customer_ids(app, tmp_path):
    df = invoice_rows(3, 1)
    df.loc[1, "customer_id"] = ""
    df.loc[2, "customer_id"] = None
    result = app["load_data"](write_frame(tmp_path / "ids.csv", df))
    assert result["customer_id"].tolist() == ["1000"]


def test_T02_clean_numeric_like_customer_ids(app, tmp_path):
    df = invoice_rows(2, 1)
    df["customer_id"] = ["1000.0", "1001.0"]
    result = app["load_data"](write_frame(tmp_path / "numeric-ids.csv", df))
    assert result["customer_id"].tolist() == ["1000", "1001"]
    assert not result["customer_id"].str.contains(r"\.0$", regex=True).any()


def test_T03_exclude_canceled_invoices_and_nonpositive_monetary(app, tmp_path):
    df = invoice_rows(2, 1)
    canceled = df.iloc[[0]].copy()
    canceled["invoice_no"] = "CANCEL-1"
    result = app["load_data"](write_frame(tmp_path / "canceled.csv", pd.concat([df, canceled], ignore_index=True)))
    assert not result["monetary"].le(0).any()
    assert len(result) == 2


def test_T04_filter_nonpositive_transactions(app, tmp_path):
    df = invoice_rows(4, 1)
    df.loc[0, "quantity"] = 0
    df.loc[1, "unit_price"] = -2
    result = app["load_data"](write_frame(tmp_path / "nonpositive.csv", df))
    assert result["frequency"].ge(1).all()
    assert result["monetary"].gt(0).all()
    assert set(result["customer_id"]) == {"1002", "1003"}


def test_T05_remove_invalid_and_future_dates_with_nonnegative_recency(app, tmp_path):
    df = invoice_rows(3, 1)
    df.loc[0, "invoice_date"] = "not-a-date"
    df.loc[1, "invoice_date"] = "2026-12-02 12:00"
    result = app["load_data"](write_frame(tmp_path / "dates.csv", df))
    assert len(result) == 1
    assert result["recency_days"].ge(0).all()


def test_T06_calculate_invoice_amount(app, tmp_path):
    df = pd.DataFrame({
        "customer_id": ["999"],
        "invoice_no": ["INV-1"],
        "invoice_date": ["2026-11-25 12:00"],
        "quantity": [2],
        "unit_price": [5.0],
    })
    result = app["load_data"](write_frame(tmp_path / "amount.csv", df))
    assert result.loc[0, "monetary"] == 10.0


def test_T07_aggregate_to_one_row_per_customer(app, tmp_path):
    result = app["load_data"](write_frame(tmp_path / "group.csv", invoice_rows(4, 3)))
    assert result["customer_id"].is_unique
    assert len(result) == 4


def test_T08_frequency_counts_unique_invoices(app, tmp_path):
    df = pd.DataFrame({
        "customer_id": ["999", "999"],
        "invoice_no": ["INV-1", "INV-1"],
        "invoice_date": ["2026-11-25 12:00"] * 2,
        "quantity": [2, 3],
        "unit_price": [5.0, 2.0],
    })
    result = app["load_data"](write_frame(tmp_path / "frequency.csv", df))
    assert result.loc[0, "frequency"] == 1


def test_T09_sum_customer_monetary_value(app, tmp_path):
    df = pd.DataFrame({
        "customer_id": ["999", "999"],
        "invoice_no": ["INV-1", "INV-2"],
        "invoice_date": ["2026-11-25 12:00"] * 2,
        "quantity": [2, 3],
        "unit_price": [5.0, 2.0],
    })
    result = app["load_data"](write_frame(tmp_path / "monetary.csv", df))
    assert result.loc[0, "monetary"] == 16.0


def test_T10_recency_uses_reference_date(app, tmp_path):
    df = pd.DataFrame({
        "customer_id": ["999"],
        "invoice_no": ["INV-1"],
        "invoice_date": ["2026-11-25 12:00"],
        "quantity": [2],
        "unit_price": [5.0],
    })
    result = app["load_data"](write_frame(tmp_path / "recency.csv", df))
    assert result.loc[0, "recency_days"] == 6


def test_T11_preserve_customer_first_seen_order(app, tmp_path):
    df = pd.DataFrame({
        "customer_id": ["B", "A", "B"],
        "invoice_no": ["INV-1", "INV-2", "INV-3"],
        "invoice_date": ["2026-11-28", "2026-11-27", "2026-11-29"],
        "quantity": [1, 1, 1],
        "unit_price": [10.0, 10.0, 10.0],
    })
    result = app["load_data"](write_frame(tmp_path / "order.csv", df))
    assert result["customer_id"].tolist() == ["B", "A"]


def test_T12_pipeline_has_expected_steps_and_cluster_count(app):
    pipeline = app["build_pipeline"](3)
    assert isinstance(pipeline, Pipeline)
    assert list(pipeline.named_steps) == ["imputer", "log", "scaler", "model"]
    assert isinstance(pipeline.named_steps["model"], KMeans)
    assert pipeline.named_steps["model"].n_clusters == 3


def test_T13_apply_log1p_before_scaling(app):
    pipeline = app["build_pipeline"](3)
    values = pipeline.named_steps["log"].transform(np.array([[0.0, np.e - 1]]))
    assert np.allclose(values, [[0.0, 1.0]])


def test_T14_fit_three_four_and_five_cluster_candidates(app):
    customers = customer_frame(18)
    models = app["train_models"](customers)
    assert set(models) == {"kmeans_3", "kmeans_4", "kmeans_5"}
    for name, count in (("kmeans_3", 3), ("kmeans_4", 4), ("kmeans_5", 5)):
        model = models[name]
        assert model.named_steps["model"].n_clusters == count
        assert hasattr(model.named_steps["model"], "cluster_centers_")


def test_T15_silhouette_score_matches_cluster_labels(app):
    customers = customer_frame(18)
    model = app["build_pipeline"](3).fit(customers[app["RFM_COLUMNS"]])
    comparison = app["evaluate_models"]({"kmeans_3": model}, customers)
    labels = model.predict(customers[app["RFM_COLUMNS"]])
    transformed = model[:-1].transform(customers[app["RFM_COLUMNS"]])
    assert np.isclose(comparison.loc[0, "silhouette_score"], silhouette_score(transformed, labels))


def test_T16_davies_bouldin_score_matches_cluster_labels(app):
    customers = customer_frame(18)
    model = app["build_pipeline"](3).fit(customers[app["RFM_COLUMNS"]])
    comparison = app["evaluate_models"]({"kmeans_3": model}, customers)
    labels = model.predict(customers[app["RFM_COLUMNS"]])
    transformed = model[:-1].transform(customers[app["RFM_COLUMNS"]])
    assert np.isclose(
        comparison.loc[0, "davies_bouldin_score"],
        davies_bouldin_score(transformed, labels),
    )


def test_T17_sort_comparison_by_silhouette_and_davies_bouldin(app):
    customers = customer_frame(18)
    models = app["train_models"](customers)
    comparison = app["evaluate_models"](models, customers)
    assert comparison.columns.tolist() == [
        "model_name", "silhouette_score", "davies_bouldin_score"
    ]
    assert comparison["silhouette_score"].is_monotonic_decreasing
    assert comparison.index.tolist() == list(range(len(comparison)))


def test_T18_select_existing_top_ranked_model(app):
    comparison = pd.DataFrame({
        "model_name": ["kmeans_4", "kmeans_3"],
        "silhouette_score": [0.8, 0.6],
    })
    models = {"kmeans_3": object(), "kmeans_4": object()}
    name, selected = app["select_best_model"](comparison, models)
    assert name == "kmeans_4" and selected is models["kmeans_4"]


def test_T19_segment_ids_preserve_customer_order(app):
    class FakeModel:
        def predict(self, X):
            return np.array([2, 0, 1])

    customers = customer_frame(3)
    result = app["segment_customers"](FakeModel(), customers)
    assert result.columns.tolist() == ["customer_id", "segment_id"]
    assert result["customer_id"].tolist() == customers["customer_id"].tolist()
    assert result["segment_id"].tolist() == [2, 0, 1]
    assert pd.api.types.is_integer_dtype(result["segment_id"])


def test_T20_train_predict_write_segmentation_artifacts(app, tmp_path, monkeypatch):
    invoice_rows(18, 3).to_csv(tmp_path / "retail_train.csv", index=False)
    invoice_rows(12, 3).to_csv(tmp_path / "retail_test.csv", index=False)
    future = invoice_rows(7, 2)
    future.to_csv(tmp_path / "retail_predict.csv", index=False)
    monkeypatch.chdir(tmp_path)

    name, comparison = app["train"]()
    assert name in comparison["model_name"].tolist()
    assert (tmp_path / "best_model.pkl").is_file()
    assert (tmp_path / "model_comparison.csv").is_file()
    assert isinstance(joblib.load(tmp_path / "best_model.pkl"), Pipeline)

    result = app["predict"]()
    assert len(result) == 7
    assert (tmp_path / "retail_segments.csv").is_file()
    assert pd.read_csv(tmp_path / "retail_segments.csv").columns.tolist() == [
        "customer_id", "segment_id"
    ]
