# Doloc Town 存档修改器 / Save Editor

[中文](#中文) · [English](#english)

## 中文

[下载 Windows 修改器 v0.1.1](https://github.com/TonisK82/doloc-town-save-editor/releases/tag/v0.1.1) · [源码运行与打包](BUILD.md)

### 作者声明

**我本人完全不会编程，此修改器完全由 ChatGPT 6.1 SOL 制作并发布。**

### 功能

- 编辑背包、箱子、货架里的便携箱子及其他容器物品。
- 搜索 990 种道具，添加、替换、清空格子或修改数量，遵守游戏叠加上限。
- 道具列表带垂直滚动条，支持中文、英文名称和 ID 搜索。
- 右上角可切换中文 / English，切换时保留未保存的修改。缺少英文名称的道具显示英文 ID。
- 修改玩家金钱，范围 **0–999,999,999**，同步玩家余额与存档概览。
- 保存前自动备份，并检测存档是否被其他程序更新。

### 使用方法

1. 下载发布页面中的 ZIP，解压后双击 `DolocTownSaveEditor-v0.1.1.exe`，无需安装 Python。
2. **完全退出游戏，建议先备份 `doloc-save-0.data`**，再点击“打开存档”。默认目录为 `%USERPROFILE%\AppData\LocalLow\RedSawGames\DolocTown\SAVE`，通常选择 `doloc-save-0.data`。
3. 左侧选择背包或容器。容器用游戏类型、坐标、ID 和存档路径区分；默认显示农场容器，可勾选显示城镇和地牢容器。
4. 右侧搜索道具，输入数量，添加到空格或替换选中格子。工具和不可堆叠物品上限为 1，需要更多时分多个格子添加。也可修改现有物品数量或清空格子。
5. 如需修改金钱，编辑顶部金钱输入框，点击“应用金钱”。直接点击保存也会应用当前金钱输入。
6. 修改完成后点击**“另存为”**，在原存档目录选择 **`doloc-save-0.data`**，确认覆盖。程序覆盖已有文件时也会自动创建备份，文件名包含 `.editor-backup-时间`。

修改数量保留原物品的特殊属性；替换会创建新物品并重置特殊属性。删除装有物品的箱子也会删除箱内内容。

### 恢复备份

退出游戏，将对应备份复制回原来的 `.data` 文件名。Steam 云同步发生冲突时，选择你希望使用的本地或云端版本。

### 验证与兼容性

当前为 **v0.1.1 正式发布版**，依据 2026-10-13 的本机安装资源制作。已验证存档解密/加密回读、背包和容器编辑、990 种道具模板、自动备份、覆盖冲突检测、滚动条、中英文切换与编辑保留、金钱边界以及独立程序启动。**仓库作者已完成游戏内实测，确认修改器可用。**

道具库包括特殊和开发用途物品，其在当前游戏流程中的可用性由游戏决定。暂不支持未解锁格子扩展、其他玩家属性编辑或游戏进程内修改。游戏更新后若存档格式或道具定义变化，需要重新验证兼容性。

本工具为非官方项目，与游戏开发商及 Steam 无关联。

## English

[Download Windows Save Editor v0.1.1](https://github.com/TonisK82/doloc-town-save-editor/releases/tag/v0.1.1) · [Run and build from source](BUILD.md)

### Author's statement

**I do not know how to program at all. This save editor was entirely created and published by ChatGPT 6.1 SOL.**

### Features

- Edit items in the backpack, boxes, portable boxes on shelves, and other containers.
- Search 990 items; add or replace items, clear slots, or change quantities within the game's stack limits.
- Scroll through the item catalog with a vertical scrollbar. Search by Chinese name, English name, or item ID.
- Switch between Chinese and English in the top-right corner without losing unsaved edits. Items without an English name display their English ID.
- Edit player money within **0–999,999,999**, updating both the player balance and the save overview.
- Automatically create backups before saving and detect changes made to the save by another program.

### How to use

1. Download the ZIP from the release page, extract it, and double-click `DolocTownSaveEditor-v0.1.1.exe`. No Python installation is required.
2. **Quit the game completely. Backing up `doloc-save-0.data` first is recommended.** Then click “Open save.” The default folder is `%USERPROFILE%\AppData\LocalLow\RedSawGames\DolocTown\SAVE`. Usually, select `doloc-save-0.data`.
3. Select the backpack or a container on the left. Containers are identified by game type, coordinates, ID, and save path. Farm containers appear by default; enable the checkbox to show town and dungeon containers.
4. Search for an item on the right, enter a quantity, and add it to an empty slot or replace the selected slot. Tools and non-stackable items have a limit of 1; use multiple slots for additional copies. You can also change existing quantities or clear slots.
5. To edit money, enter a value in the Money field and click “Apply money.” Clicking Save also applies the current money input.
6. After editing, click **“Save as,”** select **`doloc-save-0.data`** in the original save folder, and confirm overwriting it. The program also automatically backs up existing files before overwriting them; backup filenames include `.editor-backup-` followed by a timestamp.

Changing a quantity preserves the item's special properties. Replacing an item creates a new item and resets those properties. Deleting a box also deletes its contents.

### Restore a backup

Quit the game and copy the chosen backup back to the original `.data` filename. If Steam Cloud reports a conflict, choose the local or cloud version you intend to use.

### Verification and compatibility

This is the **v0.1.1 stable release**, based on the locally installed game resources on October 13, 2026. Verification covered save decryption/encryption round trips, backpack and container editing, 990 item templates, backups, overwrite conflict detection, scrolling, language switching with pending edits, money bounds, and packaged application startup. **The repository owner has tested the editor in-game and confirmed that it works.**

The catalog includes special and development items; the game determines whether they work in your current progress. Expanding locked slots, editing other player attributes, and modifying the running game are not supported. Compatibility must be rechecked if a game update changes the save format or item definitions.

This is an unofficial project and is not affiliated with the game developer or Steam.
