import base64,copy,hashlib,json,os,pathlib,sys,tempfile,datetime
ROOT=pathlib.Path(getattr(sys,'_MEIPASS',pathlib.Path(__file__).parent))
sys.path.insert(0,str(ROOT/'devlibs'))
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad,unpad
CATALOG=json.loads((ROOT/'catalog.json').read_text(encoding='utf-8'))
PREFIX='DOLOC-TOWN:'
KEY=b'lets-mix-lives-and-change-drinks';IV=b'welcome-to-doloc'
DEFAULT=pathlib.Path.home()/'AppData/LocalLow/RedSawGames/DolocTown/SAVE'
def decode(raw):
 text=raw.decode('utf-8-sig')
 if text.startswith(PREFIX):text=unpad(AES.new(KEY,AES.MODE_CBC,IV).decrypt(base64.b64decode(text[len(PREFIX):],validate=True)),16).decode('utf-8-sig')
 data=json.loads(text)
 if not isinstance(data,dict) or 'farmData' not in data:raise ValueError('不是支持的 Doloc Town 存档')
 return data
def encode(data):
 text=json.dumps(data,ensure_ascii=False,separators=(',',':'),allow_nan=False).encode('utf-8')
 return (PREFIX+base64.b64encode(AES.new(KEY,AES.MODE_CBC,IV).encrypt(pad(text,16))).decode()).encode('utf-8')
def title(id,language='zh'):
 entry=CATALOG.get(id,{})
 return entry.get('title_en',id) if language=='en' else entry.get('title',id)
def get_money(data):
 value=data['farmData']['agentData']['money']
 if type(value) is not int:raise ValueError('Invalid player money field')
 return value
def set_money(data,value):
 if type(value) is not int or not 0<=value<=999999999:
  raise ValueError('Money must be an integer between 0 and 999999999')
 get_money(data)
 data['farmData']['agentData']['money']=value
 if isinstance(data.get('baseData'),dict) and 'money' in data['baseData']:
  data['baseData']['money']=value
def inventories(data,include_world=False,language='zh'):
 result=[]
 def walk(v,path=(),label=''):
  if isinstance(v,dict):
   if isinstance(v.get('items'),list) and isinstance(v.get('slotLockStates'),list):
    if include_world or (path and path[0]=='farmData'):
     result.append((path,v,('Backpack' if language=='en' else '背包') if path==('farmData','inventory','backpack') else label or '/'.join(map(str,path))))
   own=label
   if 'itemName' in v:own=title(v['itemName'],language)
   elif '$type' in v:
    own=v['$type'].split(',')[0].split('.')[-1]
    pos=v.get('anchor',v.get('position'))
    if pos:own+=f" ({pos.get('x')}, {pos.get('y')})"
    if 'id' in v:own+=f" ID={v['id']}"
   for k,x in v.items():walk(x,path+(k,),own+' / '+k if own else '')
  elif isinstance(v,list):
   for i,x in enumerate(v):walk(x,path+(i,),label+f' [{i+1}]')
 walk(data)
 return sorted(result,key=lambda x:x[0]!=('farmData','inventory','backpack'))
def make_item(id,count):
 if id not in CATALOG:raise ValueError('未知道具编号')
 if not 1<=count<=CATALOG[id]['limit']:raise ValueError(f"数量须在 1–{CATALOG[id]['limit']} 之间；可分多个格子添加")
 item=copy.deepcopy(CATALOG[id]['template']);item['itemCount']=count;return item
def save(path,data,expected=None):
 path=pathlib.Path(path);raw=encode(data)
 if decode(raw)!=data:raise ValueError('回读校验失败')
 backup=None
 if path.exists():
  old=path.read_bytes()
  if expected and hashlib.sha256(old).hexdigest()!=expected:raise ValueError('存档已被游戏或其他程序更新，请重新打开，避免覆盖进度')
  backup=path.with_name(path.name+'.editor-backup-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S-%f'))
  with backup.open('xb') as f:f.write(old)
 fd,tmp=tempfile.mkstemp(prefix=path.name+'.',suffix='.tmp',dir=path.parent)
 try:
  with os.fdopen(fd,'wb') as f:f.write(raw);f.flush();os.fsync(f.fileno())
  os.replace(tmp,path)
 finally:
  if os.path.exists(tmp):os.unlink(tmp)
 return backup,hashlib.sha256(raw).hexdigest()
