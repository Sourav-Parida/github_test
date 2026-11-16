"""Instructor tests for the supplemental Milestone 2 logistics case study.

20 independent tests x 3 marks = 60 marks.
The completed notebook is tested by default. For candidate evaluation,
set MS2_NOTEBOOK=solution.ipynb (after the candidate fills in the notebook).
No original CSV files are modified.
"""
import os
from pathlib import Path
from types import ModuleType

import joblib
import nbformat
import numpy as np
import pandas as pd
import pytest
from sklearn.base import BaseEstimator
from sklearn.pipeline import Pipeline
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import balanced_accuracy_score, precision_score, recall_score, f1_score


@pytest.fixture(scope="module")
def app():
    notebook_path = Path(__file__).with_name(os.environ.get("MS2_NOTEBOOK", "solution_with_code.ipynb"))
    notebook = nbformat.read(notebook_path, as_version=4)
    module = ModuleType("milestone_solution")
    for cell in notebook.cells:
        if cell.cell_type != "code":
            continue
        source = cell.source.strip()
        if not source or source in {"train()", "predict()"}:
            continue
        exec(compile(source, str(notebook_path), "exec"), module.__dict__)
    return module


def fixture_df(n=30):
    days = pd.date_range("2026-03-01 08:00", periods=n, freq="12h")
    return pd.DataFrame({
        "shipment_id": [f"TKT-{i:04d}" for i in range(n)],
        "booked_at": days.strftime("%Y-%m-%d %H:%M"),
        "dispatch_note": [f"DIST: {100+i*4} km | WT: {1+i*.2:.1f} kg | ZONE: {['metro','regional','remote'][i%3]}" for i in range(n)],
        "items_count": [i%6+1 for i in range(n)],
        "driver_experience_years": [float(i%9+1) for i in range(n)],
        "hub_queue_minutes": [float(i%14*7+5) for i in range(n)],
        "prior_attempts": [i%3 for i in range(n)],
        "promised_hours": [24 if i%3==0 else 48 if i%3==1 else 72 for i in range(n)],
        "service_type": [["express", "standard", "economy"][i%3] for i in range(n)],
        "weather_condition": ["clear", "rain", "fog", "storm"]*(n//4)+["clear", "rain", "fog", "storm"][:n%4],
        "hub_status": ["normal", "congested", "restricted"]*(n//3)+["normal", "congested", "restricted"][:n%3],
        "late_delivery": ["yes" if i%3==0 else "no" for i in range(n)],
    })


def save_frame(path, df):
    df.to_csv(path, index=False)
    return str(path)


# T01-T07: Loading, re and feature engineering (3 marks each)

def test_t01_first_duplicate_retained(app, tmp_path):
    df=fixture_df(4)
    df.loc[2,"shipment_id"]=df.loc[0,"shipment_id"]
    saved=save_frame(tmp_path/"dup.csv",df)
    out=app.load_data(saved)
    assert out["shipment_id"].tolist()==["TKT-0000","TKT-0001","TKT-0003"]
    assert out.iloc[0]["items_count"]==1


def test_t02_invalid_timestamps_and_weekend(app, tmp_path):
    df=fixture_df(3)
    df.loc[0,"booked_at"]="2026-03-07 22:30"  # Saturday
    df.loc[1,"booked_at"]="08/03/2026 09:15"  # Sunday, day-first
    df.loc[2,"booked_at"]="invalid timestamp"
    out=app.load_data(save_frame(tmp_path/"dates.csv",df))
    assert len(out)==2 and out["booking_hour"].tolist()==[22,9]
    assert out["is_weekend"].tolist()==[1,1]


def test_t03_coerce_raw_numeric(app, tmp_path):
    df=fixture_df(3)
    df.loc[0,"items_count"]="not-a-number"
    df.loc[1,"hub_queue_minutes"]="bad"
    df.loc[2,"driver_experience_years"]="?"
    out=app.load_data(save_frame(tmp_path/"numeric.csv",df))
    assert pd.isna(out.iloc[0]["items_count"])
    assert pd.isna(out.iloc[1]["hub_queue_minutes"])
    assert pd.isna(out.iloc[2]["driver_experience_years"])
    assert all(pd.api.types.is_numeric_dtype(out[col]) for col in app.RAW_NUMERIC)


def test_t04_normalize_categories(app, tmp_path):
    df=fixture_df(3)
    df.loc[0,"service_type"]="  EXPRESS "
    df.loc[1,"weather_condition"]="  "
    df.loc[2,"hub_status"]=None
    out=app.load_data(save_frame(tmp_path/"categories.csv",df))
    assert out["service_type"].iloc[0]=="express"
    assert out["weather_condition"].iloc[1]=="unknown"
    assert out["hub_status"].iloc[2]=="unknown"


def test_t05_regex_distance_formats(app):
    assert app.extract_note_features(" DIST: 125.5 km ")[0]==125.5
    assert app.extract_note_features("wt=3KG; dist=340KM; zone=remote")[0]==340
    assert np.isnan(app.extract_note_features("DIST=oops; WT=2kg")[0])


def test_t06_regex_weight_zone_and_missing(app):
    assert app.extract_note_features("ZONE=REMOTE | wt=7.25KG")[1:]==(7.25,"remote")
    d,w,z=app.extract_note_features("no usable details")
    assert np.isnan(d) and np.isnan(w) and z=="unknown"
    assert app.extract_note_features(None)[2]=="unknown"


def test_t07_preserve_raw_fields_and_engineered_columns(app, tmp_path):
    df=fixture_df(5)
    df["audit_notes"]="keep"
    out=app.load_data(save_frame(tmp_path/"cols.csv",df))
    assert out["shipment_id"].tolist()==df["shipment_id"].tolist()
    assert all(c in out.columns for c in app.FEATURES)
    assert {"late_delivery","dispatch_note","audit_notes"}.issubset(out.columns)
    assert len(app.NUMERIC_FEATURES)==9 and len(app.CATEGORICAL_FEATURES)==4


# T08-T09: Preprocessing pipeline

def test_t08_column_transformer_groups(app):
    algo=DecisionTreeClassifier(random_state=42)
    p=app.build_pipeline(algo)
    assert isinstance(p,Pipeline) and p.named_steps["model"] is algo
    ct=p.named_steps["preprocessor"]
    assert ct.__class__.__name__=="ColumnTransformer"
    groups={name:list(cols) for name,_,cols in ct.transformers}
    assert groups["numeric"]==app.NUMERIC_FEATURES
    assert groups["category"]==app.CATEGORICAL_FEATURES


def test_t09_training_fitted_preprocessing_unseen_categories(app, tmp_path):
    df=fixture_df(35)
    df.loc[0,"hub_queue_minutes"]=np.nan
    train=app.load_data(save_frame(tmp_path/"train.csv",df))
    p=app.build_pipeline(DecisionTreeClassifier(random_state=42))
    p.fit(train[app.FEATURES],(df["late_delivery"]=="yes").astype(int))
    new=train.iloc[:2].copy()
    new.loc[new.index[0],"hub_queue_minutes"]=np.nan
    new.loc[new.index[1],"weather_condition"]="hail"
    assert p.predict(new[app.FEATURES]).shape==(2,)
    numeric=p.named_steps["preprocessor"].named_transformers_["numeric"]
    assert "imputer" in numeric.named_steps and "scaler" in numeric.named_steps
    assert np.isfinite(numeric.named_steps["imputer"].statistics_).all()


# T10-T12: Supervised datasets

def test_t10_prepare_return_types_and_feature_counts(app, tmp_path):
    df=fixture_df(25)
    a,b,y1,y2=app.prepare_datasets(save_frame(tmp_path/"a.csv",df),save_frame(tmp_path/"b.csv",df))
    assert all(isinstance(x,pd.DataFrame) for x in (a,b))
    assert all(isinstance(x,pd.Series) for x in (y1,y2))
    assert a.columns.tolist()==app.FEATURES and b.columns.tolist()==app.FEATURES
    assert len(a.columns)==13 and set(y1.unique())=={0,1}


def test_t11_target_mapping_and_invalid_removal(app, tmp_path):
    df=fixture_df(8)
    df.loc[0,"late_delivery"]=" YES "
    df.loc[1,"late_delivery"]=" NO "
    df.loc[2,"late_delivery"]="pending"
    df.loc[3,"late_delivery"]=None
    X,_,y,_=app.prepare_datasets(save_frame(tmp_path/"tr.csv",df),save_frame(tmp_path/"te.csv",df))
    assert len(y)==6 and len(X)==6 and y.iloc[0]==1 and y.iloc[1]==0
    assert pd.api.types.is_integer_dtype(y)


def test_t12_alignment_after_invalid_rows(app, tmp_path):
    df=fixture_df(8)
    df.loc[4,"booked_at"]="bad"
    df.loc[5,"shipment_id"]=df.loc[0,"shipment_id"]
    df.loc[6,"late_delivery"]="unknown"
    X,_,y,_=app.prepare_datasets(save_frame(tmp_path/"t.csv",df),save_frame(tmp_path/"s.csv",df))
    assert len(X)==len(y)==5
    assert X.index.tolist()==y.index.tolist()
    assert not any(c in X.columns for c in ["shipment_id","booked_at","dispatch_note","late_delivery"])


@pytest.fixture(scope="module")
def trained(app, tmp_path_factory):
    tmp=tmp_path_factory.mktemp("trained")
    df=fixture_df(80)
    path=save_frame(tmp/"fit.csv",df)
    X,_,y,_=app.prepare_datasets(path,path)
    return app.train_models(X,y),X,y


# T13-T14: Model training

def test_t13_models_and_hyperparameters(app, trained):
    fitted,_,_=trained
    assert list(fitted)==["decision_tree","random_forest"]
    dt=fitted["decision_tree"].named_steps["model"]
    rf=fitted["random_forest"].named_steps["model"]
    assert isinstance(dt,DecisionTreeClassifier) and isinstance(rf,RandomForestClassifier)
    assert (dt.max_depth,dt.min_samples_leaf,dt.class_weight,dt.random_state)==(8,4,"balanced",42)
    assert (rf.n_estimators,rf.max_depth,rf.min_samples_leaf,rf.class_weight,rf.random_state,rf.n_jobs)==(120,10,2,"balanced",42,-1)


def test_t14_separate_fitted_pipelines(app, trained):
    fitted,X,_=trained
    assert fitted["decision_tree"] is not fitted["random_forest"]
    for p in fitted.values():
        assert p.predict(X.iloc[:4]).shape==(4,)
        proba=p.predict_proba(X.iloc[:4])
        assert proba.shape==(4,2) and np.allclose(proba.sum(axis=1),1)


# T15-T16: Model evaluation

def test_t15_all_metrics_correct(app):
    class Fake:
        def __init__(self,pred): self.pred=np.array(pred)
        def predict(self,x): return self.pred
    y=pd.Series([0,0,1,1])
    preds=[0,1,1,0]
    compare=app.evaluate_models({"a":Fake(preds),"b":Fake([0,0,1,1])},pd.DataFrame({"x":[1,2,3,4]}),y)
    a=compare.set_index("model_name").loc["a"]
    assert np.isclose(a.balanced_accuracy,balanced_accuracy_score(y,preds))
    assert np.isclose(a.precision,precision_score(y,preds))
    assert np.isclose(a.recall,recall_score(y,preds))
    assert np.isclose(a.f1,f1_score(y,preds))


def test_t16_sorted_schema_and_no_refitting(app):
    class Fake:
        def __init__(self,pred): self.pred=np.array(pred)
        def predict(self,x): return self.pred
        def fit(self,*a): raise AssertionError("must not refit")
    comp=app.evaluate_models({"worse":Fake([1,1,1,1]),"better":Fake([0,0,1,1])},pd.DataFrame({"x":[0,1,2,3]}),pd.Series([0,0,1,1]))
    assert comp.columns.tolist()==["model_name","balanced_accuracy","precision","recall","f1"]
    assert comp["model_name"].tolist()==["better","worse"]
    assert comp.index.tolist()==[0,1]


# T17: Model selection

def test_t17_best_model_is_existing_instance(app):
    comparison=pd.DataFrame({"model_name":["forest","tree"],"balanced_accuracy":[.8,.6]})
    models={"tree":object(),"forest":object()}
    name,selected=app.select_best_model(comparison,models)
    assert name=="forest" and selected is models["forest"]


# T18-T19: Prediction without training

def test_t18_predict_schema_and_order(app):
    class Fake:
        classes_=np.array([0,1])
        def predict(self,X): return np.array([1,0])
        def predict_proba(self,X): return np.array([[.12345,.87655],[.65433,.34567]])
    df=fixture_df(2)
    df["extra"]="keep"
    for name in app.FEATURES:
        if name not in df:
            df[name]=1 if name in app.NUMERIC_FEATURES else "metro"
    result=app.predict_delay(Fake(),df)
    assert result.columns.tolist()==["shipment_id","predicted_delay","delay_probability"]
    assert result.shipment_id.tolist()==df.shipment_id.tolist()
    assert result.predicted_delay.tolist()==[1,0]


def test_t19_positive_probabilities_rounded_no_fit(app):
    class Fake:
        classes_=np.array([1,0])
        def predict(self,X): return np.array([1,1])
        def predict_proba(self,X): return np.array([[.123456,.876544],[.888888,.111112]])
        def fit(self,*a): raise AssertionError("must not train")
    df=fixture_df(2)
    for name in app.FEATURES:
        if name not in df:
            df[name]=1 if name in app.NUMERIC_FEATURES else "metro"
    result=app.predict_delay(Fake(),df)
    assert result.delay_probability.tolist()==[.1235,.8889]
    assert result.predicted_delay.tolist()==[1,1]


# T20: Full train/predict integration

def test_t20_train_and_predict_end_to_end(app, tmp_path, monkeypatch):
    df=fixture_df(90)
    train=df.iloc[:60].copy()
    test=df.iloc[60:80].copy()
    future=df.iloc[80:].drop(columns=["late_delivery"]).copy()
    save_frame(tmp_path/"delivery_train.csv",train)
    save_frame(tmp_path/"delivery_test.csv",test)
    save_frame(tmp_path/"delivery_predict.csv",future)
    monkeypatch.chdir(tmp_path)
    assert not (tmp_path/"best_model.pkl").exists()
    name,comparison=app.train()
    assert name in {"decision_tree","random_forest"}
    assert (tmp_path/"best_model.pkl").exists() and (tmp_path/"model_comparison.csv").exists()
    persisted=joblib.load("best_model.pkl")
    assert isinstance(persisted,Pipeline)
    result=app.predict()
    assert len(result)==10 and (tmp_path/"delivery_predictions.csv").exists()
    assert pd.read_csv("delivery_predictions.csv").columns.tolist()==["shipment_id","predicted_delay","delay_probability"]
