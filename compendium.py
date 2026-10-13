"""Edit only collection records, without changing quests, inventory or event counters."""
import copy,json
import core
CATALOG=json.loads((core.ROOT/'compendium.json').read_text(encoding='utf-8'))

def manager(data):
 value=data['farmData'].get('collectionManager')
 if not isinstance(value,dict):raise ValueError('不支持此存档的图鉴格式')
 for field in {c['field'] for c in CATALOG.values()}:
  if field in value and not isinstance(value[field],dict):raise ValueError('不支持此存档的图鉴格式')
 if 'unlockCollectionFunc' in value and not isinstance(value['unlockCollectionFunc'],list):raise ValueError('不支持此存档的图鉴格式')
 return value

def record(data,category,id):
 config=CATALOG[category]
 if id not in config['entries']:raise ValueError('Unknown compendium entry')
 return manager(data).get(config['field'],{}).get(id,{'isUnlock':False,'isRead':False,'documents':[]})

def set_record(data,category,id,unlocked,read=False,documents=()):
 config=CATALOG[category];entry=config['entries'][id]
 if any(d not in entry['documents'] for d in documents):raise ValueError('Unknown document ID')
 m=manager(data);records=m.setdefault(config['field'],{})
 original=copy.deepcopy(records.get(id,{}))
 # Preserve unfamiliar fields and document IDs from newer saves.
 extras=[d for d in original.get('documents',[]) if d not in entry['documents']]
 original.update(isUnlock=bool(unlocked),isRead=bool(read) if unlocked else False,documents=extras+list(dict.fromkeys(documents)) if unlocked else extras)
 records[id]=original

def category_stats(data,category):
 entries=CATALOG[category]['entries'];records=[record(data,category,id) for id in entries]
 unlocked=sum(bool(r.get('isUnlock')) for r in records)
 total_docs=sum(len(e['documents']) for e in entries.values())
 docs=sum(sum(d in r.get('documents',[]) for d in entries[id]['documents']) for id,r in zip(entries,records) if r.get('isUnlock'))
 return unlocked,len(entries),docs,total_docs


