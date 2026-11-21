"""Exactly 20 independent pytest checks, 3 marks each (60 total).
Run: python -m pytest test_cases.py -q
Only definition cells are executed during setup; workflow calls are tested separately.
"""
from pathlib import Path
import shutil
from unittest.mock import Mock
import joblib
import nbformat
import numpy as np
import pandas as pd
import pytest
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.exceptions import NotFittedError
from sklearn.utils.validation import check_is_fitted

HERE = Path(__file__).resolve().parent
RAW = ['distance_km', 'trip_duration_hours', 'payload_kg', 'ambient_temperature_c', 'idle_minutes']
NUM = RAW + ['start_hour', 'average_speed_kmph']
CAT = ['depot_code', 'vehicle_type', 'route_type']
FEATURES = NUM + CAT
TARGET = 'fuel_consumed_litres'
OUT = 'predicted_fuel_consumed_litres'

@pytest.fixture
def api():
    nb = nbformat.read(HERE / 'solution.ipynb', as_version=4)
    ns = {'__name__': 'assessment_definitions'}
    for cell in nb.cells:
        if cell.cell_type == 'code' and 'definitions' in cell.metadata.get('tags', []):
            exec(compile(cell.source, 'solution.ipynb', 'exec'), ns)
    return ns

@pytest.fixture
def records():
    return pd.DataFrame({
        'trip_id': ['Z9', 'B2', 'C3', 'D4'],
        'trip_start_ts': ['2025-01-25 09:15:00', '26/01/2025 17:40', '2025-02-03 00:05:00', '2025-02-04 12:10:00'],
        'distance_km': [100, 60, 160, 25], 'trip_duration_hours': [2, 3, 4, 1],
        'payload_kg': [500, 900, 200, 100], 'ambient_temperature_c': [25, 30, 27, 29],
        'idle_minutes': [10, 5, 0, 8], 'depot_code': ['pune', 'mumbai', 'pune', 'nashik'],
        'vehicle_type': ['van', 'light_truck', 'van', 'medium_truck'], 'route_type': ['urban', 'highway', 'mixed', 'urban'],
        TARGET: [14., 12., 19., 6.], 'export_note': ['a', 'b', 'c', 'd']})

def write(df, tmp_path, name='fixture.csv'):
    path = tmp_path / name
    df.to_csv(path, index=False)
    return str(path)

@pytest.fixture
def cleaned(api, records, tmp_path):
    return api['load_data'](write(records, tmp_path))

@pytest.fixture
def supervised(api):
    return api['prepare_datasets'](str(HERE/'fleet_train.csv'), str(HERE/'fleet_test.csv'))

@pytest.fixture
def fitted(api, supervised):
    Xtr, _, ytr, _ = supervised
    return api['train_models'](Xtr, ytr)

# T01 — first duplicate retained

def test_t01_duplicate_id(api, records, tmp_path):
    dup = records.iloc[[0]].assign(distance_km=999)
    actual = api['load_data'](write(pd.concat([records, dup]), tmp_path))
    assert actual.trip_id.tolist() == records.trip_id.tolist()
    assert actual.iloc[0].distance_km == 100

# T02 — invalid timestamps removed

def test_t02_invalid_timestamp(api, records, tmp_path):
    records.loc[1,'trip_start_ts'] = 'not-date'
    records.loc[2,'trip_start_ts'] = None
    actual = api['load_data'](write(records, tmp_path))
    assert actual.trip_id.tolist() == ['Z9','D4']
    assert pd.api.types.is_datetime64_any_dtype(actual.trip_start_ts)

# T03 — mixed timestamps and hour

def test_t03_mixed_formats(cleaned):
    assert cleaned.start_hour.tolist() == [9,17,0,12]
    assert cleaned.trip_start_ts.dt.month.tolist() == [1,1,2,2]
    assert cleaned.trip_start_ts.dt.day.tolist() == [25,26,3,4]

# T04 — all five numeric fields

def test_t04_numeric_conversion(api, records, tmp_path):
    for c in RAW:
        records[c] = ['12.5','bad','inf',None]
    actual = api['load_data'](write(records, tmp_path))
    for c in RAW:
        assert pd.api.types.is_numeric_dtype(actual[c])
        assert actual[c].iloc[0] == 12.5
        assert actual[c].iloc[1:].isna().all()

# T05 — all categories

def test_t05_category_normalization(api, records, tmp_path):
    for c in CAT: records[c] = ['  MiXeD ', ' ', None, ' NORMAL ']
    actual = api['load_data'](write(records, tmp_path))
    for c in CAT: assert actual[c].tolist() == ['mixed','unknown','unknown','normal']

# T06 — ratio and unsafe duration

def test_t06_speed(api, records, tmp_path):
    records['trip_duration_hours'] = [2,0,-3,np.nan]
    actual = api['load_data'](write(records, tmp_path))
    assert actual.average_speed_kmph.iloc[0] == 50
    assert actual.average_speed_kmph.iloc[1:].isna().all()

# T07 — preserve unrelated source columns and order

def test_t07_preserve_columns(cleaned, records):
    assert cleaned.trip_id.tolist() == records.trip_id.tolist()
    assert cleaned[TARGET].tolist() == records[TARGET].tolist()
    assert cleaned.export_note.tolist() == records.export_note.tolist()

# T08 — unfitted pipeline with feature groups

def test_t08_pipeline(api):
    est = LinearRegression()
    pipe = api['build_pipeline'](est)
    assert isinstance(pipe, Pipeline) and pipe.steps[-1][1] is est
    with pytest.raises(NotFittedError): check_is_fitted(pipe)
    trans = pipe.steps[0][1].transformers
    assert len(trans) == 2
    assert any(list(cols)==NUM for _,_,cols in trans)
    assert any(list(cols)==CAT for _,_,cols in trans)

# T09 — training-fitted median and scaling

def test_t09_imputation_scaling(api, cleaned):
    X = cleaned[FEATURES].copy()
    X['distance_km'] = [10.,20.,np.nan,100.]
    pipe = api['build_pipeline'](LinearRegression()).fit(X, cleaned[TARGET])
    num = next(t for _,t,cols in pipe.steps[0][1].transformers_ if list(cols)==NUM)
    assert num.steps[0][1].strategy == 'median'
    assert num.steps[0][1].statistics_[0] == 20
    assert num.steps[1][1].mean_[0] == 37.5
    transformed = num.transform(X[NUM])
    assert np.allclose(transformed.mean(axis=0),0,atol=1e-9)
    future = X.iloc[[0]].copy(); future['distance_km'] = 5000.
    pipe.predict(future)
    assert num.steps[0][1].statistics_[0] == 20

# T10 — unseen categories

def test_t10_unknown_category(api, cleaned):
    pipe = api['build_pipeline'](LinearRegression()).fit(cleaned[FEATURES],cleaned[TARGET])
    new = cleaned[FEATURES].iloc[[0]].copy()
    for c in CAT: new[c] = 'unseen'
    assert np.isfinite(pipe.predict(new)).all()

# T11 — exact supervised contract

def test_t11_prepare_types(supervised):
    Xtr,Xte,ytr,yte = supervised
    assert isinstance(Xtr,pd.DataFrame) and isinstance(Xte,pd.DataFrame)
    assert isinstance(ytr,pd.Series) and isinstance(yte,pd.Series)
    assert list(Xtr.columns) == FEATURES == list(Xte.columns)
    assert len(Xtr)==len(ytr) and len(Xte)==len(yte)

# T12 — valid targets and row alignment in both files

def test_t12_invalid_targets(api, records, tmp_path):
    train = records.copy(); train[TARGET] = ['14','bad','inf',None]
    test = records.copy(); test[TARGET] = [None,'12','-inf','6']
    Xtr,Xte,ytr,yte = api['prepare_datasets'](write(train,tmp_path,'tr.csv'),write(test,tmp_path,'te.csv'))
    assert ytr.tolist()==[14] and Xtr.distance_km.tolist()==[100]
    assert yte.tolist()==[12,6] and Xte.distance_km.tolist()==[60,25]
    assert Xtr.index.equals(ytr.index) and Xte.index.equals(yte.index)

# T13 — estimators and forest hyperparameters

def test_t13_model_configuration(fitted):
    assert set(fitted)=={'linear_regression','random_forest'}
    assert isinstance(fitted['linear_regression'].steps[-1][1],LinearRegression)
    rf = fitted['random_forest'].steps[-1][1]
    assert isinstance(rf,RandomForestRegressor)
    for k,v in dict(n_estimators=150,max_depth=10,min_samples_leaf=2,random_state=42,n_jobs=-1).items():
        assert rf.get_params()[k]==v

# T14 — separate fitted pipelines, inference on held-back rows

def test_t14_fitted_models(fitted,supervised,monkeypatch):
    _,Xte,_,_ = supervised
    a,b = fitted.values(); assert a is not b and a.steps[0][1] is not b.steps[0][1]
    monkeypatch.setattr(Pipeline,'fit',Mock(side_effect=AssertionError('Unexpected fit')))
    for model in fitted.values():
        check_is_fitted(model)
        pred = model.predict(Xte.iloc[:8]); assert len(pred)==8 and np.isfinite(pred).all()

# T15 — metric correctness

def test_t15_metrics(api):
    X = pd.DataFrame({'x':[0,1,2,3]}); y = pd.Series([2,4,8,12])
    a,b = Mock(),Mock(); a.predict.return_value=np.array([1,5,7,14]); b.predict.return_value=np.array([3,4,8,11])
    actual = api['evaluate_models']({'a':a,'b':b},X,y).set_index('model_name')
    for name,model in [('a',a),('b',b)]:
        pred=model.predict.return_value
        assert np.allclose(actual.loc[name,['mae','rmse','r2']].astype(float),[mean_absolute_error(y,pred),np.sqrt(mean_squared_error(y,pred)),r2_score(y,pred)])

# T16 — RMSE (not MAE) ranking and no fit

def test_t16_rank_rmse(api):
    X=pd.DataFrame({'x':[1,2,3,4]}); y=pd.Series([10,20,30,40])
    a,b=Mock(),Mock(); a.predict.return_value=np.array([10,20,30,48]); b.predict.return_value=np.array([13,23,33,43])
    result=api['evaluate_models']({'a':a,'b':b},X,y)
    assert list(result.columns)==['model_name','mae','rmse','r2']
    assert result.model_name.tolist()==['b','a'] and list(result.index)==[0,1]
    for model in [a,b]: model.fit.assert_not_called()

# T17 — first-ranked fitted object identity

def test_t17_selection(api):
    a,b=Mock(),Mock(); comparison=pd.DataFrame({'model_name':['b','a'],'rmse':[1.,5.]})
    name,model=api['select_best_model'](comparison,{'a':a,'b':b})
    assert name=='b' and model is b
    a.fit.assert_not_called(); b.fit.assert_not_called()

# T18 — prediction schema, clipping, rounding, order and exact features

def test_t18_prediction(api,cleaned):
    model=Mock(); model.predict.return_value=np.array([-1.4,2.36,7.04,0.])
    result=api['predict_fuel'](model,cleaned)
    assert list(result.columns)==['trip_id',OUT]
    assert result.trip_id.tolist()==cleaned.trip_id.tolist()
    assert result[OUT].tolist()==[0.,2.4,7.,0.]
    pd.testing.assert_frame_equal(model.predict.call_args.args[0],cleaned[FEATURES]); model.fit.assert_not_called()

# T19 — train workflow and saved output correctness

def test_t19_training_workflow(api,tmp_path,monkeypatch):
    for s in ['train','test']: shutil.copy(HERE/f'fleet_{s}.csv',tmp_path)
    monkeypatch.chdir(tmp_path)
    name,report=api['train']()
    saved=pd.read_csv('model_comparison.csv'); pd.testing.assert_frame_equal(saved,report,check_exact=False)
    assert list(saved.columns)==['model_name','mae','rmse','r2'] and saved.rmse.is_monotonic_increasing
    assert name==saved.iloc[0].model_name
    model=joblib.load('best_model.pkl'); check_is_fitted(model)
    assert isinstance(model,Pipeline)
    assert isinstance(model.steps[-1][1],LinearRegression if name=='linear_regression' else RandomForestRegressor)

# T20 — independent prediction with pre-existing fitted artifact

def test_t20_independent_prediction(api,tmp_path,monkeypatch,fitted):
    shutil.copy(HERE/'fleet_predict.csv',tmp_path)
    monkeypatch.chdir(tmp_path)
    model=fitted['linear_regression']; joblib.dump(model,'best_model.pkl')
    expected=api['load_data']('fleet_predict.csv'); expected_values=np.maximum(model.predict(expected[FEATURES]),0).round(1)
    monkeypatch.setitem(api,'train',Mock(side_effect=AssertionError('Unexpected training')))
    monkeypatch.setattr(Pipeline,'fit',Mock(side_effect=AssertionError('Unexpected fit')))
    actual=api['predict'](); saved=pd.read_csv('fleet_predictions.csv')
    pd.testing.assert_frame_equal(actual,saved,check_exact=False)
    assert list(saved.columns)==['trip_id',OUT] and saved.trip_id.tolist()==expected.trip_id.tolist()
    assert np.allclose(saved[OUT],expected_values)
