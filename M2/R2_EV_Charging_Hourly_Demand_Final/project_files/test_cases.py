"""20 pytest checks, 3 marks each. Run: python -m pytest test_cases.py -v"""
from pathlib import Path
import shutil
from unittest.mock import Mock
import joblib
import nbformat
import numpy as np
import pandas as pd
import pytest
from sklearn.pipeline import Pipeline
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor
from sklearn.exceptions import NotFittedError
from sklearn.utils.validation import check_is_fitted
from sklearn.metrics import mean_absolute_error, mean_squared_error, mean_squared_log_error
HERE = Path(__file__).resolve().parent
RAW = ['temperature_c','feels_like_c','humidity_pct','wind_speed_kmph','hour']
NUM = RAW[:4]+['month','is_weekend','hour_sin','hour_cos']
CAT = ['season','weather_condition','holiday','working_day']
FEATURES = NUM+CAT
TARGET, OUT = 'session_count','predicted_sessions'

def definitions():
    nb=nbformat.read(HERE/'solution.ipynb',as_version=4)
    ns={'__name__':'assessment_definitions'}
    for cell in nb.cells:
        if cell.cell_type=='code' and 'definitions' in cell.metadata.get('tags',[]):
            exec(compile(cell.source,'solution.ipynb','exec'),ns)
    return ns

@pytest.fixture
def api(): return definitions()

@pytest.fixture
def records():
    return pd.DataFrame({'observation_id':['Z9','B2','C3','D4','E5','F6'],
        'observation_date':['2025-01-24','25/01/2025','2025-01-26','03/02/2025','2025-02-04','05/02/2025'],
        'hour':[0,6,12,18,23,9], 'temperature_c':[18,24,33,21,29,25],
        'feels_like_c':[17,25,34,22,30,26], 'humidity_pct':[60,70,50,75,65,66],
        'wind_speed_kmph':[2,3,5,6,9,11], 'season':['winter']*6,
        'weather_condition':['clear','rain','clear','cloudy','clear','rain'],
        'holiday':[0,0,1,0,0,0], 'working_day':[1,0,0,1,1,1], TARGET:[4,12,20,28,0,6],
        'member_sessions':[2,8,12,19,0,3], 'guest_sessions':[2,4,8,9,0,3], 'export_note':list('abcdef')})

def write(df,tmp_path,name='fixture.csv'):
    path=tmp_path/name; df.to_csv(path,index=False); return str(path)

@pytest.fixture
def cleaned(api,records,tmp_path): return api['load_data'](write(records,tmp_path))

@pytest.fixture(scope='module')
def supervised(): return definitions()['prepare_datasets'](str(HERE/'ev_train.csv'),str(HERE/'ev_test.csv'))

@pytest.fixture(scope='module')
def fitted(supervised):
    Xtr,_,ytr,_=supervised; return definitions()['train_models'](Xtr,ytr)

def test_t01_first_duplicate(api,records,tmp_path):
    result=api['load_data'](write(pd.concat([records,records.iloc[[0]].assign(temperature_c=99)]),tmp_path))
    assert result.observation_id.tolist()==records.observation_id.tolist() and result.temperature_c.iloc[0]==18

def test_t02_dates(api,records,tmp_path):
    records.loc[4,'observation_date']='bad-date'; records.loc[5,'observation_date']=None
    result=api['load_data'](write(records,tmp_path))
    assert result.observation_id.tolist()==['Z9','B2','C3','D4']
    assert result.observation_date.dt.strftime('%Y-%m-%d').tolist()==['2025-01-24','2025-01-25','2025-01-26','2025-02-03']

def test_t03_numeric(api,records,tmp_path):
    for c in RAW: records[c]=['12.5','bad','inf','-inf',None,'4']
    result=api['load_data'](write(records,tmp_path))
    for c in RAW:
        assert pd.api.types.is_numeric_dtype(result[c])
        assert result[c].iloc[0]==12.5 and result[c].iloc[5]==4
        assert result[c].iloc[1:5].isna().all()

def test_t04_categories(api,records,tmp_path):
    records=pd.concat([records,records.assign(observation_id=lambda d: d.observation_id+'X')],ignore_index=True)
    for c in CAT: records[c]=['  MiXeD ',' ',None,' NORMAL ','1.0','2','0.000','+2.00','-3.0','2.50','abc.0','1.01']
    result=api['load_data'](write(records,tmp_path))
    for c in CAT: assert result[c].tolist()==['mixed','unknown','unknown','normal','1','2','0','+2','-3','2.50','abc.0','1.01']

def test_t05_month_weekend(cleaned):
    assert cleaned.month.tolist()==[1,1,1,2,2,2]
    assert cleaned.is_weekend.tolist()==[0,1,1,0,0,0]

def test_t06_cyclical_hour(cleaned):
    angle=2*np.pi*np.array([0,6,12,18,23,9])/24
    np.testing.assert_allclose(cleaned.hour_sin,np.sin(angle),atol=1e-10)
    np.testing.assert_allclose(cleaned.hour_cos,np.cos(angle),atol=1e-10)

def test_t07_invalid_hour(api,records,tmp_path):
    records['hour']=[0,'bad',None,'inf','-inf',12]
    result=api['load_data'](write(records,tmp_path))
    assert result[['hour_sin','hour_cos']].iloc[1:5].isna().all().all()
    assert np.isfinite(result[['hour_sin','hour_cos']].iloc[[0,5]]).all().all()

def test_t08_preserve_fields(api,records,cleaned,tmp_path):
    for c in ['observation_id',TARGET,'member_sessions','guest_sessions','export_note']:
        assert cleaned[c].tolist()==records[c].tolist()
    queued=api['load_data'](write(records.drop(columns=[TARGET]),tmp_path,'queued.csv'))
    assert TARGET not in queued and queued.observation_id.tolist()==records.observation_id.tolist()

def test_t09_pipeline(api):
    est=DecisionTreeRegressor(); pipe=api['build_pipeline'](est)
    assert isinstance(pipe,Pipeline) and pipe.steps[-1][1] is est
    with pytest.raises(NotFittedError): check_is_fitted(pipe)
    trans=pipe.steps[0][1].transformers
    assert len(trans)==2 and any(list(c)==NUM for _,_,c in trans) and any(list(c)==CAT for _,_,c in trans)

def test_t10_preprocessing(api,cleaned):
    X=cleaned[FEATURES].copy(); X['temperature_c']=[10,20,np.nan,40,60,100]
    pipe=api['build_pipeline'](DecisionTreeRegressor()).fit(X,cleaned[TARGET])
    num=next(t for _,t,c in pipe.steps[0][1].transformers_ if list(c)==NUM)
    assert num.steps[0][1].strategy=='median' and num.steps[0][1].statistics_[0]==40
    assert num.steps[1][1].mean_[0]==45
    np.testing.assert_allclose(num.transform(X[NUM]).mean(axis=0),0,atol=1e-9)
    future=X.iloc[[0]].copy(); future['temperature_c']=5000
    for c in CAT: future[c]='unseen'
    assert np.isfinite(pipe.predict(future)).all() and num.steps[0][1].statistics_[0]==40

def test_t11_supervised_contract(supervised):
    Xtr,Xte,ytr,yte=supervised
    assert isinstance(Xtr,pd.DataFrame) and isinstance(Xte,pd.DataFrame)
    assert isinstance(ytr,pd.Series) and isinstance(yte,pd.Series)
    assert list(Xtr.columns)==FEATURES==list(Xte.columns) and len(Xtr)==len(ytr) and len(Xte)==len(yte)

def test_t12_target_filter(api,records,tmp_path):
    a=records.copy(); b=records.copy()
    a[TARGET]=['0','bad','inf',None,-1,6]; b[TARGET]=[None,'12','-inf',-2,0,'6']
    Xtr,Xte,ytr,yte=api['prepare_datasets'](write(a,tmp_path,'a.csv'),write(b,tmp_path,'b.csv'))
    assert ytr.tolist()==[0,6] and yte.tolist()==[12,0,6]
    assert pd.api.types.is_numeric_dtype(ytr) and pd.api.types.is_numeric_dtype(yte)

def test_t13_alignment_no_leakage(api,records,tmp_path):
    a=records.copy(); a.loc[1,TARGET]=-1; a.loc[3,'observation_date']='bad'
    Xtr,Xte,ytr,yte=api['prepare_datasets'](write(a,tmp_path,'a.csv'),write(records,tmp_path,'b.csv'))
    assert Xtr.temperature_c.tolist()==[18,33,29,25] and ytr.tolist()==[4,20,0,6]
    assert Xtr.index.equals(ytr.index) and Xte.index.equals(yte.index)
    assert Xte.temperature_c.tolist()==records.temperature_c.tolist() and list(Xtr.columns)==FEATURES==list(Xte.columns)

def test_t14_models(fitted):
    assert set(fitted)=={'decision_tree','random_forest'}
    a,b=fitted['decision_tree'],fitted['random_forest']
    assert a is not b and a.steps[0][1] is not b.steps[0][1]
    assert isinstance(a.steps[-1][1],DecisionTreeRegressor) and isinstance(b.steps[-1][1],RandomForestRegressor)
    for k,v in dict(max_depth=10,min_samples_leaf=4,random_state=42).items(): assert a.steps[-1][1].get_params()[k]==v
    for k,v in dict(n_estimators=120,max_depth=14,min_samples_leaf=2,random_state=42,n_jobs=-1).items(): assert b.steps[-1][1].get_params()[k]==v

def test_t15_fitted_predictions(fitted,supervised,monkeypatch):
    _,Xte,_,_=supervised
    monkeypatch.setattr(Pipeline,'fit',Mock(side_effect=AssertionError('Unexpected fit')))
    for model in fitted.values():
        check_is_fitted(model); new=Xte.iloc[:8].copy(); new['weather_condition']='unseen'
        pred=model.predict(new); assert len(pred)==8 and np.isfinite(pred).all()

def test_t16_metrics(api):
    X=pd.DataFrame({'x':[0,1,2]}); y=pd.Series([0,3,10]); a,b=Mock(),Mock()
    a.predict.return_value=np.array([-5,2,13]); b.predict.return_value=np.array([2,-1,9])
    result=api['evaluate_models']({'a':a,'b':b},X,y).set_index('model_name')
    for name,model in [('a',a),('b',b)]:
        pred=np.maximum(model.predict.return_value,0)
        np.testing.assert_allclose(result.loc[name,['mae','rmse','rmsle']].astype(float),[mean_absolute_error(y,pred),np.sqrt(mean_squared_error(y,pred)),np.sqrt(mean_squared_log_error(y,pred))])
        model.fit.assert_not_called()

def test_t17_rank_rmsle(api):
    X=pd.DataFrame({'x':[1,2]}); y=pd.Series([0,100]); a,b=Mock(),Mock()
    a.predict.return_value=np.array([2,100]); b.predict.return_value=np.array([0,110])
    result=api['evaluate_models']({'a':a,'b':b},X,y)
    assert list(result.columns)==['model_name','mae','rmse','rmsle'] and result.model_name.tolist()==['b','a'] and list(result.index)==[0,1]
    assert result.iloc[0].rmse>result.iloc[1].rmse
    for model in [a,b]: model.fit.assert_not_called()

def test_t18_selection(api):
    a,b=Mock(),Mock(); comparison=pd.DataFrame({'model_name':['b','a'],'rmsle':[.1,.8]})
    name,model=api['select_best_model'](comparison,{'a':a,'b':b})
    assert name=='b' and model is b
    a.fit.assert_not_called(); b.fit.assert_not_called()

def test_t19_prediction(api,cleaned):
    model=Mock(); model.predict.return_value=np.array([-1.4,2.36,7.8,0.,4.5,5.5])
    result=api['predict_demand'](model,cleaned)
    assert list(result.columns)==['observation_id',OUT] and result.observation_id.tolist()==cleaned.observation_id.tolist()
    assert result[OUT].tolist()==[0,2,8,0,4,6] and pd.api.types.is_integer_dtype(result[OUT])
    pd.testing.assert_frame_equal(model.predict.call_args.args[0],cleaned[FEATURES]); model.fit.assert_not_called()

def test_t20_workflows(tmp_path,monkeypatch):
    for s in ['train','test','predict']: shutil.copy(HERE/f'ev_{s}.csv',tmp_path)
    monkeypatch.chdir(tmp_path); api=definitions()
    assert not Path('best_model.pkl').exists() and not Path('model_comparison.csv').exists()
    name,report=api['train']()
    saved=pd.read_csv('model_comparison.csv'); pd.testing.assert_frame_equal(saved,report,check_exact=False)
    assert list(saved.columns)==['model_name','mae','rmse','rmsle'] and saved.rmsle.is_monotonic_increasing and name==saved.iloc[0].model_name
    model=joblib.load('best_model.pkl'); check_is_fitted(model); assert isinstance(model,Pipeline)
    assert isinstance(model.steps[-1][1],DecisionTreeRegressor if name=='decision_tree' else RandomForestRegressor)
    fresh=definitions(); expected=fresh['load_data']('ev_predict.csv')
    expected_values=np.rint(np.maximum(model.predict(expected[FEATURES]),0)).astype(int)
    Path('ev_train.csv').unlink(); Path('ev_test.csv').unlink()
    monkeypatch.setitem(fresh,'train',Mock(side_effect=AssertionError('Unexpected training')))
    monkeypatch.setattr(Pipeline,'fit',Mock(side_effect=AssertionError('Unexpected fit')))
    actual=fresh['predict'](); saved=pd.read_csv('ev_predictions.csv'); pd.testing.assert_frame_equal(actual,saved)
    assert list(saved.columns)==['observation_id',OUT] and saved.observation_id.tolist()==expected.observation_id.tolist()
    np.testing.assert_array_equal(saved[OUT],expected_values)
