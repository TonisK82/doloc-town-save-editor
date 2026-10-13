import tkinter as tk
from tkinter import ttk,messagebox
import compendium

NAMES={'item':('道具','Items'),'animal':('动物','Animals'),'fish':('鱼类','Fish'),'monster':('怪物','Monsters'),'resource':('资源','Resources'),'npc':('NPC','NPCs')}

class CompendiumWindow(tk.Toplevel):
 def __init__(self,editor):
  super().__init__(editor);self.editor=editor;self.data=editor.data;self.language=editor.language
  self.title(self.t('图鉴解锁进度','Compendium progress'));self.geometry('950x650');self.minsize(780,540)
  self.protocol('WM_DELETE_WINDOW',self.close);self.current=None
  toolbar=ttk.Frame(self,padding=10);toolbar.pack(fill='x')
  self.category=tk.StringVar(value=list(NAMES)[0]);self.category_name=tk.StringVar(value=self.name('item'))
  self.combo=ttk.Combobox(toolbar,textvariable=self.category_name,values=[self.name(k) for k in NAMES],state='readonly',width=15);self.combo.pack(side='left');self.combo.bind('<<ComboboxSelected>>',self.category_changed)
  self.query=tk.StringVar();ttk.Entry(toolbar,textvariable=self.query,width=25).pack(side='left',padx=8);self.query.trace_add('write',lambda *a:self.refresh())
  self.summary=tk.StringVar();ttk.Label(self,textvariable=self.summary,padding=10).pack(fill='x')
  panels=ttk.Panedwindow(self,orient='horizontal');panels.pack(fill='both',expand=True,padx=10)
  left=ttk.Frame(panels);right=ttk.Frame(panels);panels.add(left,weight=3);panels.add(right,weight=2)
  self.entries=ttk.Treeview(left,columns=('name','state','docs'),show='headings',selectmode='browse')
  for k,label,width in [('name',self.t('名称 / ID','Name / ID'),230),('state',self.t('状态','Status'),90),('docs',self.t('资料','Documents'),80)]:self.entries.heading(k,text=label);self.entries.column(k,width=width)
  scroll=ttk.Scrollbar(left,orient='vertical',command=self.entries.yview);self.entries.configure(yscrollcommand=scroll.set);scroll.pack(side='right',fill='y');self.entries.pack(fill='both',expand=True);self.entries.bind('<<TreeviewSelect>>',self.selected)
  self.unlocked=tk.BooleanVar();self.read=tk.BooleanVar()
  ttk.Checkbutton(right,text=self.t('条目已发现','Entry discovered'),variable=self.unlocked).pack(anchor='w',pady=5)
  ttk.Checkbutton(right,text=self.t('标记为已读','Mark as read'),variable=self.read).pack(anchor='w')
  ttk.Label(right,text=self.t('双击资料行切换解锁状态','Double-click a document to toggle unlock'),wraplength=300).pack(pady=10)
  self.docs=ttk.Treeview(right,columns=('id','state'),show='headings',selectmode='browse');self.docs.heading('id',text=self.t('资料 ID','Document ID'));self.docs.heading('state',text=self.t('解锁','Unlocked'));self.docs.column('id',width=180);self.docs.column('state',width=60);self.docs.pack(fill='both',expand=True);self.docs.bind('<Double-1>',self.toggle_document)
  ttk.Button(right,text=self.t('应用选中条目','Apply selected entry'),command=self.apply_entry).pack(fill='x',pady=5)
  bottom=ttk.Frame(self,padding=10);bottom.pack(fill='x')
  ttk.Button(bottom,text=self.t('完成','Done'),command=self.close).pack(side='right')
  ttk.Label(self,text=self.t('应用后需在主窗口保存。锁回条目后，游戏可能根据已有经历重新解锁。','Save in the main window after applying. The game may rediscover locked entries from existing progress.'),wraplength=900,padding=10).pack(fill='x')
  self.refresh()
 def t(self,zh,en):return en if self.language=='en' else zh
 def name(self,k):return NAMES[k][self.language=='en']
 def category_changed(self,*a):
  self.category.set(next(k for k in NAMES if self.name(k)==self.category_name.get()));self.current=None;self.docs.delete(*self.docs.get_children());self.unlocked.set(False);self.read.set(False);self.refresh()
 def refresh(self):
  cat=self.category.get();selected=self.entries.selection();self.entries.delete(*self.entries.get_children());q=self.query.get().strip().lower()
  for id,entry in compendium.CATALOG[cat]['entries'].items():
   if not any(q in x.lower() for x in [id,entry['title'],entry['title_en']]):continue
   r=compendium.record(self.data,cat,id);count=sum(d in r.get('documents',[]) for d in entry['documents']) if r.get('isUnlock') else 0
   self.entries.insert('','end',iid=id,values=((entry['title_en'] if self.language=='en' else entry['title'])+' / '+id,self.t('已发现','Discovered') if r.get('isUnlock') else self.t('未发现','Locked'),f'{count}/{len(entry["documents"])}'))
  u,n,d,total=compendium.category_stats(self.data,cat)
  self.summary.set(self.t('已发现','Discovered')+f': {u}/{n} ({u/n*100:.1f}%) · '+self.t('资料','Documents')+f': {d}/{total}'+(f' ({d/total*100:.1f}%)' if total else ''))
  if selected and self.entries.exists(selected[0]):self.entries.selection_set(selected[0])
  menu=compendium.CATALOG[cat]['menu'];self.menu_enabled=menu in compendium.manager(self.data).get('unlockCollectionFunc',[])
 def selected(self,*a):
  sel=self.entries.selection()
  if not sel:return
  self.current=sel[0];r=compendium.record(self.data,self.category.get(),self.current);self.unlocked.set(bool(r.get('isUnlock')));self.read.set(bool(r.get('isRead')))
  self.docs.delete(*self.docs.get_children())
  for d in compendium.CATALOG[self.category.get()]['entries'][self.current]['documents']:
   self.docs.insert('','end',iid=d,values=(d,'✓' if d in r.get('documents',[]) else '—'))
 def toggle_document(self,*a):
  selected=self.docs.selection()
  if selected:
   d=selected[0];old=self.docs.item(d,'values')[1];self.docs.set(d,'state','—' if old=='✓' else '✓')
   if old!='✓':self.unlocked.set(True)
 def changed(self):
  self.editor.dirty=True;self.editor.status.set(self.editor.tr('有未保存的修改'));self.refresh()
 def apply_entry(self):
  if not self.current:return
  docs=[d for d in self.docs.get_children() if self.docs.set(d,'state')=='✓']
  compendium.set_record(self.data,self.category.get(),self.current,self.unlocked.get(),self.read.get(),docs)
  self.changed()
 def close(self):
  self.editor.compendium_window=None;self.destroy()
