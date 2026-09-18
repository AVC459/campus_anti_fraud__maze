# Changelog

本项目的所有重要变更都会记录在此文件。
格式参考 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)，版本号遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

## [1.0.0] - 2026-09-17

首次公开发布。

### 剧情
- **四个章节、四种校园诈骗**：深渊之恋（网恋杀猪盘）、赌局陷阱（网络赌博）、校园贷危机（不良网贷）、求职陷阱（兼职刷单）
- **430 个剧情节点、24 个选择点、21 个结局节点**（19 个不重复结局），全部可达
- 结局按 `bad` / `normal` / `medium` / `good` / `perfect` / `neutral` 分级，达成 good / perfect 才解锁下一章
- **隐藏线索系统**：4 处可收集线索（`department_check`、`clue_1`、`clue_2`、`clue_hint_1`），发现时有青色粒子提示，结局页显示收集数量

### 系统
- **成就系统**：20 项成就，按 bad 5 / good 6 / perfect 4 / medium 2 / normal 1 / neutral 1 / special 1 分级着色，全解锁可得「完美收藏家」
- **存档读档**：保存当前章节与节点位置（`game_save.json`）
- **章节解锁进度**：记录在 `chapters.json`；成就进度记录在 `achievements.json`

### 表现
- **全屏背景 + 角色立绘**：场景图与立绘分离，支持多角色同框
- **打字机效果**：文字逐字显示，点击画面可立即显示全文
- **自动播放模式**：自动继续剧情，延迟可在 500–5000 ms 之间调节
- **选择点跳转**：可快进到下一个选择节点、快退到上一个选择节点
- **粒子特效**：成功 / 警示 / 线索 / 金色等多种反馈（`effects_manager.py`）
- **背景音乐**：音量可调、一键静音（音量与延迟写入 `settings.json`）

### 工程
- **资源与逻辑分离**：`core/resource_manager.py` 负责加载，`core/game_state.py` 负责状态，`core/audio_manager.py` 负责音频
- **剧本纯 JSON**：全部剧情在 `data/chapters/*.json`，改剧情无需改代码或重新编译
- **打包**：提供完整的 `反诈迷雾.spec`，`pyinstaller 反诈迷雾.spec --clean --noconfirm` 可产出单文件 exe，无需 Python 环境

### 说明
- `build/`、`dist/`、`__pycache__/`、`game_save.json` 已加入 `.gitignore`
- 约 119 MB 的 `反诈迷雾.exe` 通过 GitHub Release 分发，不进仓库
- 仓库内的 `achievements.json` 为空进度（`{"unlocked": []}`），下载即全新存档
