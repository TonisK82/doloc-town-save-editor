import copy,hashlib,pathlib,subprocess,sys,tkinter as tk
from tkinter import ttk,filedialog,messagebox
import core

class Editor(tk.Tk):
 def __init__(self):
  super().__init__();self.title('Doloc Town 存档修改器');self.geometry('1180x760');self.minsize(950,600)
  self.data=None;self.path=None;self.dirty=False;self.hash=None;self.container=None
  ttk.Style().configure('Treeview',rowheight=27)
  top=ttk.Frame(self,padding=10);top.pack(fill='x')
  for text,command in [('打开存档',self.open),('保存（自动备份）',self.save),('另存为',lambda:self.save(True))]:ttk.Button(top,text=text,command=command).pack(side='left',padx=4)
  self.filelabel=ttk.Label(top,text='请选择 .data 存档');self.filelabel.pack(side='left',padx=15)
  ttk.Label(self,text='编辑前请退出游戏。数量遵守游戏叠加上限；更换物品会重置该格的特殊属性。',padding=10).pack(fill='x')
  panes=ttk.Panedwindow(self,orient='horizontal');panes.pack(fill='both',expand=True,padx=10)
  left=ttk.Frame(panes);middle=ttk.Frame(panes);right=ttk.Frame(panes);panes.add(left,weight=2);panes.add(middle,weight=3);panes.add(right,weight=3)
  ttk.Label(left,text='背包 / 箱子 / 其他容器').pack(anchor='w')
  self.world=tk.BooleanVar(value=False);ttk.Checkbutton(left,text='显示城镇 / 地牢容器',variable=self.world,command=lambda:self.refresh_containers() if self.data else None).pack(anchor='w')
  self.containers=ttk.Treeview(left,show='tree',selectmode='browse');self.containers.pack(fill='both',expand=True);self.containers.bind('<<TreeviewSelect>>',self.select_container)
  self.pathlabel=ttk.Label(middle,text='',wraplength=400);self.pathlabel.pack(fill='x')
  self.slots=ttk.Treeview(middle,columns=('slot','name','count'),show='headings',selectmode='browse')
  for k,t,w in [('slot','格子',55),('name','物品',200),('count','数量',70)]:self.slots.heading(k,text=t);self.slots.column(k,width=w)
  self.slots.pack(fill='both',expand=True);self.slots.bind('<<TreeviewSelect>>',self.select_slot)
  actions=ttk.Frame(middle);actions.pack(fill='x',pady=10)
  self.count=tk.StringVar(value='1');ttk.Label(actions,text='数量').pack(side='left');ttk.Entry(actions,textvariable=self.count,width=8).pack(side='left')
  ttk.Button(actions,text='修改数量',command=self.change_count).pack(side='left',padx=4);ttk.Button(actions,text='清空格子',command=self.clear).pack(side='left')
  ttk.Label(right,text='道具库：990 种（中文名称 / ID 搜索）').pack(anchor='w')
  self.search=tk.StringVar();ttk.Entry(right,textvariable=self.search).pack(fill='x',pady=6);self.search.trace_add('write',lambda *a:self.filter())
  self.items=ttk.Treeview(right,columns=('name','limit'),show='headings',selectmode='browse');self.items.heading('name',text='物品名称 / ID');self.items.heading('limit',text='上限');self.items.column('name',width=240);self.items.column('limit',width=50);self.items.pack(fill='both',expand=True)
  self.items.bind('<<TreeviewSelect>>',self.select_item)
  self.itemlabel=ttk.Label(right,text='',wraplength=350);self.itemlabel.pack(fill='x')
  ttk.Button(right,text='添加到第一个空格',command=lambda:self.put(False)).pack(fill='x',pady=4)
  ttk.Button(right,text='替换选中格子',command=lambda:self.put(True)).pack(fill='x',pady=4)
  self.status=tk.StringVar(value='原始存档尚未修改');ttk.Label(self,textvariable=self.status,padding=10).pack(fill='x')
  self.filter();self.protocol('WM_DELETE_WINDOW',self.close)
 def error(self,e):messagebox.showerror('操作失败',str(e))
 def confirm_discard(self):return not self.dirty or messagebox.askyesno('未保存','放弃当前未保存的修改？')
 def open(self):
  if not self.confirm_discard():return
  p=filedialog.askopenfilename(initialdir=str(core.DEFAULT),filetypes=[('Doloc Town 存档','*.data *.prev*'),('所有文件','*.*')])
  if not p:return
  try:
   raw=pathlib.Path(p).read_bytes();d=core.decode(raw)
   self.data=d;self.path=pathlib.Path(p);self.hash=hashlib.sha256(raw).hexdigest();self.dirty=False;self.filelabel.config(text=self.path.name);self.refresh_containers();self.status.set('已读取：'+p)
  except Exception as e:self.error(e)
 def refresh_containers(self):
  self.invs=core.inventories(self.data,self.world.get());self.containers.delete(*self.containers.get_children())
  for i,(path,v,label) in enumerate(self.invs):self.containers.insert('','end',iid=str(i),text=f'{label} · {len(v["items"])} 格')
  if self.invs:self.containers.selection_set('0');self.select_container()
 def select_container(self,*a):
  sel=self.containers.selection()
  if not sel:return
  path,self.container,label=self.invs[int(sel[0])];self.pathlabel.config(text='/'.join(map(str,path)));self.refresh_slots()
 def refresh_slots(self):
  self.slots.delete(*self.slots.get_children())
  for i,item in enumerate(self.container['items']):
   locked=i<len(self.container['slotLockStates']) and self.container['slotLockStates'][i]
   self.slots.insert('','end',iid=str(i),values=(f'{i+1}'+(' 锁' if locked else ''),core.title(item['itemName']) if item else '（空）',item.get('itemCount',1) if item else ''))
 def select_slot(self,*a):
  sel=self.slots.selection()
  if sel:
   item=self.container['items'][int(sel[0])]
   if item:self.count.set(str(item.get('itemCount',1)))
 def select_item(self,*a):
  sel=self.items.selection()
  if sel:self.itemlabel.config(text=sel[0]+' · '+core.CATALOG[sel[0]]['type'])
 def filter(self):
  q=self.search.get().strip().lower();self.items.delete(*self.items.get_children())
  for id,x in core.CATALOG.items():
   if q in id.lower() or q in x['title'].lower():self.items.insert('','end',iid=id,values=(x['title']+' / '+id,x['limit']))
 def slot_index(self):
  if not self.slots.selection():raise ValueError('请先选择一个格子')
  i=int(self.slots.selection()[0])
  if self.container['slotLockStates'][i]:raise ValueError('这个格子尚未解锁')
  return i
 def changed(self):
  self.dirty=True;self.status.set('有未保存的修改');self.refresh_containers()
 def mutate_done(self):
  self.dirty=True;self.status.set('有未保存的修改');self.refresh_slots()
 def change_count(self):
  try:
   i=self.slot_index();item=self.container['items'][i]
   if not item:raise ValueError('选中格子为空')
   n=int(self.count.get());limit=core.CATALOG.get(item['itemName'],{}).get('limit',2147483647)
   if not 1<=n<=limit:raise ValueError(f'数量须在 1–{limit} 之间')
   item['itemCount']=n;self.mutate_done()
  except Exception as e:self.error(e)
 def clear(self):
  try:
   i=self.slot_index()
   if not messagebox.askyesno('清空格子','清空此格物品？容器物品内部的内容也会被删除。'):return
   self.container['items'][i]=None;self.changed()
  except Exception as e:self.error(e)
 def put(self,replace):
  try:
   if self.container is None:raise ValueError('请打开存档并选择容器')
   ids=self.items.selection()
   if not ids:raise ValueError('请在道具库选择物品')
   item=core.make_item(ids[0],int(self.count.get()))
   if replace:
    i=self.slot_index()
    if self.container['items'][i] and not messagebox.askyesno('替换物品','替换该格物品？原物品及其内部内容将被删除。'):return
   else:
    i=next((i for i,x in enumerate(self.container['items']) if x is None and not self.container['slotLockStates'][i]),None)
    if i is None:raise ValueError('容器没有已解锁的空格')
   self.container['items'][i]=item;self.mutate_done()
   # Rebuild references so newly added boxes can immediately be edited.
   self.invs=core.inventories(self.data,self.world.get())
   current=self.container
   self.containers.delete(*self.containers.get_children())
   for j,(p,v,label) in enumerate(self.invs):
    self.containers.insert('','end',iid=str(j),text=f'{label} · {len(v["items"])} 格')
    if v is current:self.containers.selection_set(str(j))
  except Exception as e:self.error(e)
 def save(self,as_new=False):
  if self.data is None:return
  try:
   running=subprocess.run(['tasklist','/FI','IMAGENAME eq DolocTown.exe','/NH'],capture_output=True,creationflags=0x08000000).stdout
   if b'doloctown.exe' in running.lower():raise ValueError('请完全退出 Doloc Town 后再保存')
   p=self.path
   if as_new:
    chosen=filedialog.asksaveasfilename(initialdir=str(self.path.parent),initialfile=self.path.stem+'-edited.data',defaultextension='.data',filetypes=[('Doloc Town 存档','*.data')])
    if not chosen:return
    p=pathlib.Path(chosen)
   backup,newhash=core.save(p,self.data,self.hash if p==self.path else None)
   self.path=p;self.hash=newhash;self.dirty=False;self.filelabel.config(text=p.name)
   self.status.set('保存成功'+('；备份：'+str(backup) if backup else '：'+str(p)))
  except Exception as e:self.error(e)
 def close(self):
  if self.confirm_discard():self.destroy()

if __name__=='__main__':
 if '--self-test' in sys.argv:
  report=pathlib.Path(sys.executable).with_name('self-test.txt')
  try:
   d=core.decode((core.DEFAULT/'doloc-save-0.data').read_bytes());assert core.decode(core.encode(d))==d
   app=Editor();app.withdraw();app.data=d;app.refresh_containers();app.update();assert len(app.items.get_children())==990;app.destroy()
   report.write_text('PASS: packaged AES, catalog, save reader, Tk GUI',encoding='utf-8')
  except Exception as e:report.write_text('FAIL: '+repr(e),encoding='utf-8');raise
 else:Editor().mainloop()
