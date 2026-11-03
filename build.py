"""Build a self-contained static site, with pinned dependencies and offline dictionaries."""
import csv,json,pathlib,shutil,urllib.request,string,os,hashlib,subprocess,zipfile
root=pathlib.Path(__file__).resolve().parent
out=root/'dist';out.mkdir(exist_ok=True)
for name in ['index.html','style.css','app.js','sw.js']:shutil.copy(root/name,out/name)
(out/'vendor').mkdir(exist_ok=True);(out/'dict').mkdir(exist_ok=True)
cache=root/'.cache';cache.mkdir(exist_ok=True)
def download(url,path):
 if not path.exists():
  temp=path.with_suffix(path.suffix+'.tmp')
  subprocess.run(['curl','-fsSL','--retry','3',url,'-o',str(temp)],check=True)
  temp.replace(path)
 return path
csvpath=pathlib.Path(os.environ['ECDICT_CSV']) if os.environ.get('ECDICT_CSV') else download('https://raw.githubusercontent.com/skywind3000/ECDICT/master/ecdict.csv',cache/'ecdict.csv')
if csvpath.stat().st_size<60000000:raise ValueError('Incomplete ECDICT download')
buckets={c:{} for c in string.ascii_lowercase};meta={'source':'ECDICT','count':0,'ielts':0,'tem8':0,'sha256':hashlib.sha256(csvpath.read_bytes()).hexdigest()};forms={}
with csvpath.open(encoding='utf-8',newline='') as f:
 for row in csv.DictReader(f):
  w=row['word'].strip().lower()
  if not w or w[0] not in buckets:continue
  exchange={p.split(':',1)[0]:p.split(':',1)[1] for p in (row['exchange'] or '').split('/') if ':' in p}
  entry=[row['phonetic'] or '',(row['translation'] or '').replace('\\n','\n'),(row['definition'] or '').replace('\\n','\n'),exchange.get('0','')]
  if w not in buckets[w[0]] or (not buckets[w[0]][w][1] and entry[1]):buckets[w[0]][w]=entry
  tags=(row['tag'] or '').split();meta['ielts']+=int('ielts' in tags);meta['tem8']+=int('tem8' in tags)
  for kind,variants in exchange.items():
   if kind in ['p','d','i','3','r','t','s']:
    for variant in variants.split(','):
     if variant and variant[0] in buckets and variant!=w:forms.setdefault(variant,w)
# Preserve dictionary-provided lemmas and fill forms where the source lacks one.
for form,base in forms.items():
 entry=buckets[form[0]].get(form)
 if entry is None:buckets[form[0]][form]=['','','',base]
 elif not entry[3] and not entry[1]:entry[3]=base
# Audit published reference lists; retain ECDICT definitions, not third-party dictionary content.
for alias,base in [('barometre','barometer'),('façade','facade')]:
 buckets[alias[0]][alias]=list(buckets[base[0]][base]);buckets[alias[0]][alias][3]=base
buckets['a']['a calculated crime']=['','n. 短语：有预谋的犯罪','','']
for key,filename in [('tem8','1521164650006_Level8luan_2.zip'),('ielts_reference','1521164666922_IELTS_3.zip')]:
 archive=download('https://raw.githubusercontent.com/kajweb/dict/master/book/'+filename,cache/(key+'.zip'))
 with zipfile.ZipFile(archive) as z:
  words=set(json.loads(line)['headWord'].strip().lower() for line in z.read(z.namelist()[0]).decode('utf-8').splitlines() if line.strip())
 missing=[w for w in words if w not in buckets.get(w[0],{})]
 meta[key]=len(words);meta[key+'_covered']=len(words)-len(missing)
 if missing:raise ValueError('Reference coverage failed: '+str(missing))
for c,data in buckets.items():
 meta['count']+=len(data);(out/'dict'/f'{c}.json').write_text(json.dumps(data,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
(out/'dict'/'meta.json').write_text(json.dumps(meta,ensure_ascii=False),encoding='utf-8')
for name in ['tesseract.min.js','worker.min.js']:
 shutil.copy(root/'node_modules'/'tesseract.js'/'dist'/name,out/'vendor'/name)
for path in (root/'node_modules'/'tesseract.js-core').glob('*wasm.js'):shutil.copy(path,out/'vendor'/path.name)
model=root/'public'/'vendor'/'eng.traineddata.gz'
if not model.exists():model=download('https://tessdata.projectnaptha.com/4.0.0_fast/eng.traineddata.gz',cache/'eng.traineddata.gz')
shutil.copy(model,out/'vendor'/'eng.traineddata.gz')
licenses=['WORDLEAF — Third-party notices\n\nECDICT https://github.com/skywind3000/ECDICT\n'+download('https://raw.githubusercontent.com/skywind3000/ECDICT/master/LICENSE',cache/'ecdict-license.txt').read_text()]
for name in ['tesseract.js','tesseract.js-core']:
 licenses.append('\n'+name+'\n'+next(p for p in [(root/'node_modules'/name/'LICENSE'),(root/'node_modules'/name/'LICENSE.md')] if p.exists()).read_text())
licenses.append('\nEnglish traineddata: https://github.com/tesseract-ocr/tessdata_fast — Apache-2.0\n')
(out/'LICENSES.txt').write_text('\n'.join(licenses))
(out/'.nojekyll').touch()
manifest=['./']+[p.relative_to(out).as_posix() for p in out.rglob('*') if p.is_file() and p.name not in ['offline-manifest.json','.nojekyll']]
(out/'offline-manifest.json').write_text(json.dumps(manifest))
print(json.dumps(meta),flush=True)
