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

CASE = "d"

def test_T01_customer(s, state, tmp_path):
    df=s["load_data"](str(BASE/"retail_train.csv")); assert df["customer_id"].notna().all() and (df["customer_id"]!="").all()

def test_T02_numericid(s, state, tmp_path):
    df=s["load_data"](str(BASE/"retail_train.csv")); assert not df["customer_id"].str.contains(r"\.0$",regex=True).any()

def test_T03_canceled(s, state, tmp_path):
    df=s["load_data"](str(BASE/"retail_train.csv")); assert df["monetary"].gt(0).all()

def test_T04_nonpositive(s, state, tmp_path):
    df=s["load_data"](str(BASE/"retail_test.csv")); assert (df["monetary"]>0).all() and (df["frequency"]>=1).all()

def test_T05_validdates(s, state, tmp_path):
    df=s["load_data"](str(BASE/"retail_train.csv")); assert df["recency_days"].ge(0).all()

def test_T06_amount(s, state, tmp_path):
    mini=pd.DataFrame({"customer_id":["999"],"invoice_no":["A1"],"invoice_date":["2026-11-25 12:00"],"quantity":[2],"unit_price":[5.]}); p=tmp_path/"tiny.csv"; mini.to_csv(p,index=False); df=s["load_data"](str(p)); assert df.iloc[0]["monetary"]==10.

def test_T07_group(s, state, tmp_path):
    df=s["load_data"](str(BASE/"retail_train.csv")); assert df["customer_id"].is_unique

def test_T08_nunique(s, state, tmp_path):
    mini=pd.DataFrame({"customer_id":["999","999"],"invoice_no":["A1","A1"],"invoice_date":["2026-11-25 12:00"]*2,"quantity":[2,3],"unit_price":[5.,2.]}); p=tmp_path/"tiny.csv"; mini.to_csv(p,index=False); df=s["load_data"](str(p)); assert df.iloc[0]["frequency"]==1

def test_T09_monetary(s, state, tmp_path):
    mini=pd.DataFrame({"customer_id":["999","999"],"invoice_no":["A1","A2"],"invoice_date":["2026-11-25 12:00"]*2,"quantity":[2,3],"unit_price":[5.,2.]}); p=tmp_path/"tiny.csv"; mini.to_csv(p,index=False); df=s["load_data"](str(p)); assert df.iloc[0]["monetary"]==16.

def test_T10_recency(s, state, tmp_path):
    mini=pd.DataFrame({"customer_id":["999"],"invoice_no":["A1"],"invoice_date":["2026-11-25 12:00"],"quantity":[2],"unit_price":[5.]}); p=tmp_path/"tiny.csv"; mini.to_csv(p,index=False); df=s["load_data"](str(p)); assert df.iloc[0]["recency_days"]==6

def test_T11_order(s, state, tmp_path):
    df=s["load_data"](str(BASE/"retail_train.csv")); raw=pd.read_csv(BASE/"retail_train.csv",dtype=str); assert df.iloc[0]["customer_id"].replace(".0","")==raw.iloc[0]["customer_id"].replace(".0","")

def test_T12_pipeline(s, state, tmp_path):
    p=s["build_pipeline"](3); assert list(p.named_steps)==["imputer","log","scaler","model"] and p.named_steps["model"].n_clusters==3

def test_T13_log(s, state, tmp_path):
    p=s["build_pipeline"](3); assert isinstance(p.named_steps["log"],FunctionTransformer); assert np.allclose(p.named_steps["log"].transform(np.array([[0.,np.e-1]])),np.array([[0.,1.]]))

def test_T14_candidates(s, state, tmp_path):
    assert set(state["models"])=={"kmeans_3","kmeans_4","kmeans_5"}; assert all(hasattr(p.named_steps["model"],"cluster_centers_") for p in state["models"].values())

def test_T15_silhouette(s, state, tmp_path):
    row=state["comp"].iloc[0]; model=state["models"][row["model_name"]]; labels=model.predict(state["b"][s["RFM_COLUMNS"]]); transformed=model[:-1].transform(state["b"][s["RFM_COLUMNS"]]); assert np.isclose(row["silhouette_score"],silhouette_score(transformed,labels))

def test_T16_dbscore(s, state, tmp_path):
    row=state["comp"].iloc[0]; model=state["models"][row["model_name"]]; labels=model.predict(state["b"][s["RFM_COLUMNS"]]); transformed=model[:-1].transform(state["b"][s["RFM_COLUMNS"]]); assert np.isclose(row["davies_bouldin_score"],davies_bouldin_score(transformed,labels))

def test_T17_sort(s, state, tmp_path):
    c=state["comp"]; assert c["silhouette_score"].is_monotonic_decreasing and c.columns.tolist()==["model_name","silhouette_score","davies_bouldin_score"]

def test_T18_select(s, state, tmp_path):
    assert state["best"][1] is state["models"][state["best"][0]]

def test_T19_segmentation(s, state, tmp_path):
    customers=s["load_data"](str(BASE/"retail_predict.csv")); r=s["segment_customers"](state["best"][1],customers); assert r.columns.tolist()==["customer_id","segment_id"] and len(r)==len(customers); assert pd.api.types.is_integer_dtype(r["segment_id"])

def test_T20_integration(s, state, tmp_path):
    name,comp,result,path=run_integration(s,tmp_path); assert (path/"best_model.pkl").exists() and (path/"retail_segments.csv").exists() and len(result)>0

