"""20 independent MS2 assessment checks (3 marks per case = 60 marks).

Default notebook is the candidate's solution.ipynb.
For instructor verification on the answer notebook:
    MS2_NOTEBOOK=solution_with_code.ipynb python -m pytest test_cases.py -v
"""
import os
import tempfile
from pathlib import Path
from types import SimpleNamespace

import joblib
import nbformat
import numpy as np
import pandas as pd
import pytest
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, f1_score
from sklearn.pipeline import Pipeline


NOTEBOOK = Path(os.getenv("MS2_NOTEBOOK", "solution.ipynb"))


def _load_functions():
    notebook = nbformat.read(NOTEBOOK, as_version=4)
    namespace = {"__name__": "ms2_candidate_notebook"}
    for cell in notebook.cells:
        if cell.cell_type != "code" or "workflow-run" in cell.metadata.get("tags", []):
            continue
        exec(compile(cell.source, f"{NOTEBOOK.name}:cell", "exec"), namespace)
    return SimpleNamespace(**namespace)


@pytest.fixture(scope="module")
def app():
    return _load_functions()


def _raw_rows(n=45, target=True):
    rows = []
    labels = ["Healthy", "Inspect", "Urgent"]
    for i in range(n):
        rows.append({
            "inspection_id": f"I-{i:03d}",
            "inspected_at": f"2026-04-{i % 25 + 1:02d} {i % 24:02d}:30",
            "inlet_pressure_bar": 1.5 + (i % 5) * .2,
            "outlet_pressure_bar": 4.0 + (i % 6) * .2,
            "flow_volume_m3": 60.0 + i,
            "runtime_hours": 4.0 + (i % 4),
            "motor_temperature_c": 58.0 + (i % 8) * 2.1,
            "ambient_temperature_c": 25.0 + (i % 5),
            "vibration_mm_s": 1.3 + (i % 9) * .65,
            "operating_load_pct": 50.0 + (i % 15) * 2.0,
            "pump_type": ["centrifugal", "submersible", "diaphragm"][i % 3],
            "maintenance_zone": ["zone_a", "zone_b", "zone_c"][i % 3],
            "shift_code": str(i % 3 + 1),
            **({"condition_label": labels[i % 3]} if target else {})
        })
    return pd.DataFrame(rows)


def _prepared(app, frame):
    # Simulate the contract: build_pipeline and predict_condition take cleaned input.
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / "fixture.csv"
        frame.to_csv(p, index=False)
        return app.load_data(str(p))


def _file(tmp_path, frame, filename="some.csv"):
    dest = tmp_path / filename
    frame.to_csv(dest, index=False)
    return str(dest)


# T01 - unique identifiers, first occurrence and whitespace cleaning

def test_t01_ids_deduplicated_first(app, tmp_path):
    f = _raw_rows(4)
    f.loc[0, "inspection_id"] = "  ID-1  "
    f.loc[1, "inspection_id"] = "ID-1"
    f.loc[2, "inspection_id"] = "  "
    out = app.load_data(_file(tmp_path, f))
    assert out["inspection_id"].tolist() == ["ID-1", "I-003"]
    assert np.isclose(out.iloc[0]["vibration_mm_s"], f.iloc[0]["vibration_mm_s"])


# T02 - ISO + day-first date/time, invalid rows excluded

def test_t02_mixed_dates_and_invalid(app, tmp_path):
    f = _raw_rows(3)
    f.loc[0, "inspected_at"] = "2026-04-07 06:35"
    f.loc[1, "inspected_at"] = "18/03/2026 22:10"
    f.loc[2, "inspected_at"] = "not-a-date"
    out = app.load_data(_file(tmp_path, f))
    assert out["inspection_hour"].tolist() == [6, 22]


# T03 - raw numeric conversion and infinite to NaN

def test_t03_numeric_and_infinity(app, tmp_path):
    f = _raw_rows(3)
    f[["vibration_mm_s", "outlet_pressure_bar", "operating_load_pct"]] = f[["vibration_mm_s", "outlet_pressure_bar", "operating_load_pct"]].astype(object)
    f.loc[0, "vibration_mm_s"] = "invalid"
    f.loc[1, "outlet_pressure_bar"] = "inf"
    f.loc[2, "operating_load_pct"] = "-inf"
    out = app.load_data(_file(tmp_path, f))
    assert pd.isna(out.loc[0, "vibration_mm_s"])
    assert pd.isna(out.loc[1, "outlet_pressure_bar"])
    assert pd.isna(out.loc[2, "operating_load_pct"])


# T04 - category normalization and unknown fallback

def test_t04_text_categories(app, tmp_path):
    f = _raw_rows(3)
    f.loc[0, "pump_type"] = "  CENTRIFUGAL "
    f.loc[1, "maintenance_zone"] = "   "
    f.loc[2, "pump_type"] = None
    out = app.load_data(_file(tmp_path, f))
    assert out.loc[0, "pump_type"] == "centrifugal"
    assert out.loc[1, "maintenance_zone"] == "unknown"
    assert out.loc[2, "pump_type"] == "unknown"


# T05 - simple decimal-category cleanup

def test_t05_shift_code_regex_cleanup(app, tmp_path):
    f = _raw_rows(4)
    f["shift_code"] = [" 1.0 ", "2.000", "3", None]
    out = app.load_data(_file(tmp_path, f))
    assert out["shift_code"].tolist() == ["1", "2", "3", "unknown"]


# T06 - hour, pressure gain and temperature-rise features

def test_t06_feature_calculations(app, tmp_path):
    f = _raw_rows(2)
    f.loc[0, "inspected_at"] = "2026-03-10 18:25"
    f.loc[0, "inlet_pressure_bar"] = 2.4
    f.loc[0, "outlet_pressure_bar"] = 5.1
    f.loc[0, "motor_temperature_c"] = 73
    f.loc[0, "ambient_temperature_c"] = 28
    out = app.load_data(_file(tmp_path, f))
    assert out.loc[0, "inspection_hour"] == 18
    assert out.loc[0, "pressure_gain_bar"] == pytest.approx(2.7)
    assert out.loc[0, "temperature_rise_c"] == pytest.approx(45)


# T07 - safe flow rate and division-by-zero handling

def test_t07_flow_rate_safe(app, tmp_path):
    f = _raw_rows(3)
    f["runtime_hours"] = [5.0, 0.0, -1.0]
    f["flow_volume_m3"] = [50.0, 50.0, 50.0]
    out = app.load_data(_file(tmp_path, f))
    assert out.loc[0, "flow_rate_m3h"] == pytest.approx(10)
    assert pd.isna(out.loc[1, "flow_rate_m3h"])
    assert pd.isna(out.loc[2, "flow_rate_m3h"])


# T08 - optional target and extra columns preserved through common loader

def test_t08_loader_preserves_columns_and_order(app, tmp_path):
    f = _raw_rows(4, target=False)
    f["extra_note"] = ["A", "B", "C", "D"]
    out = app.load_data(_file(tmp_path, f))
    assert "condition_label" not in out
    assert out["inspection_id"].tolist() == f["inspection_id"].tolist()
    assert out["extra_note"].tolist() == f["extra_note"].tolist()


# T09 - estimator pipeline and ColumnTransformer lists

def test_t09_pipeline_structure(app):
    model = LogisticRegression(max_iter=1000)
    p = app.build_pipeline(model)
    assert isinstance(p, Pipeline)
    assert p.named_steps["model"] is model
    prep = p.named_steps["preprocessor"]
    assert isinstance(prep, ColumnTransformer)
    cols = {name: list(fields) for name, _, fields in prep.transformers}
    assert cols["numeric"] == list(app.numeric_features)
    assert cols["category"] == list(app.category_cols)


# T10 - train-fitted imputation, scaling and unknown category tolerance

def test_t10_fit_transform_unseen_category(app):
    f = _raw_rows(30)
    f.loc[0, "vibration_mm_s"] = np.nan
    f = _prepared(app, f)
    X = f[app.features]
    model = app.build_pipeline(LogisticRegression(max_iter=1000))
    model.fit(X, np.arange(30) % 3)
    new = f.iloc[[3]].copy()
    new.loc[3, "maintenance_zone"] = "zone_unseen"
    new.loc[3, "vibration_mm_s"] = np.nan
    assert model.predict(new[app.features]).shape == (1,)
    numeric = model.named_steps["preprocessor"].named_transformers_["numeric"]
    assert numeric.named_steps["imputer"].strategy == "median"
    assert isinstance(numeric.named_steps["scaler"], __import__('sklearn.preprocessing',fromlist=['StandardScaler']).StandardScaler)


# T11 - correct four return values, types, and feature order

def test_t11_prepare_contract(app, tmp_path):
    f = _raw_rows(21)
    path = _file(tmp_path, f, "train.csv")
    result = app.prepare_datasets(path, path)
    assert isinstance(result, tuple) and len(result) == 4
    Xtr, Xte, ytr, yte = result
    assert isinstance(Xtr, pd.DataFrame) and isinstance(Xte, pd.DataFrame)
    assert isinstance(ytr, pd.Series) and isinstance(yte, pd.Series)
    assert list(Xtr.columns) == list(app.features) == list(Xte.columns)


# T12 - stable title-case cleanup and three-class target encoding

def test_t12_target_normalization_and_filtering(app, tmp_path):
    f = _raw_rows(9)
    f.loc[0, "condition_label"] = " healthy "
    f.loc[1, "condition_label"] = "INSPECT"
    f.loc[2, "condition_label"] = " urgent "
    f.loc[3, "condition_label"] = "bad_class"
    f.loc[4, "condition_label"] = None
    p = _file(tmp_path, f)
    Xtr, Xte, ytr, yte = app.prepare_datasets(p, p)
    assert len(ytr) == 7
    assert ytr.iloc[:3].tolist() == [0, 1, 2]
    assert set(ytr.tolist()) == {0, 1, 2}


# T13 - stable train/test mapping with retained feature/target row alignment

def test_t13_target_alignment(app, tmp_path):
    tr = _raw_rows(12)
    te = _raw_rows(12)
    te["condition_label"] = [" URGENT ", "healthy", "Inspect"] * 4
    path1 = _file(tmp_path, tr, "train.csv")
    path2 = _file(tmp_path, te, "test.csv")
    Xtr, Xte, ytr, yte = app.prepare_datasets(path1, path2)
    assert Xtr.index.equals(ytr.index) and Xte.index.equals(yte.index)
    assert yte.iloc[:3].tolist() == [2,0,1]


# T14 - named classifiers and all specified hyperparameters

def test_t14_model_types_and_parameters(app):
    f = _raw_rows(45)
    f = _prepared(app, f)
    models = app.train_models(f[app.features], pd.Series(np.arange(45) % 3))
    assert set(models) == {"logistic_regression", "random_forest"}
    lr = models["logistic_regression"].named_steps["model"]
    rf = models["random_forest"].named_steps["model"]
    assert isinstance(lr, LogisticRegression)
    assert lr.max_iter == 1000 and lr.class_weight == "balanced" and lr.random_state == 42
    assert isinstance(rf, RandomForestClassifier)
    assert (rf.n_estimators, rf.max_depth, rf.min_samples_leaf, rf.class_weight, rf.random_state, rf.n_jobs) == (150,12,2,"balanced",42,-1)


# T15 - both separate fitted pipelines offer predictions + probabilities

def test_t15_pipelines_fitted_and_probabilities(app):
    f = _raw_rows(45)
    f = _prepared(app, f)
    models = app.train_models(f[app.features], pd.Series(np.arange(45) % 3))
    assert models["logistic_regression"] is not models["random_forest"]
    for m in models.values():
        assert m.predict(f[app.features]).shape == (45,)
        prob = m.predict_proba(f[app.features])
        assert prob.shape == (45,3)
        assert np.allclose(prob.sum(axis=1),1)


class _PredOnly:
    def __init__(self, preds): self.preds=np.asarray(preds)
    def predict(self, X): return self.preds[:len(X)]


# T16 - accuracy, macro and weighted F1 calculations

def test_t16_classification_metrics(app):
    y = pd.Series([0,0,0,1,1,2])
    X = pd.DataFrame({"dummy": range(6)})
    p = np.asarray([0,0,1,1,2,2])
    out = app.evaluate_models({"fixed":_PredOnly(p)}, X, y)
    assert out.loc[0,"accuracy"] == pytest.approx(accuracy_score(y,p))
    assert out.loc[0,"macro_f1"] == pytest.approx(f1_score(y,p,average="macro",labels=[0,1,2]))
    assert out.loc[0,"weighted_f1"] == pytest.approx(f1_score(y,p,average="weighted",labels=[0,1,2]))


# T17 - all three sorting keys + reset_index and no refit

def test_t17_multicolumn_ranking(app):
    y = pd.Series([0,1,2,0,1,2])
    X = pd.DataFrame({"dummy": range(6)})
    names={"z":_PredOnly([0,1,2,0,1,2]), "b":_PredOnly([0,1,2,0,1,2]), "a":_PredOnly([0,0,0,0,0,0])}
    result=app.evaluate_models(names,X,y)
    assert list(result.columns) == ["model_name","accuracy","macro_f1","weighted_f1"]
    assert result["model_name"].tolist() == ["b","z","a"]
    assert result.index.tolist() == [0,1,2]


# T18 - identity of selected model (not newly fitted)

def test_t18_best_model_identity(app):
    f = pd.DataFrame({"model_name":["random_forest","logistic_regression"],"macro_f1":[.9,.7]})
    objs={"random_forest":object(),"logistic_regression":object()}
    name,model=app.select_best_model(f,objs)
    assert name == "random_forest" and model is objs[name]


class _FixedProb:
    classes_ = np.asarray([0,1,2])
    def predict(self,X): return np.asarray([2,0,1])[:len(X)]
    def predict_proba(self,X): return np.asarray([[.11,.17,.72],[.84,.10,.06],[.15,.754321,.095679]])[:len(X)]


# T19 - inverse_transform + correct urgent probability + ID order

def test_t19_prediction_schema(app):
    f = _raw_rows(3, target=False)
    extra = f.copy()
    extra["extra_column"] = "not modeled"
    extra = _prepared(app, extra)
    r=app.predict_condition(_FixedProb(),extra)
    assert list(r.columns)==["inspection_id","predicted_condition","urgent_probability"]
    assert r["predicted_condition"].tolist()==["Urgent","Healthy","Inspect"]
    assert r["inspection_id"].tolist()==f["inspection_id"].tolist()
    assert r["urgent_probability"].tolist()==[.72,.06,.0957]


# T20 - training saves fitted model, model comparison, confusion matrix; independent prediction

def test_t20_train_predict_end_to_end(app, tmp_path, monkeypatch):
    train=_raw_rows(75)
    test=_raw_rows(27)
    pred=_raw_rows(9, target=False)
    for name,data in [("pump_train.csv",train),("pump_test.csv",test),("pump_predict.csv",pred)]:
        data.to_csv(tmp_path/name,index=False)
    monkeypatch.chdir(tmp_path)
    best,comparison=app.train()
    assert best in {"logistic_regression","random_forest"}
    assert (tmp_path/"best_model.pkl").exists()
    assert (tmp_path/"model_comparison.csv").exists()
    assert (tmp_path/"confusion_matrix.csv").exists()
    saved=joblib.load("best_model.pkl")
    assert saved.predict(app.load_data("pump_test.csv")[app.features]).shape==(27,)
    confusion=pd.read_csv("confusion_matrix.csv")
    assert confusion.shape==(3,4)
    assert confusion.iloc[:,1:].to_numpy().sum()==27
    result=app.predict()
    assert result.shape==(9,3)
    assert (tmp_path/"pump_predictions.csv").exists()
    assert set(result["predicted_condition"]).issubset({"Healthy","Inspect","Urgent"})
