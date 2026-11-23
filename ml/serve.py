"""Local-only research demo. No endpoint is exposed on the public network."""
import json
from http.server import BaseHTTPRequestHandler,HTTPServer
from predict import predict
from prepare import ROOT
class Handler(BaseHTTPRequestHandler):
 def send(self,status,body,kind='application/json'):
  self.send_response(status);self.send_header('Content-Type',kind+'; charset=utf-8');self.send_header('Cache-Control','no-store');self.send_header('X-Content-Type-Options','nosniff');self.end_headers();self.wfile.write(body.encode())
 def do_GET(self):
  if self.path=='/':return self.send(200,(ROOT/'demo.html').read_text(),'text/html')
  if self.path=='/api/evaluation':
   file=ROOT.parent/'research/evaluation.json'
   return self.send(200,file.read_text()) if file.exists() else self.send(503,json.dumps({'error':'No completed training run yet.'}))
  self.send(404,'{}')
 def do_POST(self):
  if self.path!='/api/predict':return self.send(404,'{}')
  try:
   n=int(self.headers.get('Content-Length','0'))
   if not 0<n<=32768:raise ValueError('Request is too large or empty.')
   data=json.loads(self.rfile.read(n));ingredients=data.get('ingredients');category=data.get('category')
   if not isinstance(ingredients,str) or not isinstance(category,str):raise ValueError('Enter ingredients and category.')
   self.send(200,json.dumps(predict(ingredients,category)))
  except (ValueError,TypeError) as e:self.send(400,json.dumps({'error':str(e)}))
 def log_message(self,*args):pass # Do not log users' ingredient entries.
if __name__=='__main__':
 print('NutriLens research demo: http://127.0.0.1:8765',flush=True);HTTPServer(('127.0.0.1',8765),Handler).serve_forever()
