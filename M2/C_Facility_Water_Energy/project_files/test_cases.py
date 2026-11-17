"""Exactly 20 independently graded checks (3 marks each = 60 marks)."""
import os
import shutil
from pathlib import Path
import joblib
import nbformat
import numpy as np
import pandas as pd
import pytest
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import LabelEncoder, FunctionTransformer
from sklearn.metrics import (f1_score, confusion_matrix, mean_absolute_error,
    mean_squared_error, r2_score, silhouette_score, davies_bouldin_score)

BASE = Path(__file__).resolve().parent

@pytest.fixture(scope="module")
def s():
    notebook_name = os.environ.get("MS2_NOTEBOOK", "solution.ipynb")
    notebook = nbformat.read(BASE / notebook_name, as_version=4)
    ns = {"__name__": "notebook_under_test"}
    for cell in notebook.cells:
        if cell.cell_type == "code" and "definitions" in cell.metadata.get("tags", []):
            exec(compile(cell.source, notebook_name, "exec"), ns)
    return ns

@pytest.fixture(scope="module")
def state(s):
    training = {"a": ("shipment_train.csv", "shipment_test.csv"),
                "b": ("ticket_train.csv", "ticket_test.csv"),
                "c": ("water_train.csv", "water_test.csv"),
                "d": ("retail_train.csv", "retail_test.csv")}[CASE]
    if CASE == "d":
        a, b = s["prepare_datasets"](*(str(BASE / f) for f in training))
        models = s["train_models"](a)
        comp = s["evaluate_models"](models, b)
        best = s["select_best_model"](comp, models)
        return {"a":a,"b":b,"models":models,"comp":comp,"best":best}
    prepared = s["prepare_datasets"](*(str(BASE / f) for f in training))
    xtr, xte, ytr, yte = prepared[:4]
    models = s["train_models"](xtr,ytr)
    evaluated = s["evaluate_models"](models,xte,yte)
    comp = evaluated[0] if CASE=="b" else evaluated
    best=s["select_best_model"](comp,models)
    return {"xtr":xtr,"xte":xte,"ytr":ytr,"yte":yte,
            "models":models,"comp":comp,"best":best,
            "encoder":prepared[4] if CASE=="b" else None,
            "matrices":evaluated[1] if CASE=="b" else None}

def run_integration(s, tmp_path):
    # Work in temporary directory so source CSVs stay unchanged.
    patterns = {"a": ["shipment_train.csv","shipment_test.csv","shipment_predict.csv"],
        "b": ["ticket_train.csv","ticket_test.csv","ticket_predict.csv"],
        "c": ["water_train.csv","water_test.csv","water_predict.csv"],
        "d": ["retail_train.csv","retail_test.csv","retail_predict.csv"]}
    for name in patterns[CASE]:
        shutil.copy(BASE/name, tmp_path/name)
    old=os.getcwd()
    try:
        os.chdir(tmp_path)
        name, comparison=s["train"]()
        assert Path("best_model.pkl").is_file()
        assert Path("model_comparison.csv").is_file()
        result=s["predict"]()
        return name,comparison,result,Path(tmp_path)
    finally:
        os.chdir(old)

CASE = "c"

def test_T01_dedup(s, state, tmp_path):
    df=s["load_data"](str(BASE/"water_train.csv")); assert df["reading_id"].is_unique

def test_T02_invaliddate(s, state, tmp_path):
    df=s["load_data"](str(BASE/"water_test.csv")); assert df["reading_ts"].notna().all()

def test_T03_inf(s, state, tmp_path):
    df=s["load_data"](str(BASE/"water_train.csv")); assert not np.isinf(df[s["RAW_NUMERIC"]].to_numpy(dtype=float)).any()

def test_T04_nonnegative(s, state, tmp_path):
    df=s["load_data"](str(BASE/"water_train.csv")); assert (df[s["RAW_NUMERIC"]].fillna(0)>=0).all().all()

def test_T05_timeengineer(s, state, tmp_path):
    df=s["load_data"](str(BASE/"water_train.csv")); assert (df["reading_hour"]==df["reading_ts"].dt.hour).all(); assert df["reading_month"].between(1,12).all()

def test_T06_ratio(s, state, tmp_path):
    df=s["load_data"](str(BASE/"water_train.csv")); assert not np.isinf(df["flow_per_pump_hour"].dropna().to_numpy()).any()

def test_T07_features(s, state, tmp_path):
    assert len(s["FEATURES"])==10 and "reading_ts" not in s["FEATURES"]

def test_T08_steps(s, state, tmp_path):
    p=s["build_pipeline"](state["models"]["ridge_regression"].named_steps["model"]); assert list(p.named_steps)==["imputer","log","scaler","model"]

def test_T09_logtransform(s, state, tmp_path):
    p=s["build_pipeline"](state["models"]["ridge_regression"].named_steps["model"]); assert isinstance(p.named_steps["log"],FunctionTransformer); assert np.allclose(p.named_steps["log"].transform(np.array([[0.,np.e-1]])), np.array([[0.,1.]]))

def test_T10_median(s, state, tmp_path):
    m=state["models"]["ridge_regression"]; assert len(m.named_steps["imputer"].statistics_)==len(s["FEATURES"])

def test_T11_target(s, state, tmp_path):
    assert (state["ytr"]>=0).all() and np.isfinite(state["ytr"]).all()

def test_T12_exclusions(s, state, tmp_path):
    assert state["xtr"].columns.tolist()==s["FEATURES"]; assert s["TARGET"] not in state["xtr"]

def test_T13_models(s, state, tmp_path):
    assert set(state["models"])=={"ridge_regression","random_forest"}

def test_T14_mae(s, state, tmp_path):
    c=state["comp"]; row=c.iloc[0]; pred=state["models"][row["model_name"]].predict(state["xte"]); assert np.isclose(row["mae"],mean_absolute_error(state["yte"],pred))

def test_T15_rmse(s, state, tmp_path):
    c=state["comp"]; row=c.iloc[0]; pred=state["models"][row["model_name"]].predict(state["xte"]); assert np.isclose(row["rmse"],np.sqrt(mean_squared_error(state["yte"],pred)))

def test_T16_r2(s, state, tmp_path):
    c=state["comp"]; row=c.iloc[0]; pred=state["models"][row["model_name"]].predict(state["xte"]); assert np.isclose(row["r2"],r2_score(state["yte"],pred))

def test_T17_sort(s, state, tmp_path):
    c=state["comp"]; assert c["mae"].is_monotonic_increasing; assert state["best"][1] is state["models"][state["best"][0]]

def test_T18_predict(s, state, tmp_path):
    df=s["load_data"](str(BASE/"water_predict.csv")); r=s["predict_energy"](state["best"][1],df); assert r.columns.tolist()==["reading_id","predicted_energy_kwh"]; assert (r["predicted_energy_kwh"]>=0).all(); assert np.allclose(r["predicted_energy_kwh"],r["predicted_energy_kwh"].round(2))

def test_T19_artifact(s, state, tmp_path):
    name,comp,result,path=run_integration(s,tmp_path); assert (path/"best_model.pkl").exists() and (path/"model_comparison.csv").exists(); assert joblib.load(path/"best_model.pkl") is not None

def test_T20_independent(s, state, tmp_path):
    name,comp,result,path=run_integration(s,tmp_path); assert (path/"water_predictions.csv").exists(); assert len(result)>0

