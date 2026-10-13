import pathlib,tkinter as tk
from tkinter import ttk,filedialog,messagebox
import core,farm_layout

class FarmLayoutWindow(tk.Toplevel):
 def __init__(self,editor):
  super().__init__(editor);self.editor=editor;self.language=editor.language;self.plan=None
  self.transient(editor);self.grab_set()
  self.title(self.t('农场布局预览','Farm layout preview'));self.geometry('1100x760');self.minsize(850,600)
  bar=ttk.Frame(self,padding=10);bar.pack(fill='x')
  self.mode=tk.StringVar(value=self.t('生产设施归组','Group production facilities'))
  ttk.Combobox(bar,textvariable=self.mode,state='readonly',values=[self.t('生产设施归组','Group production facilities'),self.t('作物品种归组','Group crop varieties')],width=30).pack(side='left')
  ttk.Button(bar,text=self.t('生成方案','Generate plan'),command=self.generate).pack(side='left',padx=8)
  ttk.Button(bar,text=self.t('导出布局存档副本','Export layout save copy'),command=self.export).pack(side='right')
  self.summary=tk.StringVar();ttk.Label(self,textvariable=self.summary,padding=10).pack(fill='x')
  ttk.Label(self,text=self.t('第一版只整理已放置设施。灰色：固定；绿色：将移动。建筑、供电、灌溉附近设施及连接设备固定。','First version reorganizes placed equipment only. Gray: fixed; green: moving. Buildings, powered/connected equipment and equipment near irrigation remain fixed.'),wraplength=1040,padding=10).pack(fill='x')
  self.canvas=tk.Canvas(self,height=310,background='#f5f8f1');self.canvas.pack(fill='both',expand=True,padx=10);self.canvas.bind('<Configure>',lambda *a:self.draw())
  frame=ttk.Frame(self);frame.pack(fill='both',expand=True,padx=10)
  self.rows=ttk.Treeview(frame,columns=('name','from','to'),show='headings',height=7)
  for key,name in [('name',self.t('设施','Equipment')),('from',self.t('原位置','Original')),('to',self.t('新位置','New'))]:self.rows.heading(key,text=name)
  scroll=ttk.Scrollbar(frame,orient='vertical',command=self.rows.yview);scroll.pack(side='right',fill='y');self.rows.configure(yscrollcommand=scroll.set);self.rows.pack(fill='both',expand=True)
  self.notes=tk.StringVar();ttk.Label(self,textvariable=self.notes,wraplength=1040,padding=10).pack(fill='x')
  self.generate()
 def t(self,zh,en):return en if self.language=='en' else zh
 def generate(self):
  try:
   mode='crops' if self.mode.get()==self.t('作物品种归组','Group crop varieties') else 'production'
   self.plan=farm_layout.build_plan(self.editor.data,mode);p=self.plan
   self.summary.set(self.t('现有设施','Existing equipment')+f": {p['equipment_count']} · "+self.t('可整理','Eligible')+f": {p['eligible']} · "+self.t('移动','Moves')+f": {len(p['moves'])} · "+self.t('材料消耗：0','Materials used: 0'))
   self.rows.delete(*self.rows.get_children())
   for m in p['moves']:self.rows.insert('','end',values=(core.title(m['name'],self.language)+f" ID={m['id']}",f"({m['from']['x']},{m['from']['y']})",f"({m['to']['x']},{m['to']['y']})"))
   self.notes.set(self.t('复用现有合法占地，保留原道路与空隙；不消耗或生成道具，不移动建筑。背包与农场容器已读取，但第一版不自动放置未建造道具。图中是格子占地示意，并非游戏地图。','Reuses existing footprints and preserves gaps/paths. No items are consumed or created; buildings stay fixed. Inventory is scanned, but unplaced items are not built in this version. This is an occupancy schematic, not the game map.'))
   self.draw()
  except Exception as e:messagebox.showerror(self.t('操作失败','Operation failed'),str(e),parent=self)
 def draw(self):
  if not self.plan:return
  self.canvas.delete('all');es=farm_layout.equipment(self.editor.data);known=[e for e in es if e.get('equipmentName') in farm_layout.CATALOG]
  if not known:return
  bounds=[(e['anchor']['x'],e['anchor']['y'],*farm_layout.CATALOG[e['equipmentName']]['size']) for e in known]
  minx=min(x for x,y,w,h in bounds);maxx=max(x+w for x,y,w,h in bounds);miny=min(y for x,y,w,h in bounds);maxy=max(y+h for x,y,w,h in bounds)
  cw=max(self.canvas.winfo_width(),850);ch=max(self.canvas.winfo_height(),240);scale=min((cw/2-40)/max(maxx-minx,1),(ch-65)/max(maxy-miny,1));moves={m['index']:m for m in self.plan['moves']}
  for panel,label in [(0,self.t('当前布局','Current')),(1,self.t('方案预览','Proposed'))]:
   origin=panel*cw/2+20;self.canvas.create_text(origin,15,text=label,anchor='w',font=('Arial',12,'bold'))
   for i,e in enumerate(es):
    if e.get('equipmentName') not in farm_layout.CATALOG:continue
    a=moves[i]['to'] if panel and i in moves else e['anchor'];w,h=farm_layout.CATALOG[e['equipmentName']]['size'];x=origin+(a['x']-minx)*scale;y=40+(maxy-a['y']-h)*scale
    self.canvas.create_rectangle(x,y,x+w*scale,y+h*scale,fill='#52b788' if i in moves else '#adb5bd',outline='#ffffff')
    if w*scale>22 and h*scale>12:self.canvas.create_text(x+w*scale/2,y+h*scale/2,text=str(e.get('id','')),font=('Arial',7))
 def export(self):
  if not self.plan:return
  try:
   result=farm_layout.apply(self.editor.data,self.plan)
   if not self.plan['moves']:raise ValueError(self.t('没有可移动的设施；当前方案没有变化。','No movable equipment; the plan makes no changes.'))
   source=self.editor.path
   name=filedialog.asksaveasfilename(parent=self,initialdir=str(source.parent),initialfile=source.stem+'-farm-layout.data',defaultextension='.data',filetypes=[('Doloc Town','*.data')])
   if not name:return
   target=pathlib.Path(name)
   if target.resolve()==source.resolve():raise ValueError(self.t('请导出为新文件名，第一版不直接覆盖原存档。','Choose a new filename; this first version does not overwrite the original save.'))
   running=__import__('subprocess').run(['tasklist','/FI','IMAGENAME eq DolocTown.exe','/NH'],capture_output=True,creationflags=0x08000000).stdout
   if b'doloctown.exe' in running.lower():raise ValueError(self.t('请先完全退出游戏。','Quit the game completely first.'))
   core.save(target,result)
   messagebox.showinfo(self.t('导出成功','Exported'),self.t('已生成布局副本。请先备份原存档，再将副本复制成原存档文件名，进行游戏内测试。','Layout copy created. Back up the original save, then copy this file to the original save filename for in-game testing.')+'\n'+str(target),parent=self)
  except Exception as e:messagebox.showerror(self.t('操作失败','Operation failed'),str(e),parent=self)
