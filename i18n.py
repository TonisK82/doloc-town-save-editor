EN = {
 'Doloc Town 存档修改器':'Doloc Town Save Editor',
 '打开存档':'Open save', '保存（自动备份）':'Save (with backup)', '另存为':'Save as',
 '请选择 .data 存档':'Select a .data save file',
 '编辑前请退出游戏。数量遵守游戏叠加上限；更换物品会重置该格的特殊属性。':'Quit the game before editing. Stack limits apply; replacing an item resets its special properties.',
 '背包 / 箱子 / 其他容器':'Backpack / Boxes / Other containers',
 '显示城镇 / 地牢容器':'Show town / dungeon containers',
 '格子':'Slot', '物品':'Item', '数量':'Quantity', '修改数量':'Set quantity', '清空格子':'Clear slot',
 '道具库：990 种（中文名称 / ID 搜索）':'990 items (search Chinese / English / ID)',
 '物品名称 / ID':'Item name / ID', '上限':'Limit', '添加到第一个空格':'Add to first empty slot',
 '替换选中格子':'Replace selected slot', '原始存档尚未修改':'Original save has not been modified',
 '操作失败':'Operation failed', '未保存':'Unsaved changes', '放弃当前未保存的修改？':'Discard unsaved changes?',
 'Doloc Town 存档':'Doloc Town saves', '所有文件':'All files', '已读取：':'Loaded: ',
 '（空）':'(Empty)', ' 锁':' Locked', ' 格':' slots', '请先选择一个格子':'Select a slot first',
 '这个格子尚未解锁':'This slot is locked', '有未保存的修改':'Unsaved changes', '选中格子为空':'Selected slot is empty',
 '清空此格物品？容器物品内部的内容也会被删除。':'Clear this slot? Contents inside this item will also be deleted.',
 '请打开存档并选择容器':'Open a save and select a container', '请在道具库选择物品':'Select an item in the catalog',
 '替换物品':'Replace item', '替换该格物品？原物品及其内部内容将被删除。':'Replace this slot? The old item and its contents will be deleted.',
 '容器没有已解锁的空格':'No unlocked empty slots available', '请完全退出 Doloc Town 后再保存':'Quit Doloc Town completely before saving',
 '保存成功':'Saved successfully', '；备份：':'; Backup: ', '：':': ',
 '金钱':'Money', '应用金钱':'Apply money', '请先打开存档':'Open a save first',
 '金钱须为 0–999999999 的整数':'Money must be an integer between 0 and 999999999',
 '金钱已修改；点击保存写入存档':'Money updated; click Save to write the save file',
 '数量须在 {limit} 之间':'Quantity must be between {limit}',
 '存档已被游戏或其他程序更新，请重新打开，避免覆盖进度':'The save was changed by another program. Reopen it to avoid overwriting progress.',
 '不是支持的 Doloc Town 存档':'Not a supported Doloc Town save', '回读校验失败':'Save round-trip verification failed',
 '未知道具编号':'Unknown item ID', '请输入整数':'Enter an integer',
}

def translate(text,language):
 if not isinstance(text,str):return text
 reverse={value:key for key,value in EN.items()}
 original=reverse.get(text,text)
 if language=='zh':
  for key in ['已读取：','保存成功','有未保存的修改','金钱已修改；点击保存写入存档']:
   if text.startswith(EN[key]):return key+text[len(EN[key]):].replace(EN['；备份：'],'；备份：')
  return original
 if original in EN:return EN[original]
 for key in ['已读取：','保存成功','有未保存的修改','金钱已修改；点击保存写入存档']:
  if original.startswith(key):
   return EN[key]+original[len(key):].replace('；备份：',EN['；备份：'])
 return original
