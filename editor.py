import copy, hashlib, pathlib, subprocess, sys, tkinter as tk
from tkinter import ttk, filedialog, messagebox
import core
from i18n import translate
import compendium
from compendium_ui import CompendiumWindow
from farm_layout_ui import FarmLayoutWindow

class Editor(tk.Tk):

    def __init__(self):
        super().__init__()
        self.language = 'zh'
        self.title(self.tr('Doloc Town 存档修改器')+' v0.1.3')
        self.geometry('1180x760')
        self.minsize(950, 600)
        self.data = None
        self.path = None
        self.dirty = False
        self.hash = None
        self.container = None
        self.compendium_window = None
        ttk.Style().configure('Treeview', rowheight=27)
        top = ttk.Frame(self, padding=10)
        top.pack(fill='x')
        for text, command in [(self.tr('打开存档'), self.open), (self.tr('保存（自动备份）'), self.save), (self.tr('另存为'), lambda: self.save(True))]:
            ttk.Button(top, text=text, command=command).pack(side='left', padx=4)
        self.filelabel = ttk.Label(top, text=self.tr('请选择 .data 存档'))
        self.filelabel.pack(side='left', padx=15)
        self.lang_choice = tk.StringVar(value='中文')
        self.lang_box = ttk.Combobox(top, textvariable=self.lang_choice, values=['中文', 'English'], state='readonly', width=10)
        self.lang_box.pack(side='right')
        self.lang_box.bind('<<ComboboxSelected>>', self.switch_language)
        moneybar = ttk.Frame(self, padding=10)
        moneybar.pack(fill='x')
        ttk.Label(moneybar, text=self.tr('金钱')).pack(side='left')
        self.money = tk.StringVar()
        self.money.trace_add('write',self.money_edited)
        self.money_entry = ttk.Entry(moneybar, textvariable=self.money, width=18, state='disabled')
        self.money_entry.pack(side='left', padx=8)
        self.money_button = ttk.Button(moneybar, text=self.tr('应用金钱'), command=self.apply_money, state='disabled')
        self.money_button.pack(side='left')
        ttk.Button(moneybar,text=self.tr('图鉴解锁进度'),command=self.open_compendium).pack(side='left',padx=12)
        ttk.Button(moneybar,text=self.tr('自动布局农场'),command=self.open_farm_layout).pack(side='left',padx=8)
        ttk.Label(self, text=self.tr('编辑前请退出游戏。数量遵守游戏叠加上限；更换物品会重置该格的特殊属性。'), padding=10).pack(fill='x')
        panes = ttk.Panedwindow(self, orient='horizontal')
        panes.pack(fill='both', expand=True, padx=10)
        left = ttk.Frame(panes)
        middle = ttk.Frame(panes)
        right = ttk.Frame(panes)
        panes.add(left, weight=2)
        panes.add(middle, weight=3)
        panes.add(right, weight=3)
        ttk.Label(left, text=self.tr('背包 / 箱子 / 其他容器')).pack(anchor='w')
        self.world = tk.BooleanVar(value=False)
        ttk.Checkbutton(left, text=self.tr('显示城镇 / 地牢容器'), variable=self.world, command=lambda: self.refresh_containers() if self.data else None).pack(anchor='w')
        self.containers = ttk.Treeview(left, show='tree', selectmode='browse')
        self.containers.pack(fill='both', expand=True)
        self.containers.bind('<<TreeviewSelect>>', self.select_container)
        self.pathlabel = ttk.Label(middle, text='', wraplength=400)
        self.pathlabel.pack(fill='x')
        self.slots = ttk.Treeview(middle, columns=('slot', 'name', 'count'), show='headings', selectmode='browse')
        for k, t, w in [('slot', self.tr('格子'), 55), ('name', self.tr('物品'), 200), ('count', self.tr('数量'), 70)]:
            self.slots.heading(k, text=t)
            self.slots.column(k, width=w)
        self.slots.pack(fill='both', expand=True)
        self.slots.bind('<<TreeviewSelect>>', self.select_slot)
        actions = ttk.Frame(middle)
        actions.pack(fill='x', pady=10)
        self.count = tk.StringVar(value='1')
        ttk.Label(actions, text=self.tr('数量')).pack(side='left')
        ttk.Entry(actions, textvariable=self.count, width=8).pack(side='left')
        ttk.Button(actions, text=self.tr('修改数量'), command=self.change_count).pack(side='left', padx=4)
        ttk.Button(actions, text=self.tr('清空格子'), command=self.clear).pack(side='left')
        ttk.Label(right, text=self.tr('道具库：990 种（中文名称 / ID 搜索）')).pack(anchor='w')
        self.search = tk.StringVar()
        ttk.Entry(right, textvariable=self.search).pack(fill='x', pady=6)
        self.search.trace_add('write', lambda *a: self.filter())
        itemframe = ttk.Frame(right)
        itemframe.pack(fill='both', expand=True)
        self.items = ttk.Treeview(itemframe, columns=('name', 'limit'), show='headings', selectmode='browse')
        self.items.heading('name', text=self.tr('物品名称 / ID'))
        self.items.heading('limit', text=self.tr('上限'))
        self.items.column('name', width=240)
        self.items.column('limit', width=50)
        self.items.pack(side='left', fill='both', expand=True)
        self.item_scroll = ttk.Scrollbar(itemframe, orient='vertical', command=self.items.yview)
        self.item_scroll.pack(side='right', fill='y')
        self.items.configure(yscrollcommand=self.item_scroll.set)
        self.items.bind('<<TreeviewSelect>>', self.select_item)
        self.itemlabel = ttk.Label(right, text='', wraplength=350)
        self.itemlabel.pack(fill='x')
        ttk.Button(right, text=self.tr('添加到第一个空格'), command=lambda: self.put(False)).pack(fill='x', pady=4)
        ttk.Button(right, text=self.tr('替换选中格子'), command=lambda: self.put(True)).pack(fill='x', pady=4)
        self.status = tk.StringVar(value=self.tr('原始存档尚未修改'))
        ttk.Label(self, textvariable=self.status, padding=10).pack(fill='x')
        self.filter()
        self.protocol('WM_DELETE_WINDOW', self.close)

    def error(self, e):
        messagebox.showerror(self.tr('操作失败'), self.tr(str(e)))

    def confirm_discard(self):
        return not self.dirty or messagebox.askyesno(self.tr('未保存'), self.tr('放弃当前未保存的修改？'))

    def open(self):
        if self.compendium_window is not None:self.compendium_window.close()
        if not self.confirm_discard():
            return
        p = filedialog.askopenfilename(initialdir=str(core.DEFAULT), filetypes=[(self.tr('Doloc Town 存档'), '*.data *.prev*'), (self.tr('所有文件'), '*.*')])
        if not p:
            return
        try:
            raw = pathlib.Path(p).read_bytes()
            d = core.decode(raw)
            balance = core.get_money(d)
            self.data = d
            self.path = pathlib.Path(p)
            self.hash = hashlib.sha256(raw).hexdigest()
            self.dirty = False
            self.filelabel.config(text=self.path.name)
            self.refresh_containers()
            self.money.set(str(balance))
            self.money_entry.config(state='normal')
            self.money_button.config(state='normal')
            self.status.set(self.tr('已读取：') + p)
        except Exception as e:
            self.error(e)

    def refresh_containers(self):
        self.invs = core.inventories(self.data, self.world.get(), self.language)
        self.containers.delete(*self.containers.get_children())
        for i, (path, v, label) in enumerate(self.invs):
            self.containers.insert('', 'end', iid=str(i), text=f"{label} · {len(v['items'])}" + self.tr(' 格'))
        if self.invs:
            self.containers.selection_set('0')
            self.select_container()

    def select_container(self, *a):
        sel = self.containers.selection()
        if not sel:
            return
        path, self.container, label = self.invs[int(sel[0])]
        self.pathlabel.config(text='/'.join(map(str, path)))
        self.refresh_slots()

    def refresh_slots(self):
        self.slots.delete(*self.slots.get_children())
        for i, item in enumerate(self.container['items']):
            locked = i < len(self.container['slotLockStates']) and self.container['slotLockStates'][i]
            self.slots.insert('', 'end', iid=str(i), values=(f'{i + 1}' + (self.tr(' 锁') if locked else ''), core.title(item['itemName'], self.language) if item else self.tr('（空）'), item.get('itemCount', 1) if item else ''))

    def select_slot(self, *a):
        sel = self.slots.selection()
        if sel:
            item = self.container['items'][int(sel[0])]
            if item:
                self.count.set(str(item.get('itemCount', 1)))

    def select_item(self, *a):
        sel = self.items.selection()
        if sel:
            self.itemlabel.config(text=sel[0] + ' · ' + core.CATALOG[sel[0]]['type'])

    def filter(self):
        q = self.search.get().strip().lower()
        self.items.delete(*self.items.get_children())
        for id, x in core.CATALOG.items():
            if any((q in value.lower() for value in [id, x['title'], x.get('title_en', id)])):
                self.items.insert('', 'end', iid=id, values=(core.title(id, self.language) + ' / ' + id, x['limit']))

    def slot_index(self):
        if not self.slots.selection():
            raise ValueError(self.tr('请先选择一个格子'))
        i = int(self.slots.selection()[0])
        if self.container['slotLockStates'][i]:
            raise ValueError(self.tr('这个格子尚未解锁'))
        return i

    def changed(self):
        self.dirty = True
        self.status.set(self.tr('有未保存的修改'))
        self.refresh_containers()

    def mutate_done(self):
        self.dirty = True
        self.status.set(self.tr('有未保存的修改'))
        self.refresh_slots()

    def change_count(self):
        try:
            i = self.slot_index()
            item = self.container['items'][i]
            if not item:
                raise ValueError(self.tr('选中格子为空'))
            n = int(self.count.get())
            limit = core.CATALOG.get(item['itemName'], {}).get('limit', 999999999)
            if not 1 <= n <= limit:
                raise ValueError(self.tr('数量须在 {limit} 之间').format(limit=f'1–{limit}'))
            item['itemCount'] = n
            self.mutate_done()
        except Exception as e:
            self.error(e)

    def clear(self):
        try:
            i = self.slot_index()
            if not messagebox.askyesno(self.tr('清空格子'), self.tr('清空此格物品？容器物品内部的内容也会被删除。')):
                return
            self.container['items'][i] = None
            self.changed()
        except Exception as e:
            self.error(e)

    def put(self, replace):
        try:
            if self.container is None:
                raise ValueError(self.tr('请打开存档并选择容器'))
            ids = self.items.selection()
            if not ids:
                raise ValueError(self.tr('请在道具库选择物品'))
            try:
                n=int(self.count.get())
            except ValueError:raise ValueError(self.tr('请输入整数'))
            limit=core.CATALOG[ids[0]]['limit']
            if not 1<=n<=limit:raise ValueError(self.tr('数量须在 {limit} 之间').format(limit=f'1–{limit}'))
            item = core.make_item(ids[0],n)
            if replace:
                i = self.slot_index()
                if self.container['items'][i] and (not messagebox.askyesno(self.tr('替换物品'), self.tr('替换该格物品？原物品及其内部内容将被删除。'))):
                    return
            else:
                i = next((i for i, x in enumerate(self.container['items']) if x is None and (not self.container['slotLockStates'][i])), None)
                if i is None:
                    raise ValueError(self.tr('容器没有已解锁的空格'))
            self.container['items'][i] = item
            self.mutate_done()
            self.invs = core.inventories(self.data, self.world.get(), self.language)
            current = self.container
            self.containers.delete(*self.containers.get_children())
            for j, (p, v, label) in enumerate(self.invs):
                self.containers.insert('', 'end', iid=str(j), text=f"{label} · {len(v['items'])}" + self.tr(' 格'))
                if v is current:
                    self.containers.selection_set(str(j))
        except Exception as e:
            self.error(e)

    def save(self, as_new=False):
        if self.data is None:
            return
        try:
            self.commit_money()
            running = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq DolocTown.exe', '/NH'], capture_output=True, creationflags=134217728).stdout
            if b'doloctown.exe' in running.lower():
                raise ValueError(self.tr('请完全退出 Doloc Town 后再保存'))
            p = self.path
            if as_new:
                chosen = filedialog.asksaveasfilename(initialdir=str(self.path.parent), initialfile=self.path.stem + '-edited.data', defaultextension='.data', filetypes=[(self.tr('Doloc Town 存档'), '*.data')])
                if not chosen:
                    return
                p = pathlib.Path(chosen)
            backup, newhash = core.save(p, self.data, self.hash if p == self.path else None)
            self.path = p
            self.hash = newhash
            self.dirty = False
            self.filelabel.config(text=p.name)
            self.status.set(self.tr('保存成功') + (self.tr('；备份：') + str(backup) if backup else '：' + str(p)))
        except Exception as e:
            self.error(e)

    def close(self):
        if self.confirm_discard():
            self.destroy()

    def money_edited(self,*args):
        if self.data is not None and self.money.get()!=str(core.get_money(self.data)):
            self.dirty=True
            self.status.set(self.tr('有未保存的修改'))

    def tr(self,text):
        return translate(text,self.language)

    def open_compendium(self):
        if self.data is None:
            self.error(self.tr('请先打开存档'));return
        try:
            compendium.manager(self.data)
            if self.compendium_window is not None:self.compendium_window.lift();return
            self.compendium_window=CompendiumWindow(self)
        except Exception as e:self.error(e)

    def open_farm_layout(self):
        if self.data is None:
            self.error(self.tr('请先打开存档'));return
        FarmLayoutWindow(self)

    def commit_money(self):
        if self.data is None:
            raise ValueError(self.tr('请先打开存档'))
        try:
            value=int(self.money.get())
            if not 0<=value<=999999999:raise ValueError()
        except ValueError:
            raise ValueError(self.tr('金钱须为 0–999999999 的整数'))
        if value!=core.get_money(self.data):
            core.set_money(self.data,value)
            self.dirty=True

    def apply_money(self):
        try:
            self.commit_money()
            self.status.set(self.tr('金钱已修改；点击保存写入存档'))
        except Exception as e:self.error(e)

    def switch_language(self,*args):
        reopen=self.compendium_window is not None
        if reopen:self.compendium_window.close()
        selected=self.items.selection()
        currentpath=self.invs[int(self.containers.selection()[0])][0] if self.data and self.containers.selection() else None
        slot=self.slots.selection()
        self.language='en' if self.lang_choice.get()=='English' else 'zh'
        def update(widget):
            if 'text' in widget.keys():
                widget.configure(text=self.tr(widget.cget('text')))
            for child in widget.winfo_children():update(child)
        update(self)
        self.title(self.tr('Doloc Town 存档修改器')+' v0.1.3')
        for key,name in [('slot','格子'),('name','物品'),('count','数量')]:self.slots.heading(key,text=self.tr(name))
        self.items.heading('name',text=self.tr('物品名称 / ID'));self.items.heading('limit',text=self.tr('上限'))
        self.status.set(self.tr(self.status.get()))
        self.filter()
        if selected and self.items.exists(selected[0]):self.items.selection_set(selected[0]);self.select_item()
        if self.data:
            self.refresh_containers()
            for i,(path,inv,label) in enumerate(self.invs):
                if path==currentpath:self.containers.selection_set(str(i));self.select_container();break
            if slot and self.slots.exists(slot[0]):self.slots.selection_set(slot[0])
        if reopen:self.open_compendium()

if __name__ == '__main__':
    if '--self-test' in sys.argv:
        report = pathlib.Path(sys.executable).with_name('self-test.txt')
        try:
            d = core.decode((core.DEFAULT / 'doloc-save-0.data').read_bytes())
            assert core.decode(core.encode(d)) == d
            app = Editor()
            app.withdraw()
            app.data = d
            app.refresh_containers()
            app.update()
            assert len(app.items.get_children()) == 990
            app.money.set(str(core.get_money(d)))
            app.lang_choice.set('English')
            app.switch_language()
            assert app.money_button.cget('text') == 'Apply money'
            app.open_compendium()
            assert app.compendium_window is not None
            app.compendium_window.close()
            import farm_layout
            plan=farm_layout.build_plan(d)
            assert core.decode(core.encode(farm_layout.apply(d,plan))) == farm_layout.apply(d,plan)
            core.set_money(d,123456)
            assert core.get_money(core.decode(core.encode(d))) == 123456
            app.destroy()
            report.write_text('PASS v0.1.3: packaged AES, 990 items, bilingual GUI, scrollbar, money round-trip, compendium GUI', encoding='utf-8')
        except Exception as e:
            report.write_text('FAIL: ' + repr(e), encoding='utf-8')
            raise
    else:
        Editor().mainloop()
