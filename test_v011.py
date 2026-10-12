import copy,hashlib,pathlib,tempfile,unittest
import core
from editor import Editor

class Changes(unittest.TestCase):
 def setUp(self):
  self.data={'farmData':{'agentData':{'money':100},'inventory':{'backpack':{'items':[None]*50,'slotLockStates':[False]*50}}},'baseData':{'money':100},'cityData':{'store':{'money':33}},'unrelated':{'value':123}}
 def test_money_roundtrip_and_scope(self):
  original=copy.deepcopy(self.data)
  for value in [0,999999,999999999]:
   core.set_money(self.data,value)
   self.assertEqual(core.get_money(core.decode(core.encode(self.data))),value)
   self.assertEqual(self.data['baseData']['money'],value)
   self.assertEqual(self.data['cityData'],original['cityData'])
   self.assertEqual(self.data['unrelated'],original['unrelated'])
  for value in [-1,1000000000,True,1.5]:
   with self.assertRaises(ValueError):core.set_money(self.data,value)
 def test_backup(self):
  with tempfile.TemporaryDirectory(dir=pathlib.Path(__file__).parent) as td:
   p=pathlib.Path(td)/'test.data';old=core.encode(self.data);p.write_bytes(old)
   core.set_money(self.data,5000);backup,h=core.save(p,self.data,hashlib.sha256(old).hexdigest())
   self.assertEqual(backup.read_bytes(),old);self.assertEqual(core.decode(p.read_bytes()),self.data)
 def test_language_scrollbar_and_pending_edits(self):
  app=Editor();app.update()
  try:
   app.data=self.data;app.money.set('100');app.refresh_containers();app.update()
   self.assertEqual(len(app.items.get_children()),990)
   self.assertTrue(app.item_scroll.cget('command'))
   app.items.yview_moveto(1);app.update();self.assertGreater(app.items.yview()[0],0)
   app.money.set('2000');app.apply_money();self.assertTrue(app.dirty)
   app.container['items'][0]=core.make_item('wood',10)
   app.items.selection_set('wood');app.lang_choice.set('English');app.switch_language();app.update()
   self.assertEqual(core.get_money(app.data),2000);self.assertEqual(app.money.get(),'2000')
   self.assertEqual(app.container['items'][0]['itemCount'],10)
   self.assertEqual(app.items.selection(),('wood',))
   self.assertEqual(app.items.item('wood')['values'][0],core.title('wood','en')+' / wood')
   self.assertEqual(app.money_button.cget('text'),'Apply money')
   app.search.set(core.CATALOG['wood']['title_en']);app.update();self.assertIn('wood',app.items.get_children())
   app.lang_choice.set('中文');app.switch_language();app.update();self.assertEqual(app.money_button.cget('text'),'应用金钱')
   app.money.set('-1')
   with self.assertRaises(ValueError):app.commit_money()
   self.assertEqual(core.get_money(app.data),2000)
  finally:app.destroy()

if __name__=='__main__':unittest.main()
