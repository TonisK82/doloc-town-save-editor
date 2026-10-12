# 从源码运行与打包

需要 Windows 和 Python 3.12（含 tkinter）。

```powershell
python -m pip install -r requirements.txt
python editor.py
python -m PyInstaller --noconfirm --windowed --onefile --name DolocTownSaveEditor --add-data "catalog.json;." editor.py
```

程序输出在 `dist/DolocTownSaveEditor.exe`。

`catalog.json` 仅包含道具名称、编号、叠加上限和存档模板。项目不包含游戏程序集、反编译源码、图像音频资源或玩家存档。

工具非官方，与游戏开发商和 Steam 无关联。当前版本依照 2026-10-13 本机安装版本制作；游戏更新后的兼容性需要重新验证。
