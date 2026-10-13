"""Conservative farm planner: permute compatible, existing occupied sites only."""
import copy,json,hashlib,collections
import core
CATALOG=json.loads((core.ROOT/'layout_catalog.json').read_text(encoding='utf-8'))
PATH=('farmData','farm','DM_equipment','equipments','list')
MOVABLE={'PlantBasin','Synthesizer','Workbench','EquipmentWorkbench','Case','StorageShelf','Barrel','GeneIncubator','GeneReplicator','ShowerRoom'}
def equipment(data):
 v=data
 for key in PATH:v=v[key]
 if not isinstance(v,list):raise ValueError('Unsupported farm equipment format')
 return v
def fingerprint(data):return hashlib.sha256(json.dumps(data,sort_keys=True,ensure_ascii=False).encode()).hexdigest()
def cells(e):
 w,h=CATALOG[e['equipmentName']]['size'];x,y=e['anchor']['x'],e['anchor']['y']
 return {(x+dx,y+dy) for dx in range(w) for dy in range(h)}
def kind(e):return e.get('$type','').split(',')[0].split('.')[-1]
def build_plan(data,mode='production'):
 if mode not in ['production','crops']:raise ValueError('Unknown planning mode')
 es=equipment(data);groups=collections.defaultdict(list);fixed={};known={};occupied=collections.defaultdict(list)
 for i,e in enumerate(es):
  proto=CATALOG.get(e.get('equipmentName'))
  if proto and all(type(e.get('anchor',{}).get(k)) is int for k in ['x','y']):
   known[i]=cells(e)
   for c in known[i]:occupied[c].append(i)
 # Radius is deliberately conservative: freeze crops near any local sprinkler/affector.
 sensitive=[e for e in es if any(s in kind(e) for s in ['Sprinkler','Affector','Lightning','Lamp','Feeder','Heater'])]
 for i,e in enumerate(es):
  p=CATALOG.get(e.get('equipmentName'));k=kind(e);reason=None
  if not p or i not in known:reason='unknown'
  elif k not in MOVABLE:reason='special'
  elif e.get('electronicComponent') is not None:reason='power'
  elif p['attachments'] or e.get('decalInfo') is not None or p['fit']!=0:reason='attachment'
  elif any(len(occupied[c])>1 for c in known[i]):reason='overlap'
  elif not isinstance(e.get('position'),dict) or not all(type(e['position'].get(k)) in [int,float] for k in ['x','y','z']):reason='unknown'
  elif k=='PlantBasin' and any(abs(e['anchor']['x']-s['anchor']['x'])<=12 and abs(e['anchor']['y']-s['anchor']['y'])<=6 for s in sensitive):reason='irrigation'
  if reason:fixed[i]=reason;continue
  # Same row, footprint, fit, and environment means identical occupied geometry and support.
  group=(tuple(p['size']),p['fit'],p['environment'],e['anchor']['y'])
  groups[group].append(i)
 moves=[]
 for indices in groups.values():
  sites=sorted(indices,key=lambda i:es[i]['anchor']['x'])
  def order(i):
   e=es[i];name=e['equipmentName'];crop=(e.get('crop') or {}).get('seedName','')
   section=0 if kind(e)=='PlantBasin' else 1 if kind(e) in ['Case','StorageShelf','Barrel'] else 2
   return ((crop,name,section) if mode=='crops' else (section,name,crop))+(e['anchor']['x'],i)
  objects=sorted(indices,key=order)
  for src,dst in zip(objects,sites):
   if src==dst:continue
   target=es[dst]['anchor'];old=es[src]['anchor'];dx=target['x']-old['x'];dy=target['y']-old['y']
   position=copy.deepcopy(es[src]['position']);position['x']+=dx*1.5;position['y']+=dy*1.5
   moves.append({'index':src,'id':es[src].get('id'),'name':es[src]['equipmentName'],'from':copy.deepcopy(old),'to':copy.deepcopy(target),'position':position})
 plan={'mode':mode,'fingerprint':fingerprint(data),'moves':moves,'fixed':fixed,'equipment_count':len(es),'eligible':sum(map(len,groups.values())),'inventory':resource_summary(data)}
 validate(data,plan)
 return plan
def resource_summary(data):
 counts=collections.Counter()
 for _,inv,_ in core.inventories(data):
  for item in inv['items']:
   if item:counts[item['itemName']]+=item.get('itemCount',1)
 return dict(counts)
def validate(data,plan):
 if fingerprint(data)!=plan['fingerprint']:raise ValueError('Farm or save changed; generate a new preview')
 before=equipment(data);after=copy.deepcopy(before);indices=set()
 for m in plan['moves']:
  i=m['index']
  if i in indices or i in plan['fixed']:raise ValueError('Invalid duplicate or fixed equipment move')
  indices.add(i);after[i]['anchor']=m['to'];after[i]['position']=m['position']
  proto=CATALOG[before[i]['equipmentName']]
  legal=[j for j,e in enumerate(before) if j not in plan['fixed'] and e['anchor']==m['to'] and CATALOG.get(e.get('equipmentName'))==proto]
  if not legal or m['from']!=before[i]['anchor'] or m['to']['y']!=m['from']['y']:raise ValueError('Target is not a compatible verified site')
  if after[i]['position']['x']-before[i]['position']['x']!=(m['to']['x']-m['from']['x'])*1.5:raise ValueError('Invalid position shift')
  if after[i]['position']['y']!=before[i]['position']['y'] or after[i]['position']['z']!=before[i]['position']['z']:raise ValueError('Invalid vertical position shift')
 # Multiset equality preserves all existing footprint occupancy, paths and support.
 b=collections.Counter(c for e in before if e.get('equipmentName') in CATALOG for c in cells(e))
 a=collections.Counter(c for e in after if e.get('equipmentName') in CATALOG for c in cells(e))
 if a!=b:raise ValueError('Layout changes occupied ground or introduces overlaps')
 for i,e in enumerate(before):
  original=copy.deepcopy(e);new=copy.deepcopy(after[i])
  for k in ['anchor','position']:original.pop(k,None);new.pop(k,None)
  if new!=original:raise ValueError('Equipment contents or state changed')
 return True
def apply(data,plan):
 validate(data,plan);result=copy.deepcopy(data);es=equipment(result)
 for m in plan['moves']:es[m['index']]['anchor']=copy.deepcopy(m['to']);es[m['index']]['position']=copy.deepcopy(m['position'])
 return result
