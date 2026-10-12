# Doloc Town 存档修改器

[下载 Windows 修改器](https://github.com/TonisK82/doloc-town-save-editor/releases/tag/v0.1.1) · [源码运行与打包](BUILD.md)

v0.1.1：道具列表增加垂直滚动条，右上角支持中文 / English 切换，支持修改玩家金钱（0–999,999,999）。缺少英文名称的道具显示英文 ID；搜索支持中文、英文和 ID。

编辑顶部金钱后点击“应用金钱”再保存；直接保存也会应用当前金钱输入。修改同步玩家余额和存档概览，保存前自动备份。语言切换保留未保存的修改。

English: Switch languages with the top-right selector. Edit Money and click Apply money, then Save. Saving also applies the money field. The range is 0–999,999,999. The catalog supports Chinese, English and ID searches and includes a vertical scrollbar. Quit the game before saving; backups are created automatically.

双击 `DolocTownSaveEditor.exe`，无需安装 Python。

1. 完全退出游戏，点击“打开存档”。默认目录为 `%USERPROFILE%\AppData\LocalLow\RedSawGames\DolocTown\SAVE`，通常选择 `doloc-save-0.data`。
2. 左侧选择背包或容器；箱子用游戏类型、坐标、ID 和存档路径区分。货架里的便携箱子也会列出。默认显示农场容器，可勾选显示城镇和地牢容器。
3. 右侧搜索中文名称或英文 ID，输入数量，添加到空格或替换选中格子。工具和不可堆叠物品上限为 1；需要更多时分多个格子添加。
4. 可单独修改现有物品数量或清空格子。修改数量保留原物品的特殊属性；替换会创建新物品，重置特殊属性。删除装有物品的箱子也会删除箱内内容。
5. 点击保存；程序自动创建 `.editor-backup-时间` 备份，并检测存档是否被其他程序更新。也可以先另存为副本。

恢复：退出游戏，将对应备份复制回原来的 `.data` 文件名。Steam 云同步发生冲突时，应选择你希望使用的本地或云端版本。

道具库包含本机游戏资源中的 990 种道具，包括特殊和开发用途物品；这些物品是否适合当前流程由游戏决定。未提供未解锁格子扩展、属性编辑或游戏进程内修改。

已验证：真实存档解密/加密回读、背包和容器修改、全部 990 种道具模板、自动备份、并发修改检测、界面初始化及搜索。未进行游戏内载入实测。原始存档和游戏安装文件未被修改。

当前为 v0.1.1 预发布。本版本依据 2026-10-13 本机安装资源制作。游戏更新后若格式或道具定义变化，需要重新核对兼容性。
