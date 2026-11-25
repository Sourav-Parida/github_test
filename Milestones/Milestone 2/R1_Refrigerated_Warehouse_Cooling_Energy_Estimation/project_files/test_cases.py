"""AI Services MS2 — Refrigerated Warehouse Cooling Energy Estimation.
20 independent pytest checks × 3 marks = 60 marks.
Tests use small temporary fixtures and never alter the distributed CSV files.
"""
from pathlib import Path
import os
import joblib
import nbformat
import numpy as np
import pandas as pd
import pytest

PROJECT = Path(__file__).resolve().parent


@pytest.fixture(scope="module")
def code():
    book = nbformat.read(PROJECT / os.environ.get("MS2_NOTEBOOK", "solution.ipynb"), as_version=4)
    ns = {"__name__": "assessment_tests"}
    for cell in book.cells:
        if cell.cell_type == "code" and set(cell.metadata.get("tags", [])) & {"setup", "functions"}:
            exec(compile(cell.source, "assessed_notebook.ipynb", "exec"), ns)
    return ns


def sample(n=24, with_target=True):
    dates = pd.date_range("2026-03-01 01:00", periods=n, freq="12h")
    df = pd.DataFrame({
        "reading_id": [f"RUN-{i:04d}" for i in range(n)],
        "reading_start_ts": dates.strftime("%Y-%m-%d %H:%M"),
        "site_code": ["MUM-01", "PUN-02", "BLR-03"] * (n//3) + ["MUM-01"] * (n%3),
        "ambient_temperature_c": np.linspace(22, 40, n),
        "chamber_setpoint_c": [-18, 2, -8] * (n//3) + [-18] * (n%3),
        "goods_load_tonnes": np.linspace(1, 12, n),
        "operating_hours": np.linspace(2, 12, n),
        "door_open_minutes": np.linspace(10, 50, n),
        "compressor_load_pct": np.linspace(35, 90, n),
        "refrigerant_type": ["ammonia", "r134a", "co2"] * (n//3) + ["ammonia"] * (n%3),
        "service_state": ["normal", "inspection_due", "derated"] * (n//3) + ["normal"] * (n%3),
        "shift_code": ["1", "2.0", "3"] * (n//3) + ["1"] * (n%3),
    })
    if with_target:
        df["energy_consumed_kwh"] = (df["goods_load_tonnes"] * 30 + df["operating_hours"] * 25 + 200).round(1)
    return df


def write(tmp_path, df, name="input.csv"):
    p = tmp_path / name
    df.to_csv(p, index=False)
    return str(p)


def trained_pair(code):
    df = sample(90)
    filename = PROJECT / "cooling_train.csv"
    # Small controlled fixture, not a live CSV dependency.
    x = df[code["RAW_NUMERIC"]].copy()
    # Feature loader is exercised separately; reuse exactly the known cleaned feature matrix.
    d = df.copy()
    d["reading_start_ts"] = pd.to_datetime(d["reading_start_ts"])
    d["start_hour"] = d["reading_start_ts"].dt.hour
    d["is_weekend"] = (d["reading_start_ts"].dt.dayofweek >= 5).astype(int)
    d["temperature_gap_c"] = d["ambient_temperature_c"] - d["chamber_setpoint_c"]
    d["load_rate_tph"] = d["goods_load_tonnes"] / d["operating_hours"]
    d["shift_code"] = d["shift_code"].replace({"2.0": "2"})
    return d[code["FEATURES"]], d[code["TARGET"]]


def test_01_first_duplicate_kept(code, tmp_path):
    df = sample(4); duplicate = df.iloc[[0]].copy(); duplicate["goods_load_tonnes"] = 999
    got = code["load_data"](write(tmp_path, pd.concat([df,duplicate])))
    assert len(got) == 4 and got.iloc[0]["goods_load_tonnes"] != 999


def test_02_mixed_dates_and_invalid_removed(code, tmp_path):
    df=sample(3);df.loc[0,"reading_start_ts"]="18/03/2026 22:00";df.loc[1,"reading_start_ts"]="invalid"
    got=code["load_data"](write(tmp_path,df))
    assert len(got)==2 and got.iloc[0]["reading_start_ts"].hour==22


def test_03_numeric_coercion_and_infinity(code, tmp_path):
    df=sample(3); df.loc[0,"goods_load_tonnes"]="invalid";df.loc[1,"door_open_minutes"]="inf"
    got=code["load_data"](write(tmp_path,df))
    assert pd.isna(got.loc[0,"goods_load_tonnes"]) and pd.isna(got.loc[1,"door_open_minutes"])


def test_04_category_strip_lower_and_missing(code, tmp_path):
    df=sample(3);df.loc[0,"site_code"]="  MUM-01 ";df.loc[1,"refrigerant_type"]=" ";df.loc[2,"service_state"]=None
    got=code["load_data"](write(tmp_path,df))
    assert got.loc[0,"site_code"]=="mum-01" and got.loc[1,"refrigerant_type"]=="unknown" and got.loc[2,"service_state"]=="unknown"


def test_05_simple_shift_dot_zero_regex(code,tmp_path):
    df=sample(3);df["shift_code"]=[" +2.000 ","3.0","1"]
    got=code["load_data"](write(tmp_path,df))
    assert got["shift_code"].tolist()==["+2","3","1"]


def test_06_hour_and_weekend(code,tmp_path):
    df=sample(2);df.loc[0,"reading_start_ts"]="2026-03-07 19:30";df.loc[1,"reading_start_ts"]="2026-03-09 03:00"
    got=code["load_data"](write(tmp_path,df))
    assert got["start_hour"].tolist()==[19,3] and got["is_weekend"].tolist()==[1,0]


def test_07_temperature_gap_and_safe_rate(code,tmp_path):
    df=sample(3);df.loc[0,["ambient_temperature_c","chamber_setpoint_c","goods_load_tonnes","operating_hours"]]=[32,-8,6,3]
    df.loc[1,"operating_hours"]=0;df.loc[2,"operating_hours"]=-1
    got=code["load_data"](write(tmp_path,df))
    assert got.loc[0,"temperature_gap_c"]==40 and got.loc[0,"load_rate_tph"]==2
    assert pd.isna(got.loc[1,"load_rate_tph"]) and pd.isna(got.loc[2,"load_rate_tph"])


def test_08_keeps_order_optional_target_and_extra_column(code,tmp_path):
    df=sample(5,False);df["optional_note"]="audit";df=df.iloc[[4,1,3,2,0]]
    got=code["load_data"](write(tmp_path,df))
    assert got["reading_id"].tolist()==df["reading_id"].tolist() and "energy_consumed_kwh" not in got and "optional_note" in got


def test_09_unfitted_model_pipeline(code):
    from sklearn.linear_model import Ridge
    p=code["build_pipeline"](Ridge())
    assert p.__class__.__name__=="Pipeline" and p.named_steps["model"].__class__.__name__=="Ridge"
    assert not hasattr(p.named_steps["preprocessor"], "transformers_")


def test_10_column_transformer_numeric_and_categorical(code):
    from sklearn.linear_model import Ridge
    p=code["build_pipeline"](Ridge())
    ct=p.named_steps["preprocessor"]
    assert ct.__class__.__name__=="ColumnTransformer"
    assert list(ct.transformers[0][2])==code["NUMERIC_FEATURES"]
    assert list(ct.transformers[1][2])==code["CATEGORICAL"]
    num=ct.transformers[0][1]
    assert [name for name,_ in num.steps]==["imputer","scaler"]
    assert ct.transformers[1][1].handle_unknown=="ignore"


def test_11_pipeline_handles_missing_and_unknown_categories(code):
    from sklearn.linear_model import Ridge
    X,y=trained_pair(code)
    p=code["build_pipeline"](Ridge()).fit(X,y)
    new=X.iloc[[0]].copy();new.loc[new.index[0],"site_code"]="new_site";new.loc[new.index[0],"goods_load_tonnes"]=np.nan
    assert np.isfinite(p.predict(new)).all()


def test_12_prepare_returns_types_columns(code,tmp_path):
    train=sample(9);test=sample(6)
    Xtr,Xte,ytr,yte=code["prepare_datasets"](write(tmp_path,train,"train.csv"),write(tmp_path,test,"test.csv"))
    assert isinstance(Xtr,pd.DataFrame) and isinstance(Xte,pd.DataFrame)
    assert isinstance(ytr,pd.Series) and isinstance(yte,pd.Series)
    assert list(Xtr.columns)==code["FEATURES"] and list(Xte.columns)==code["FEATURES"]


def test_13_invalid_infinite_negative_target_excluded(code,tmp_path):
    tr=sample(9);tr.loc[0,code["TARGET"]]=np.nan;tr.loc[1,code["TARGET"]]=-1;tr.loc[2,code["TARGET"]]="inf";tr.loc[3,code["TARGET"]]="bad"
    te=sample(6)
    Xtr,Xte,ytr,yte=code["prepare_datasets"](write(tmp_path,tr,"train.csv"),write(tmp_path,te,"test.csv"))
    assert len(Xtr)==len(ytr)==5 and ytr.ge(0).all() and np.isfinite(ytr).all()
    assert len(Xte)==len(yte)==6


def test_14_models_keys_types_and_parameters(code):
    X,y=trained_pair(code);m=code["train_models"](X,y)
    assert set(m)=={"ridge_regression","random_forest"}
    assert m["ridge_regression"].named_steps["model"].alpha==1.0
    rf=m["random_forest"].named_steps["model"]
    assert (rf.n_estimators,rf.max_depth,rf.min_samples_leaf,rf.random_state,rf.n_jobs)==(120,12,2,42,-1)


def test_15_independent_fitted_pipelines(code):
    X,y=trained_pair(code);m=code["train_models"](X,y)
    assert m["ridge_regression"] is not m["random_forest"]
    assert all(np.isfinite(p.predict(X.iloc[:3])).all() for p in m.values())


def test_16_evaluation_metrics(code):
    class Fake:
        def __init__(self, y):self.y=np.array(y)
        def predict(self,X):return self.y
    y=pd.Series([10.,20.,30.]);X=pd.DataFrame({"a":[1,2,3]})
    res=code["evaluate_models"]({"exact":Fake([10,20,30]),"off":Fake([12,17,30])},X,y)
    perfect=res.set_index("model_name").loc["exact"]
    assert perfect["mae"]==0 and perfect["rmse"]==0 and perfect["r2"]==1
    off=res.set_index("model_name").loc["off"]
    assert off["mae"]==pytest.approx(5/3) and off["rmse"]==pytest.approx((13/3)**.5)


def test_17_comparison_schema_and_mae_order(code):
    class Fake:
        def __init__(self,v):self.v=v
        def predict(self,X):return np.array(self.v)
    y=pd.Series([0.,2.]);X=pd.DataFrame({"a":[1,2]})
    res=code["evaluate_models"]({"bad":Fake([9,9]),"good":Fake([0,2])},X,y)
    assert list(res.columns)==["model_name","mae","rmse","r2"]
    assert res.model_name.tolist()==["good","bad"] and res.index.tolist()==[0,1]


def test_18_selection_reuses_existing_instance(code):
    a,b=object(),object();cmp=pd.DataFrame({"model_name":["second","first"],"mae":[1,2]})
    name,model=code["select_best_model"](cmp,{"first":a,"second":b})
    assert name=="second" and model is b


def test_19_predict_clips_rounds_and_keeps_id_order(code):
    class Fake:
        def predict(self,X):return np.array([-2.13,14.264,2.567])
    df=sample(3,False);df["reading_id"]=["c","a","b"]
    df["start_hour"]=1;df["is_weekend"]=0;df["temperature_gap_c"]=40;df["load_rate_tph"]=1
    got=code["predict_energy"](Fake(),df)
    assert got.columns.tolist()==["reading_id","predicted_energy_kwh"]
    assert got["reading_id"].tolist()==["c","a","b"]
    assert got["predicted_energy_kwh"].tolist()==[0.0,14.3,2.6]


def test_20_saved_model_and_separate_prediction(code,tmp_path,monkeypatch):
    monkeypatch.chdir(tmp_path)
    write(tmp_path,sample(140),"cooling_train.csv")
    write(tmp_path,sample(45),"cooling_test.csv")
    write(tmp_path,sample(13,False),"cooling_predict.csv")
    name,comparison=code["train"]()
    assert name in {"ridge_regression","random_forest"}
    assert Path("best_model.pkl").exists() and Path("model_comparison.csv").exists()
    assert list(pd.read_csv("model_comparison.csv").columns)==["model_name","mae","rmse","r2"]
    loaded=joblib.load("best_model.pkl")
    assert np.isfinite(loaded.predict(code["load_data"]("cooling_predict.csv")[code["FEATURES"]])).all()
    # The inference workflow does not call train_models/fit.
    original=code["train_models"]
    code["train_models"]=lambda *a,**k: (_ for _ in ()).throw(AssertionError("prediction retrained"))
    try:
        got=code["predict"]()
    finally:
        code["train_models"]=original
    assert len(got)==13 and Path("cooling_predictions.csv").exists()
    assert pd.read_csv("cooling_predictions.csv").columns.tolist()==["reading_id","predicted_energy_kwh"]
