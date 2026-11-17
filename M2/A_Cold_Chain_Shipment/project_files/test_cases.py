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

CASE = "a"

def test_T01_dup(s, state, tmp_path):
    df=s["load_data"](str(BASE/"shipment_train.csv")); assert df["shipment_id"].is_unique

def test_T02_datebad(s, state, tmp_path):
    df=s["load_data"](str(BASE/"shipment_test.csv")); assert df["dispatch_ts"].notna().all(); assert pd.api.types.is_datetime64_any_dtype(df["dispatch_ts"])

def test_T03_mixeddate(s, state, tmp_path):
    df=s["load_data"](str(BASE/"shipment_train.csv")); assert df["departure_hour"].between(0,23).all()

def test_T04_numerics(s, state, tmp_path):
    df=s["load_data"](str(BASE/"shipment_train.csv")); assert all(pd.api.types.is_numeric_dtype(df[col]) for col in s["RAW_NUMERIC"])

def test_T05_category(s, state, tmp_path):
    df=s["load_data"](str(BASE/"shipment_train.csv")); assert all(df[col].str.strip().eq(df[col]).all() and df[col].str.lower().eq(df[col]).all() for col in s["CATEGORICAL"])

def test_T06_regexdistance(s, state, tmp_path):
    assert s["extract_decimal"]("Distance: 18.75 km; Weight: 3.2 kg","distance")==18.75

def test_T07_regexweight(s, state, tmp_path):
    assert s["extract_decimal"]("distance: 18 km; weight: 3.25 kg","weight")==3.25; assert np.isnan(s["extract_decimal"]("missing","weight"))

def test_T08_categorydecimal(s, state, tmp_path):
    df=s["load_data"](str(BASE/"shipment_train.csv")); assert not df["route_zone"].str.contains(r"\.0$",regex=True).any()

def test_T09_monthmap(s, state, tmp_path):
    assert s["MONTH_MAP"]["jan"]==1 and s["MONTH_MAP"]["dec"]==12; df=s["load_data"](str(BASE/"shipment_test.csv")); assert df["month_number"].between(1,12).all()

def test_T10_timehour(s, state, tmp_path):
    df=s["load_data"](str(BASE/"shipment_train.csv")); assert (df["departure_hour"]==df["dispatch_ts"].dt.hour).all()

def test_T11_safe_ratio(s, state, tmp_path):
    df=s["load_data"](str(BASE/"shipment_train.csv")); assert not np.isinf(df["distance_per_hour"].dropna().to_numpy()).any()

def test_T12_featurelist(s, state, tmp_path):
    assert len(s["NUMERIC"])==7 and len(s["CATEGORICAL"])==3 and len(s["FEATURES"])==10

def test_T13_columntransformer(s, state, tmp_path):
    p=s["build_pipeline"](state["models"]["logistic_regression"].named_steps["model"]); assert isinstance(p.named_steps["preprocessor"],ColumnTransformer); assert p.named_steps["preprocessor"].transformers[0][2]==s["NUMERIC"]

def test_T14_unseen(s, state, tmp_path):
    df=state["xte"].iloc[:3].copy(); df["region"]="new_region"; assert len(state["models"]["logistic_regression"].predict(df))==3

def test_T15_targetmapping(s, state, tmp_path):
    assert set(state["ytr"].unique())=={0,1}; assert state["ytr"].notna().all()

def test_T16_fittedmodels(s, state, tmp_path):
    assert set(state["models"])=={"logistic_regression","random_forest"}; assert all(hasattr(m.named_steps["model"],"classes_") for m in state["models"].values())

def test_T17_scoremetrics(s, state, tmp_path):
    row=state["comp"].iloc[0]; model=state["models"][row["model_name"]]; idx=list(model.classes_).index(1); preds=(model.predict_proba(state["xte"])[:,idx]>=s["THRESHOLD"]).astype(int); assert np.isclose(row["f1"],f1_score(state["yte"],preds,zero_division=0))

def test_T18_multisort(s, state, tmp_path):
    c=state["comp"]; assert list(c.columns)==["model_name","accuracy","precision","recall","f1"]; assert c["f1"].is_monotonic_decreasing; assert state["best"][1] is state["models"][state["best"][0]]

def test_T19_predict(s, state, tmp_path):
    df=s["load_data"](str(BASE/"shipment_predict.csv")); result=s["predict_delay"](state["best"][1],df); assert result.columns.tolist()==["shipment_id","predicted_late","late_probability"]; assert result["predicted_late"].isin([0,1]).all(); assert result["late_probability"].between(0,1).all()

def test_T20_integration(s, state, tmp_path):
    name,comparison,result,path=run_integration(s,tmp_path); assert (path/"shipment_predictions.csv").exists(); assert len(result)>0 and name in comparison["model_name"].tolist()

