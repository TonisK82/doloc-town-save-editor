import copy,pathlib,unittest
import core,compendium
from editor import Editor
from compendium_ui import CompendiumWindow

class CompendiumTests(unittest.TestCase):
 def setUp(self):
  self.data={'farmData':{'agentData':{'money':100},'inventory':{'backpack':{'items':[None],'slotLockStates':[False]}},'collectionManager':{'collections':{},'creatureCollections':{},'monsterCollections':{},'resourceCollections':{},'npcCollections':{},'unlockCollectionFunc':['archive','map']},'missionManager':{'quest':'unchanged'},'eventRecorderManager':{'events':[1,2]}},'cityData':{'liking':{'npc':5}}}
 def test_single_entry_scope_and_roundtrip(self):
  baseline=copy.deepcopy(self.data);cat='monster';id=next(iter(compendium.CATALOG[cat]['entries']));docs=compendium.CATALOG[cat]['entries'][id]['documents']
  compendium.set_record(self.data,cat,id,True,True,docs[:1])
  m=compendium.manager(self.data);self.assertEqual(list(m['monsterCollections']),[id]);self.assertEqual(m['monsterCollections'][id]['documents'],docs[:1])
  self.assertEqual(core.decode(core.encode(self.data)),self.data)
  self.assertEqual(m['unlockCollectionFunc'],baseline['farmData']['collectionManager']['unlockCollectionFunc'])
  self.assertEqual(self.data['cityData'],baseline['cityData']);self.assertEqual(self.data['farmData']['missionManager'],baseline['farmData']['missionManager']);self.assertEqual(self.data['farmData']['eventRecorderManager'],baseline['farmData']['eventRecorderManager']);self.assertEqual(self.data['farmData']['inventory'],baseline['farmData']['inventory'])
  compendium.set_record(self.data,cat,id,False);self.assertFalse(compendium.record(self.data,cat,id)['isUnlock']);self.assertEqual(compendium.record(self.data,cat,id)['documents'],[])
 def test_unknown_fields_preserved(self):
  id=next(iter(compendium.CATALOG['fish']['entries']));self.data['farmData']['collectionManager']['creatureCollections'][id]={'isUnlock':True,'isRead':True,'documents':['future-document'],'future':33}
  compendium.set_record(self.data,'fish',id,False)
  r=compendium.record(self.data,'fish',id);self.assertEqual(r['future'],33);self.assertEqual(r['documents'],['future-document'])
 def test_gui_individual_only(self):
  app=Editor();app.update()
  try:
   app.data=self.data;app.money.set('100');app.open_compendium();app.update();w=app.compendium_window
   self.assertIsInstance(w,CompendiumWindow);self.assertFalse(hasattr(w,'batch'));self.assertFalse(hasattr(w,'apply_percent'));self.assertFalse(hasattr(compendium,'apply_percent'))
   id=next(iter(compendium.CATALOG['item']['entries']));w.entries.selection_set(id);app.update();w.unlocked.set(True);w.apply_entry();app.update()
   self.assertTrue(compendium.record(self.data,'item',id)['isUnlock']);self.assertTrue(app.dirty)
   app.lang_choice.set('English');app.switch_language();app.update();self.assertEqual(app.compendium_window.language,'en');self.assertTrue(compendium.record(self.data,'item',id)['isUnlock'])
  finally:app.destroy()

if __name__=='__main__':unittest.main()
