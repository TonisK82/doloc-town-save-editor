import copy,unittest
import core,farm_layout
class LayoutTests(unittest.TestCase):
 def fixture(self):
  names=['smelter','charcoal_kiln','garbage_collector'];items=[]
  for i,name in enumerate(names):items.append({'$type':'DolocTown.Synthesizer, Assembly-CSharp','equipmentName':name,'anchor':{'x':i*5,'y':7},'position':{'x':i*7.5+3,'y':10.5,'z':0},'id':i,'electronicComponent':None,'decalInfo':None,'inventory':{'items':[{'itemName':'wood','itemCount':i+1}],'slotLockStates':[False]},'taskCounter':{'value':17}})
  return {'farmData':{'farm':{'DM_equipment':{'equipments':{'list':items}},'DM_building':{'buildings':[{'room':{'keep':33}}]}},'agentData':{'money':123}},'cityData':{'quests':[3]}}
 def test_scope_and_preservation(self):
  d=self.fixture();before=copy.deepcopy(d);p=farm_layout.build_plan(d);self.assertTrue(p['moves']);r=farm_layout.apply(d,p)
  self.assertEqual(d,before);self.assertEqual(core.decode(core.encode(r)),r)
  self.assertEqual(r['farmData']['farm']['DM_building'],d['farmData']['farm']['DM_building']);self.assertEqual(r['cityData'],d['cityData'])
  for a,b in zip(farm_layout.equipment(d),farm_layout.equipment(r)):
   for k in a:
    if k not in ['anchor','position']:self.assertEqual(a[k],b[k])
  d['cityData']['quests'].append(9)
  with self.assertRaises(ValueError):farm_layout.apply(d,p)
 def test_power_fixed(self):
  d=self.fixture();farm_layout.equipment(d)[0]['electronicComponent']={'power':1};p=farm_layout.build_plan(d);self.assertIn(0,p['fixed']);self.assertFalse(any(m['index']==0 for m in p['moves']))
 def test_real_save_readonly(self):
  source=core.DEFAULT/'doloc-save-0.data'
  if not source.exists():self.skipTest('No local save')
  raw=source.read_bytes();d=core.decode(raw);p=farm_layout.build_plan(d);result=farm_layout.apply(d,p);self.assertEqual(core.decode(core.encode(result)),result);self.assertEqual(source.read_bytes(),raw)
if __name__=='__main__':unittest.main()
