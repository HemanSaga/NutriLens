"""Reproducible grouped evaluation. No nutrient/score/brand features enter the model."""
import collections,copy,datetime,hashlib,json,pathlib,platform
import joblib,numpy as np,sklearn
from scipy.sparse import hstack,csr_matrix
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import StratifiedGroupKFold
from sklearn.neural_network import MLPClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.dummy import DummyClassifier
from sklearn.metrics import accuracy_score,f1_score,classification_report,confusion_matrix,log_loss
from sklearn.utils.class_weight import compute_sample_weight
from threadpoolctl import threadpool_limits
from prepare import ROOT,prepare
CLASSES=['intermediate','less_favourable','more_favourable']
def metrics(y,p):
 if not np.isfinite(p).all():raise ValueError('Non-finite evaluation probabilities')
 pred=np.array(CLASSES)[p.argmax(axis=1)]
 return {'n':len(y),'accuracy':accuracy_score(y,pred),'macro_f1':f1_score(y,pred,labels=CLASSES,average='macro',zero_division=0),'log_loss':log_loss(y,p,labels=CLASSES),'confusion_matrix':confusion_matrix(y,pred,labels=CLASSES).tolist(),'per_class':classification_report(y,pred,labels=CLASSES,output_dict=True,zero_division=0)}
def main():
 rows=prepare();labels=np.array([r['label'] for r in rows]);groups=np.array([r['group'] for r in rows]);strata=np.array([r['category']+':'+r['label'] for r in rows])
 counts=collections.Counter(labels)
 if len(rows)<150 or any(counts[c]<15 for c in CLASSES):raise SystemExit('Insufficient labelled data: need >=150 rows and >=15 per class for even a research pilot. No model produced.')
 # Predeclared folds; do not search split seeds for better results.
 folds=list(StratifiedGroupKFold(5,shuffle=True,random_state=42).split(rows,strata,groups))
 test=folds[0][1];val=folds[1][1];train=np.setdiff1d(np.arange(len(rows)),np.r_[test,val])
 for a,b in [(train,val),(train,test),(val,test)]:assert not set(groups[a])&set(groups[b])
 for ix in [train,val,test]:
  if set(labels[ix])!=set(CLASSES):raise SystemExit('A grouped split lacks a class. Collect more independent labelled product families; do not silently substitute random product splitting.')
 texts=[r['ingredients'] for r in rows];vectorizer=TfidfVectorizer(max_features=4000,ngram_range=(1,2),min_df=2,sublinear_tf=True)
 vectorizer.fit([texts[i] for i in train]);x=vectorizer.transform(texts)
 cats=csr_matrix(np.array([[r['category']=='snack',r['category']=='beverage'] for r in rows],dtype=float));x=hstack([x,cats]).tocsr()
 weights=compute_sample_weight('balanced',labels[train]);history=[]
 net=MLPClassifier(hidden_layer_sizes=(128,64,32),activation='relu',solver='adam',alpha=.01,batch_size=32,learning_rate_init=.001,random_state=42,max_iter=1)
 best=None;best_epoch=0;best_loss=float('inf');patience=0
 for epoch in range(1,151):
  net.partial_fit(x[train],labels[train],classes=CLASSES,sample_weight=weights)
  loss=log_loss(labels[val],net.predict_proba(x[val]),labels=CLASSES)
  history.append({'epoch':epoch,'training_loss':float(net.loss_),'validation_log_loss':float(loss)})
  if loss<best_loss-0.001:best_loss=loss;best=copy.deepcopy(net);best_epoch=epoch;patience=0
  else:patience+=1
  if epoch%10==0:print('epoch',epoch,'validation loss',round(loss,4),flush=True)
  if patience>=15:break
 models={'majority':DummyClassifier(strategy='prior'),'logistic_regression':LogisticRegression(max_iter=1000,class_weight='balanced',random_state=42),'random_forest':RandomForestClassifier(n_estimators=200,max_depth=20,class_weight='balanced',random_state=42,n_jobs=2)}
 for model in models.values():model.fit(x[train],labels[train])
 models['deep_mlp']=best
 results={name:{'validation':metrics(labels[val],m.predict_proba(x[val])),'test':metrics(labels[test],m.predict_proba(x[test]))} for name,m in models.items()}
 for category in ['snack','beverage']:
  ix=np.array([i for i in test if rows[i]['category']==category]);results['deep_mlp']['test_'+category]=metrics(labels[ix],best.predict_proba(x[ix])) if len(ix) else None
 baseline=max(results[n]['validation']['macro_f1'] for n in models if n!='deep_mlp')
 # These are engineering research gates, not clinical validation criteria.
 val_f1=results['deep_mlp']['validation']['macro_f1']
 gate={'enough_test_support':all(sum(rows[i]['category']==cat and labels[i]==c for i in test)>=30 for cat in ['snack','beverage'] for c in CLASSES),'validation_macro_f1_at_least_0_70':val_f1>=.70,'beats_best_baseline_on_validation':val_f1>baseline,'independent_expert_review':False}
 report={'created_at':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'research_only','target':'2023 source Nutri-Score bands, not personal health or food safety','classes':CLASSES,'dataset_sha256':hashlib.sha256((ROOT/'data/curated.json').read_bytes()).hexdigest(),'versions':{'python':platform.python_version(),'sklearn':sklearn.__version__,'numpy':np.__version__},'split_counts':{name:{'n':len(ix),'classes':dict(collections.Counter(labels[ix])),'groups':len(set(groups[ix]))} for name,ix in [('train',train),('validation',val),('test',test)]},'architecture':[x.shape[1],128,64,32,3],'selected_epoch':best_epoch,'results':results,'release_gates':gate,'consumer_release_approved':all(gate.values()),'history':history}
 out=ROOT/'artifacts';out.mkdir(exist_ok=True)
 joblib.dump({'model':best,'vectorizer':vectorizer,'classes':CLASSES,'status':'research_only','dataset_sha256':report['dataset_sha256']},out/'ingredient-mlp.joblib')
 (ROOT.parent/'research/evaluation.json').write_text(json.dumps(report,indent=2))
 (ROOT/'data/splits.json').write_text(json.dumps({name:[rows[i]['code'] for i in ix] for name,ix in [('train',train),('validation',val),('test',test)]},indent=2))
 print(json.dumps({name:{'val_macro_f1':r['validation']['macro_f1'],'test_macro_f1':r['test']['macro_f1']} for name,r in results.items()},indent=2));print('Consumer release approved:',report['consumer_release_approved'])
if __name__=='__main__':
 with threadpool_limits(limits=2):main()
