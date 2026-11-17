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

CASE = "b"

def test_T01_dedup(s, state, tmp_path):
    df=s["load_data"](str(BASE/"ticket_train.csv")); assert df["ticket_id"].is_unique

def test_T02_timestamp(s, state, tmp_path):
    df=s["load_data"](str(BASE/"ticket_train.csv")); assert pd.api.types.is_datetime64_any_dtype(df["opened_ts"]); assert df["opened_ts"].notna().all()

def test_T03_infinity(s, state, tmp_path):
    df=s["load_data"](str(BASE/"ticket_train.csv")); assert not np.isinf(df[s["RAW_NUMERIC"]].to_numpy(dtype=float)).any()

def test_T04_numericstring(s, state, tmp_path):
    df=s["load_data"](str(BASE/"ticket_train.csv")); assert not df["customer_tier"].str.contains(r"\.0$",regex=True).any()

def test_T05_targetnormal(s, state, tmp_path):
    df=s["load_data"](str(BASE/"ticket_train.csv")); assert df["priority"].dropna().str.upper().eq(df["priority"].dropna()).all(); assert not df["priority"].dropna().str.contains(" ").any()

def test_T06_datetimefeatures(s, state, tmp_path):
    df=s["load_data"](str(BASE/"ticket_test.csv")); assert (df["opened_hour"]==df["opened_ts"].dt.hour).all() and (df["opened_month"]==df["opened_ts"].dt.month).all()

def test_T07_safe_division(s, state, tmp_path):
    df=s["load_data"](str(BASE/"ticket_train.csv")); assert not np.isinf(df["backlog_per_agent"].dropna().to_numpy()).any()

def test_T08_features(s, state, tmp_path):
    assert len(s["FEATURES"])==11; assert "ticket_id" not in s["FEATURES"] and s["TARGET"] not in s["FEATURES"]

def test_T09_preprocessor(s, state, tmp_path):
    pipe=s["build_pipeline"](state["models"]["random_forest"].named_steps["model"]); assert isinstance(pipe.named_steps["preprocessor"],ColumnTransformer); assert len(pipe.named_steps["preprocessor"].transformers)==2

def test_T10_labelencode(s, state, tmp_path):
    assert isinstance(state["encoder"],LabelEncoder); assert set(state["encoder"].classes_)==set(s["CLASS_NAMES"]); assert set(state["ytr"].unique())=={0,1,2}

def test_T11_invalidtargets(s, state, tmp_path):
    assert state["ytr"].notna().all() and state["yte"].notna().all(); assert len(state["xtr"])==len(state["ytr"])

def test_T12_columnexclude(s, state, tmp_path):
    assert state["xtr"].columns.tolist()==s["FEATURES"]; assert "opened_ts" not in state["xtr"]

def test_T13_modelclasses(s, state, tmp_path):
    assert set(state["models"])=={"logistic_regression","random_forest"}

def test_T14_fitted(s, state, tmp_path):
    assert all(hasattr(p.named_steps["model"],"classes_") for p in state["models"].values())

def test_T15_macro(s, state, tmp_path):
    row=state["comp"].iloc[0]; p=state["models"][row["model_name"]]; y=p.predict(state["xte"]); assert np.isclose(row["macro_f1"],f1_score(state["yte"],y,labels=[0,1,2],average="macro",zero_division=0))

def test_T16_weighted(s, state, tmp_path):
    row=state["comp"].iloc[0]; p=state["models"][row["model_name"]]; y=p.predict(state["xte"]); assert np.isclose(row["weighted_f1"],f1_score(state["yte"],y,labels=[0,1,2],average="weighted",zero_division=0))

def test_T17_confusion(s, state, tmp_path):
    for_name=state["best"][0]; cm=state["matrices"][for_name]; assert cm.shape==(3,3) and cm.sum()==len(state["yte"])

def test_T18_sortbest(s, state, tmp_path):
    c=state["comp"]; assert c["macro_f1"].is_monotonic_decreasing; assert state["best"][1] is state["models"][state["best"][0]]

def test_T19_inverse(s, state, tmp_path):
    df=s["load_data"](str(BASE/"ticket_predict.csv")); r=s["predict_priority"](state["best"][1],state["encoder"],df); assert r.columns.tolist()==["ticket_id","predicted_priority","confidence","high_probability"]; assert set(r["predicted_priority"]).issubset(set(s["CLASS_NAMES"])); assert r["high_probability"].between(0,1).all()

def test_T20_integration(s, state, tmp_path):
    name,comp,result,path=run_integration(s,tmp_path); assert (path/"confusion_matrix.csv").exists() and (path/"ticket_predictions.csv").exists() and len(result)>0

