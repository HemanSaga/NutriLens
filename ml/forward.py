"""Reference forward pass that avoids platform BLAS matmul status warnings."""
import numpy as np

def probabilities(model,features):
 a=features.toarray() if hasattr(features,'toarray') else np.asarray(features)
 for i,(w,b) in enumerate(zip(model.coefs_,model.intercepts_)):
  a=np.einsum('ij,jk->ik',a,w,optimize=False)+b
  if i<len(model.coefs_)-1:a=np.maximum(a,0)
 if not np.isfinite(a).all():raise ValueError('Non-finite neural activations; prediction withheld.')
 exp=np.exp(a-a.max(axis=1,keepdims=True))
 return exp/exp.sum(axis=1,keepdims=True)
