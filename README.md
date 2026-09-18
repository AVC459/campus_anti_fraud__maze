<div align="center">
  <img src="images/banner.svg" alt="咸师反诈迷雾 · Campus Anti-Fraud Maze" width="100%">

  <h1>咸师反诈迷雾</h1>

  <p><b>一款讲校园诈骗的文字冒险游戏 —— 4 个章节，430 个剧情节点，21 个结局节点。</b><br>
  不做说教，让你在故事里自己撞一次南墙。</p>

  <p>
    <img src="https://img.shields.io/badge/Python-3.11-3776AB?style=flat-square&logo=python&logoColor=white" alt="Python">
    <img src="https://img.shields.io/badge/Tkinter-GUI-2563EB?style=flat-square" alt="Tkinter">
    <img src="https://img.shields.io/badge/Pygame-%E9%9F%B3%E9%A2%91-10B981?style=flat-square" alt="Pygame audio">
    <img src="https://img.shields.io/badge/%E5%89%A7%E6%9C%AC-430%20%E8%8A%82%E7%82%B9-64748B?style=flat-square" alt="430 nodes">
    <img src="https://img.shields.io/badge/%E7%BB%93%E5%B1%80-21%20%E4%B8%AA-64748B?style=flat-square" alt="21 endings">
  </p>

  <p><a href="README_EN.md">English</a> · <b>简体中文</b></p>
</div>

---

## 这是什么

反诈宣传见过太多，通常是几张 PPT 加一句"提高警惕"。问题是没人会在真被骗的那一刻想起 PPT。

**咸师反诈迷雾**换了个做法：把你放进骗局里，让你自己做选择。主角是大学生「小夏」，四个章节是四种最常见的校园诈骗套路 —— 网恋杀猪盘、网络赌博、校园贷、兼职刷单。每一章都有多条分支，你的每个选择都会改变信任值、怀疑值和损失金额，最后落到不同的结局上。

结局是分级的：`bad` 是彻底沉沦，`perfect` 是不仅自己没上当还拉住了别人。**只有在 good / perfect 这一档，下一章才会解锁** —— 这一点和现实有点像。

> 游戏里埋了 4 处隐藏线索，发现时会有青色粒子提示，结局页会显示收集数量。

## 下载即玩

到 [Releases](../../releases/latest) 下载 **`anti-fraud-maze.exe`**（单文件，约 119 MB，**无需安装 Python 环境**），双击运行 —— 它就是 `pyinstaller` 打包出的 `反诈迷雾.exe`，同一份文件，只是 Release 附件用了 ASCII 文件名。

首次启动会在 exe 同级目录生成 `achievements.json`（成就进度）与 `game_save.json`（存档）。

## 从源码运行

```bash
pip install pillow pygame
python main.py
```

需要 Python 3 与标准库自带的 Tkinter（官方安装包默认包含）。

## 四个章节

| 章节 | 名称 | 诈骗类型 | 剧情节点 | 选择点 | 结局节点 |
|---|---|---|---|---|---|
| 第一章 | 深渊之恋 | 网恋诈骗（杀猪盘） | 132 | 14 | 6 |
| 第二章 | 赌局陷阱 | 网络赌博诈骗 | 168 | 6 | 8 |
| 第三章 | 校园贷危机 | 不良网贷诈骗 | 50 | 1 | 3 |
| 第四章 | 求职陷阱 | 兼职刷单诈骗 | 80 | 3 | 4 |
| **合计** | | | **430** | **24** | **21** |

<img src="images/storymap.svg" alt="四章剧情与结局分布" width="100%">

## 结局一览

### 第一章 · 深渊之恋

| 结局 | 类型 |
|---|---|
| 彻底沉沦 | bad |
| 半醒半梦 | medium |
| 老师出手 | good |
| 报警成功 | good |
| 火车站对峙 | medium |
| 及时清醒 | neutral |

### 第二章 · 赌局陷阱

| 结局 | 类型 |
|---|---|
| 深渊难爬 | bad |
| 理性救赎 | good |
| 反诈先锋 | perfect |
| 迷途知返 | normal |
| 明智抉择 | perfect |
| 悬崖勒马 | good |

> 第二章共 **8 个结局节点**，「悬崖勒马」有三个不同入口，去重后是 6 个结局。全游戏 21 个结局节点、19 个不重复结局。

### 第三章 · 校园贷危机

| 结局 | 类型 |
|---|---|
| 绝处逢生 | good |
| 悔之晚矣 | bad |
| 家难临头 | bad |

### 第四章 · 求职陷阱

| 结局 | 类型 |
|---|---|
| 迷途知返 | good |
| 血本无归 | bad |
| 保持警惕 | perfect |
| 防微杜渐 | perfect |

## 玩法

1. **开始演练** —— 主菜单点「开始演练」，选择已解锁的章节
2. **阅读剧情** —— 文字逐字显示，点击画面可立即显示全文
3. **做出选择** —— 关键节点出现选项，不同选择影响信任值、怀疑值与损失金额
4. **右上角控制栏** —— ⏩ 快进到下一个选择节点 / ▶ 自动播放 / ⏪ 快退到上一个选择节点 / 💾 存档 / ⚙ 设置
5. **结局判定** —— 达成 `good` / `perfect` 结局解锁下一章
6. **成就收集** —— 主菜单「成就系统」查看进度，20 项全解锁可拿到「完美收藏家」

## 功能特性

| | 特性 | 说明 |
|---|---|---|
| 🎮 | **多分支剧情** | 430 个剧情节点、24 个选择点、21 个结局节点，全部可达 |
| 🏆 | **成就系统** | 20 项成就，按 bad 5 / good 6 / perfect 4 / medium 2 / normal 1 / neutral 1 / special 1 分级着色 |
| 🖼️ | **全屏背景 + 角色立绘** | 场景图与立绘分离，支持多角色同框 |
| ⌨️ | **打字机效果** | 文字逐字显示，点击可跳过等待 |
| ▶️ | **自动播放** | 自动继续剧情，延迟可在 500–5000 ms 之间调节 |
| ⏪⏩ | **选择点跳转** | 直接快进到下一个 / 快退到上一个选择节点，方便重试分支 |
| 💾 | **存档读档** | 保存当前章节与节点位置 |
| 🎵 | **背景音乐** | 音量可调、一键静音 |
| ✨ | **粒子特效** | 成功 / 警示 / 线索 / 金色等多种反馈，线索发现时会有青色提示 |
| 🔍 | **隐藏线索** | 4 处可收集线索，结局页显示收集情况 |

## 隐藏线索

| 线索 ID | 位置 | 内容 |
|---|---|---|
| `department_check` | 第一章 | 查询学籍时发现查无此人 |
| `clue_1` / `clue_2` | 第二章 | 老蛋诱导下注时露出的破绽 |
| `clue_hint_1` | 第二章 | 老蛋拿手机时手在发抖 |

## 技术栈

| 用途 | 选型 |
|---|---|
| GUI | **Tkinter**（`Canvas` 全屏绘制 + 组件叠加） |
| 图像 | **Pillow**（`Image` / `ImageTk`，立绘与背景缩放） |
| 音频 | **Pygame**（`mixer` 播放背景音乐，音量实时调整） |
| 数据 | 纯 **JSON** 剧本，无数据库、无网络请求 |
| 打包 | **PyInstaller**（单文件 exe） |

Python 源码合计约 2500 行，其中 `main.py` 1736 行负责渲染、流程与设置。

## 项目结构

```
├── main.py                    # 主程序：渲染、流程控制、设置与存档
├── chapter_manager.py         # 章节加载与解锁进度管理
├── effects_manager.py         # 粒子与视觉特效
├── core/
│   ├── game_state.py          # 状态管理（信任值 / 怀疑值 / 金钱 / 线索 / 成就）
│   ├── audio_manager.py       # 背景音乐与音量设置
│   └── resource_manager.py    # 资源加载
├── data/chapters/
│   ├── chapter1.json          # 第一章脚本（132 节点）
│   ├── chapter2.json          # 第二章脚本（168 节点）
│   ├── chapter3.json          # 第三章脚本（50 节点）
│   └── chapter4.json          # 第四章脚本（80 节点）
├── assets/first/              # 背景图与角色立绘
├── music/                     # 背景音乐
├── md/                        # 剧情策划与角色设计文档
├── settings.json              # 音量与自动播放设置
├── chapters.json              # 章节解锁进度
├── achievements_config.json   # 成就定义（20 项）
├── achievements.json          # 成就解锁进度（运行时写入）
├── 反诈迷雾.spec              # PyInstaller 打包配置
└── requirements.txt
```

> `build/`、`dist/`、`__pycache__/`、`game_save.json` 已在 `.gitignore` 中；exe 通过 [Releases](../../releases/latest) 分发，不进仓库。

## 剧本格式

章节 JSON 顶层是对象，`script` 字段是节点数组：

```json
{
  "id": "chapter1",
  "name": "深渊之恋",
  "script": [
    { "role": "旁白", "content": "剧情文本", "bg": "pg1" },
    { "type": "choice", "content": "问题？", "options": [
        { "text": "选项A", "next": 5, "effect": { "trust": 5, "set_money": -100 } }
    ]},
    { "type": "ending", "ending_id": "call_police",
      "ending_name": "报警成功", "ending_type": "good", "content": "..." }
  ]
}
```

推进规则：`choice` 节点走 `option.next`；其他节点有 `jump` 则跳转，否则前进到 `idx + 1`；`ending` 是终点。

选项效果支持**顶层字段**与 **`effect` 子对象**两种等价写法（第一章用 `effect`，其余章节用顶层字段）：

```json
{ "text": "A", "next": 5, "set_money": -100, "trust": 5 }
{ "text": "B", "next": 6, "effect": { "set_money": -100, "trust": 5 } }
```

## 自己打包

```bash
pyinstaller 反诈迷雾.spec --clean --noconfirm
```

产物为 `dist/反诈迷雾.exe`（单文件，无需 Python 环境）。

## 常见问题

<details>
<summary><b>为什么仓库里没有 exe？</b></summary>

`anti-fraud-maze.exe` 约 119 MB，超过 GitHub 单文件 100 MB 的限制，所以放在 [Releases](../../releases/latest) 而不是仓库里。仓库里保留了完整的 `.spec`，你自己 `pyinstaller` 也能打出同样的包。
</details>

<details>
<summary><b>成就和存档会跟着仓库走吗？</b></summary>

`achievements.json` 在仓库里是**空进度**（`{"unlocked": []}`），`game_save.json` 已被忽略。所以你下下来就是全新存档，不会继承别人的通关记录。
</details>

<details>
<summary><b>没有声音 / 音乐放不出来？</b></summary>

背景音乐走 Pygame，请确认 `pip install pygame` 成功，并且 `music/` 目录下的音频文件没被删。设置面板里也能一键静音，先检查一下音量。
</details>

<details>
<summary><b>能在 macOS / Linux 上跑吗？</b></summary>

代码是 Tkinter + Pillow + Pygame，跨平台可用，只是 `dist/` 里的 exe 是 Windows 版本。其他系统请从源码运行。
</details>

<details>
<summary><b>剧情可以自己改吗？</b></summary>

可以，全部剧情都在 `data/chapters/*.json` 里，格式见上面的「剧本格式」一节。改完直接重启游戏即可，不需要重新编译。
</details>

## 开发文档

`md/` 目录里放了策划过程：

- `gamestory_plan.md` —— 整体剧情规划
- `多结局剧情扩展方案.md` —— 多结局设计思路
- `角色设计文档_小夏与老蛋.md` —— 主要角色设定
- `AI绘图提示词文档.md` —— 素材生成用到的提示词
- `《咸师反诈迷雾：赌局陷阱》情节梳理(1).docx` —— 第二章梳理

## 更新日志

见 [CHANGELOG.md](CHANGELOG.md)。

## 参与贡献

欢迎开 [Issue](../../issues) 反馈剧情逻辑问题、错别字或漏掉的诈骗套路，也欢迎直接 PR 新的章节脚本与结局。改剧情请附上节点可达性说明。

如果这个游戏让身边多一个人少上一次当，给个 ⭐ 就是最好的支持。

## 赞赏

这个游戏不带广告、不收费、也不收集任何数据。如果它让你或者你的同学对某个骗局多留了一点心，可以请我喝杯咖啡 —— 完全随意，不请也照样能玩。

<table align="center">
  <tr>
    <td align="center" width="240"><img src="images/alipay-qr.jpg" width="200" alt="支付宝收款码"><br><b>支付宝</b></td>
    <td align="center" width="240"><img src="images/wechat-qr.png" width="200" alt="微信收款码"><br><b>微信</b></td>
  </tr>
</table>

## 许可

本项目**仅供学习、教学与公益反诈宣传使用**，详见 [LICENSE](LICENSE)。

---

**反诈提醒**：网络交友需谨慎，涉及金钱交易务必提高警惕！如遇诈骗请立即拨打 **96110**。
