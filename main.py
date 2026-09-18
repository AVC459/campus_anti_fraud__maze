import os
import sys

# 设置正确的 Tcl/Tk 库路径
# 对于虚拟环境，使用基础 Python 安装路径
base_prefix = getattr(sys, 'base_prefix', sys.prefix)
tcl_path = os.path.join(base_prefix, 'tcl', 'tcl8.6')
tk_path = os.path.join(base_prefix, 'tcl', 'tk8.6')

if os.path.exists(tcl_path):
    os.environ['TCL_LIBRARY'] = tcl_path
if os.path.exists(tk_path):
    os.environ['TK_LIBRARY'] = tk_path

import tkinter as tk
from tkinter import messagebox
import json
# Deleted:import sys
from PIL import Image, ImageTk
import pygame
from chapter_manager import ChapterManager
from effects_manager import EffectsManager
from core.game_state import GameStateManager
from core.resource_manager import ResourceManager
from core.audio_manager import AudioManager

def resource_path(relative_path):
    """获取资源文件的绝对路径，支持开发环境和打包后的环境"""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


class AntiFraudGame:
    def __init__(self, root):
        self.root = root
        self.root.title("咸师反诈迷雾")

        # 1. 硬件全屏适配
        self.root.attributes("-fullscreen", True)
        self.sw = self.root.winfo_screenwidth()
        self.sh = self.root.winfo_screenheight()

        self.save_file = "game_save.json"
        
        # 当前章节
        self.current_chapter = "chapter1"

        # 流式输出相关
        self.typing_text = ""
        self.typing_index = 0
        self.typing_id = None
        self.typing_speed = 50  # 打字速度（毫秒）

        # 自动播放相关
        self.auto_play = False  # 自动播放状态
        self.auto_play_id = None  # 自动播放定时器ID
        # 从 settings.json 加载自动播放延迟，默认 2000
        self.auto_play_delay = self.load_auto_play_delay()  # 自动继续延迟（毫秒）

        # --- 初始化核心组件 ---
        self.state_manager = GameStateManager()
        self.resource_manager = ResourceManager(self.sw, self.sh)
        self.audio_manager = AudioManager()

        # --- 加载成就配置 ---
        self.achievements_config = self._load_achievements_config()

        # --- 加载图片资源 ---
        self.load_assets()

        # --- 初始化并播放背景音乐 ---
        self.init_bgm()

        # --- 初始化章节管理器 ---
        self.chapter_manager = ChapterManager()

        # 默认脚本为空，选择章节时加载
        self.script = []

        self.idx = 0
        
        # 记录玩家选择历史，用于回退功能
        self.choice_history = []
        self.canvas = tk.Canvas(self.root, width=self.sw, height=self.sh, bg="#0f0e17", highlightthickness=0)
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self.next_scene)

        self.effects_manager = EffectsManager(self.canvas, self.root, self.sw, self.sh)
        self.effects_manager.start()

        self.render_menu()

    def load_assets(self):
        """预加载并缩放所有背景图和人物立绘（等比例缩放）"""
        self.images = {}
        paths = {
            # 通用背景
            "index": "assets/first/index.jpg",
            "pg1": "assets/first/pg1.jpg",
            "pg2": "assets/first/pg2.jpg",
            "pg3": "assets/first/pg3.jpg",
            "pg4": "assets/first/pg4.jpg",
            "pg5": "assets/first/pg5.jpg",
            "pg6": "assets/first/pg6.jpg",
            "playground": "assets/first/playground.png",
            "wangba": "assets/first/网吧.png",
            "canteen": "assets/first/食堂.jpg",
            "counselor_office": "assets/first/辅导员办公室.jpg",
            "security_office": "assets/first/保卫处场景.jpg",
            # chapter1 背景
            "cafe": "assets/first/pg4.jpg",
            "bedroom": "assets/first/pg5.jpg",
            "campus": "assets/first/pg6.jpg",
            # chapter3 背景
            "dormitory": "assets/first/pg5.jpg",
            "classroom": "assets/first/pg2.jpg"
        }
        for key, path in paths.items():
            try:
                img = Image.open(resource_path(path))
                img = img.resize((self.sw, self.sh), Image.Resampling.LANCZOS)
                self.images[key] = ImageTk.PhotoImage(img)
            except Exception as e:
                print(f"无法加载图片 {path}: {e}")
                placeholder = Image.new('RGB', (self.sw, self.sh), color='#1a1c2c')
                self.images[key] = ImageTk.PhotoImage(placeholder)
        
        self.characters = {}
        self.character_info = {}
        char_paths = {
            "linshu1": "assets/first/character/girl1.png",
            "linshu2": "assets/first/character/girl2.png",
            "linshu3": "assets/first/character/girl3.png",
            "magor": "assets/first/character/magor.png",
            "magor2": "assets/first/character/magor2.png",
            "polic": "assets/first/character/polic.png",
            "luren_jia": "assets/first/character/路人甲.png",
            "luren_yi": "assets/first/character/路人乙.png",
            "fudaoyuan": "assets/first/character/辅导员.png",
            "xiaxia": "assets/first/character/小夏.png",
            "laodan": "assets/first/character/老蛋.png",
            "xiaogao": "assets/first/character/小高.png",
            "security_teacher": "assets/first/character/保卫处老师.png"
        }
        target_height = int(self.sh * 0.42)
        for key, path in char_paths.items():
            try:
                img = Image.open(resource_path(path))
                original_width, original_height = img.size
                ratio = original_width / original_height
                new_width = int(target_height * ratio)
                img = img.resize((new_width, target_height), Image.Resampling.LANCZOS)
                self.characters[key] = ImageTk.PhotoImage(img)
                self.character_info[key] = {"width": new_width, "height": target_height}
            except Exception as e:
                print(f"无法加载人物图片 {path}: {e}")
                new_width = int(target_height * 0.6)
                placeholder = Image.new('RGBA', (new_width, target_height), color=(45, 52, 54, 128))
                self.characters[key] = ImageTk.PhotoImage(placeholder)
                self.character_info[key] = {"width": new_width, "height": target_height}
        
        self.linshu_index = 0
        self.linshu_images = ["linshu1", "linshu2", "linshu3"]
        
        self.role_to_character = {
            "林舒学姐": "linshu",
            "林警官": "polic",
            "民警": "magor",
            "警察": "magor",
            "周学长": "magor2",
            "神秘声音": "polic",
            "室友A": "luren_jia",
            "室友B": "luren_yi",
            "辅导员": "fudaoyuan",
            "导员": "fudaoyuan",
            "生科院学生": "luren_yi",
            "同学": "luren_jia",
            "招聘员": "luren_yi",
            "母亲": "luren_jia",
            "小夏": "xiaxia",
            "老蛋": "laodan",
            "小高": "xiaogao",
            "保卫处老师": "security_teacher",
            "你": "xiaxia",
            "旁白": None,
            "心理": None,
            "系统": None,
            "真相": None
        }

    def _load_achievements_config(self):
        """加载成就配置文件"""
        try:
            config_path = resource_path("achievements_config.json")
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"加载成就配置失败: {e}")
            return {"achievements": []}

    def _check_all_achievements(self):
        """检查是否解锁了所有结局成就，如果是则解锁特殊成就"""
        # 获取所有非特殊成就
        all_ending_achievements = [
            a.get("id") for a in self.achievements_config.get("achievements", [])
            if a.get("chapter") != "all"
        ]
        
        # 检查是否全部解锁
        unlocked = self.state_manager.get_all_unlocked_achievements()
        all_unlocked = all(achievement_id in unlocked for achievement_id in all_ending_achievements)
        
        if all_unlocked:
            # 解锁特殊成就
            self.state_manager.unlock_achievement("chapter_all_collector")

    def init_bgm(self):
        """初始化并循环播放背景音乐"""
        self.audio_manager.init_bgm("music/The Search - Richard Harvey.mp3")

    def set_bgm_volume(self, volume):
        """设置BGM音量"""
        self.audio_manager.set_volume(volume)

    def load_bgm_volume(self):
        """从配置文件加载BGM音量"""
        return self.audio_manager.get_volume()

    def save_bgm_volume(self):
        """保存BGM音量到配置文件"""
        pass  # 已经在 AudioManager 中处理

    def load_auto_play_delay(self):
        """从 settings.json 加载自动播放延迟"""
        try:
            with open('settings.json', 'r', encoding='utf-8') as f:
                settings = json.load(f)
                return settings.get('game_settings', {}).get('auto_play_delay', 2000)
        except:
            return 2000

    def save_auto_play_delay(self):
        """保存自动播放延迟到 settings.json"""
        try:
            path = 'settings.json'
            settings = {}
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
            except:
                pass
            if 'game_settings' not in settings:
                settings['game_settings'] = {}
            settings['game_settings']['auto_play_delay'] = self.auto_play_delay
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(settings, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"保存自动播放延迟失败: {e}")

    def unlock_next_chapter(self):
        """解锁下一章节"""
        self.chapter_manager.unlock_next_chapter(self.current_chapter)

    def select_chapter(self, chapter_id):
        """选择章节开始游戏"""
        if not self.chapter_manager.is_chapter_unlocked(chapter_id):
            messagebox.showwarning("提示", "该章节尚未解锁，请先完成前一章！")
            return
        self.current_chapter = chapter_id
        self.script = self.chapter_manager.get_chapter_script(chapter_id)
        if not self.script:
            messagebox.showwarning("提示", "章节脚本加载失败！")
            return
        self.start_game()

    def save_game(self):
        # 清除之前的提示
        if hasattr(self, 'save_hint_label'):
            self.save_hint_label.destroy()
        if hasattr(self, 'save_success_label'):
            self.save_success_label.destroy()

        # 显示保存中转圈提示
        self.save_hint_label = tk.Label(self.root, text="⏳ 保存中...", font=("微软雅黑", 12),
                                        bg="#444", fg="white", padx=10, pady=5)
        self.canvas.create_window(self.sw - 80, self.sh - 40, window=self.save_hint_label)

        def do_save():
            success = self.state_manager.save_to_file(self.save_file, self.idx, self.current_chapter)
            
            # 销毁保存中提示
            self.save_hint_label.destroy()

            if success:
                # 显示保存成功
                self.save_success_label = tk.Label(self.root, text="✓ 保存成功", font=("微软雅黑", 12),
                                                   bg="#444", fg="white", padx=10, pady=5)
                self.canvas.create_window(self.sw - 80, self.sh - 40, window=self.save_success_label)
                self.root.after(3000, lambda: self.save_success_label.destroy() if hasattr(self, 'save_success_label') else None)
            else:
                self.save_fail_label = tk.Label(self.root, text="✗ 保存失败", font=("微软雅黑", 12),
                                                bg="#ff4757", fg="white", padx=10, pady=5)
                self.canvas.create_window(self.sw - 80, self.sh - 40, window=self.save_fail_label)
                self.root.after(3000, lambda: self.save_fail_label.destroy() if hasattr(self, 'save_fail_label') else None)

        # 异步执行保存（稍微延迟一下让用户看到转圈效果）
        self.root.after(100, do_save)

    def load_game(self):
        save_data = self.state_manager.load_from_file(self.save_file)
        if save_data is None:
            messagebox.showwarning("提示", "还没有进行过游戏！")
            return
        
        chapter_id = save_data.get("current_chapter", "chapter1")
        
        # 加载章节脚本
        self.current_chapter = chapter_id
        self.script = self.chapter_manager.get_chapter_script(chapter_id)
        if not self.script:
            messagebox.showwarning("提示", "章节脚本加载失败！")
            return
        
        self.idx = save_data.get("idx", 0)
        self.auto_play = False
        if self.auto_play_id:
            self.root.after_cancel(self.auto_play_id)
            self.auto_play_id = None
        # 清空选择历史（因为存档中没有保存历史记录）
        self.choice_history = []
        self.render_frame()

    def render_menu(self):
        self.idx = -2
        if self.auto_play_id:
            self.root.after_cancel(self.auto_play_id)
            self.auto_play_id = None
        self.auto_play = False
        self.clear_all_widgets()
        self.canvas.delete("all")

        self.effects_manager.clear_all()

        self.canvas.create_image(0, 0, image=self.images["index"], anchor="nw")

        self.canvas.create_rectangle(0, 0, self.sw, self.sh, fill="#1a1a2e", stipple="gray50")

        self.effects_manager.create_floating_particles(count=25, color="#ff8906")

        # 标题区域
        self.canvas.create_text(self.sw / 2, self.sh * 0.25, text="咸师反诈迷雾",
                                fill="#ff4757", font=("黑体", 64, "bold"))
        self.canvas.create_text(self.sw / 2, self.sh * 0.32, text="—— 反诈教育互动游戏 ——",
                                fill="#fff", font=("微软雅黑", 22))

        # 警示标语
        self.canvas.create_text(self.sw / 2, self.sh * 0.38,
                                text="提高警惕 · 认清骗局 · 守护财产",
                                fill="#ff8906", font=("微软雅黑", 18))

        # 按钮区域 - 采用警方警示风格
        btn_y = 0.50
        buttons = [
            ("开始演练", self.render_chapter_select),
            ("继续上次", self.load_game),
            ("成就系统", self.render_achievements),
            ("游戏设置", self.render_settings),
            ("退出游戏", self.quit_game)
        ]

        for i, (text, cmd) in enumerate(buttons):
            # 按钮配色方案 - 反诈警示风格
            if i == 0:
                # 开始按钮 - 红色警示
                normal_bg = "#c0392b"
                hover_bg = "#e74c3c"
                border_color = "#ff6b6b"
            else:
                # 其他按钮 - 深色沉稳
                normal_bg = "#2d3436"
                hover_bg = "#3d4446"
                border_color = "#636e72"

            # 创建按钮 - 简洁矩形样式
            btn = tk.Label(self.root, text=text, font=("黑体", 22, "bold"),
                           bg=normal_bg, fg="white",
                           padx=60, pady=15,
                           cursor="hand2",
                           bd=2, relief="raised",
                           highlightbackground=border_color,
                           highlightthickness=2)

            btn.bind("<Button-1>", lambda e, c=cmd: c())
            btn.bind("<Enter>", lambda e, b=btn, h=hover_bg: b.config(bg=h))
            btn.bind("<Leave>", lambda e, b=btn, n=normal_bg: b.config(bg=n))

            self.canvas.create_window(self.sw / 2, self.sh * btn_y, window=btn)
            btn_y += 0.09

        # 底部反诈提示
        self.canvas.create_text(self.sw / 2, self.sh * 0.92,
                                text="⚠️ 如遇诈骗请立即拨打 96110 ⚠️",
                                fill="#ff4757", font=("微软雅黑", 18))
        self.canvas.create_text(self.sw / 2, self.sh * 0.96,
                                text="咸阳师范学院 · 咸阳市公安局反诈中心 出品",
                                fill="#71717a", font=("微软雅黑", 14))

    def render_chapter_select(self):
        """渲染章节选择页面"""
        self.idx = -2
        if self.auto_play_id:
            self.root.after_cancel(self.auto_play_id)
            self.auto_play_id = None
        self.auto_play = False
        self.clear_all_widgets()
        self.canvas.delete("all")

        self.effects_manager.clear_all()

        self.canvas.create_image(0, 0, image=self.images["index"], anchor="nw")

        self.canvas.create_rectangle(0, 0, self.sw, self.sh, fill="#1a1a2e", stipple="gray50")

        self.effects_manager.create_floating_particles(count=20, color="#ff4757")

        # 标题区域
        self.canvas.create_text(self.sw / 2, self.sh * 0.15, text="章节选择",
                                fill="#ff4757", font=("黑体", 56, "bold"))
        self.canvas.create_text(self.sw / 2, self.sh * 0.21, text="选择你想体验的反诈剧情",
                                fill="#fff", font=("微软雅黑", 20))

        # 横向排列章节卡片
        chapters = self.chapter_manager.chapters
        total_chapters = len(chapters)
        start_x = 0.12  # 起始位置
        spacing = (1 - start_x * 2) / total_chapters  # 每个卡片的宽度

        for i, chapter in enumerate(chapters):
            if chapter["unlocked"]:
                btn_text = f"{chapter['icon']}\n{chapter['name']}\n{chapter['description']}"
                bg_color = "#2d3436"
                fg_color = "white"
                cursor = "hand2"
                cmd = lambda c=chapter["id"]: self.select_chapter(c)
            else:
                btn_text = f"🔒\n{chapter['name']}\n尚未解锁"
                bg_color = "#1a1a2e"
                fg_color = "#666"
                cursor = "arrow"
                cmd = lambda: None

            # 计算卡片位置（横向均匀分布）
            card_x = start_x + i * spacing + spacing / 2

            # 创建章节卡片（紧凑设计）
            card = tk.Label(self.root, text=btn_text, font=("微软雅黑", 16, "bold"),
                            bg=bg_color, fg=fg_color,
                            padx=25, pady=20,
                            cursor=cursor,
                            justify="center",
                            bd=2, relief="raised",
                            highlightbackground="#ff4757" if chapter["unlocked"] else "#333",
                            highlightthickness=1)

            card.bind("<Button-1>", lambda e, c=cmd: c())
            if chapter["unlocked"]:
                card.bind("<Enter>", lambda e, b=card: b.config(bg="#c0392b"))
                card.bind("<Leave>", lambda e, b=card: b.config(bg="#2d3436"))

            self.canvas.create_window(self.sw * card_x, self.sh * 0.5, window=card)

        # 章节进度提示
        unlocked_count = self.chapter_manager.get_unlocked_count()
        total_count = self.chapter_manager.get_total_chapters()
        self.canvas.create_text(self.sw / 2, self.sh * 0.72,
                                text=f"📊 已解锁章节: {unlocked_count}/{total_count}",
                                fill="#ff8906", font=("微软雅黑", 18))

        # 返回按钮
        back_frame = tk.Frame(self.root, bg="#1a2744", bd=2, relief="groove",
                              highlightbackground="#00d4ff", highlightthickness=1)
        back_btn = tk.Label(back_frame, text="🔙 返回主菜单", font=("微软雅黑", 18, "bold"),
                            bg="#1a2744", fg="#fff", padx=40, pady=15, cursor="hand2")
        back_btn.pack()
        back_btn.bind("<Button-1>", lambda e: self.render_menu())
        back_btn.bind("<Enter>", lambda e, b=back_btn, f=back_frame: [b.config(bg="#00d4ff", fg="#0a192f"),
                                                                      f.config(bg="#00d4ff")])
        back_btn.bind("<Leave>",
                      lambda e, b=back_btn, f=back_frame: [b.config(bg="#1a2744", fg="#fff"), f.config(bg="#1a2744")])
        self.canvas.create_window(self.sw / 2, self.sh * 0.88, window=back_frame)

    def render_achievements(self):
        """渲染成就展示页面 - 带滚动功能"""
        self.idx = -2
        if self.auto_play_id:
            self.root.after_cancel(self.auto_play_id)
        self.auto_play = False
        self.clear_all_widgets()
        self.canvas.delete("all")

        self.effects_manager.clear_all()

        # 绘制背景
        self.canvas.create_image(0, 0, image=self.images["index"], anchor="nw")
        self.canvas.create_rectangle(0, 0, self.sw, self.sh, fill="#1a1a2e", stipple="gray50")
        self.effects_manager.create_floating_particles(count=15, color="#ffd700")

        # 标题区域（固定）
        self.canvas.create_text(self.sw / 2, self.sh * 0.06, text="🏆 成就系统",
                                fill="#ffd700", font=("黑体", 48, "bold"))

        # 统计信息（固定）
        unlocked_count = len(self.state_manager.get_all_unlocked_achievements())
        total_count = len([a for a in self.achievements_config.get("achievements", []) if a.get("chapter") != "all"])
        self.canvas.create_text(self.sw / 2, self.sh * 0.11,
                                text=f"已解锁成就: {unlocked_count}/{total_count}",
                                fill="#fff", font=("微软雅黑", 18))

        # 返回按钮（固定在底部）
        back_frame = tk.Frame(self.root, bg="#1a2744", bd=2, relief="groove",
                              highlightbackground="#00d4ff", highlightthickness=1)
        back_btn = tk.Label(back_frame, text="🔙 返回主菜单", font=("微软雅黑", 16, "bold"),
                            bg="#1a2744", fg="#fff", padx=35, pady=12, cursor="hand2")
        back_btn.pack()
        back_btn.bind("<Button-1>", lambda e: self.render_menu())
        back_btn.bind("<Enter>", lambda e, b=back_btn, f=back_frame: [b.config(bg="#00d4ff", fg="#0a192f"),
                                                                      f.config(bg="#00d4ff")])
        back_btn.bind("<Leave>",
                      lambda e, b=back_btn, f=back_frame: [b.config(bg="#1a2744", fg="#fff"), f.config(bg="#1a2744")])
        self.canvas.create_window(self.sw / 2, self.sh * 0.95, window=back_frame)

        # 成就卡片滚动区域
        scroll_area_top = int(self.sh * 0.15)
        scroll_area_bottom = int(self.sh * 0.88)
        scroll_area_height = scroll_area_bottom - scroll_area_top

        # 绘制半透明背景遮罩
        self.canvas.create_rectangle(0, scroll_area_top, self.sw, scroll_area_bottom,
                                     fill="#000000", stipple="gray50")  # 50%透明的黑色背景

        # 创建滚动Canvas（背景与主界面一致）
        scroll_canvas = tk.Canvas(self.root, highlightthickness=0, bd=0, bg="#0f0e17")
        scroll_canvas.place(x=0, y=scroll_area_top, width=self.sw, height=scroll_area_height)

        # 内部容器Frame（背景与主界面一致，让半透明遮罩生效）
        inner_frame = tk.Frame(scroll_canvas, bg="#0f0e17")

        # 滚动条（设置为半透明外观）
        scrollbar = tk.Scrollbar(self.root, orient="vertical", command=scroll_canvas.yview,
                                troughcolor="#000000", bg="#1a1a2e")
        scrollbar.place(x=self.sw - 20, y=scroll_area_top, height=scroll_area_height)

        # 配置滚动
        scroll_canvas.configure(yscrollcommand=scrollbar.set)
        scroll_canvas.create_window((0, 0), window=inner_frame, anchor="nw", tags="inner_frame")

        # 按章节分组展示成就
        achievements = self.achievements_config.get("achievements", [])
        chapters = ["chapter1", "chapter2", "chapter3", "chapter4", "all"]
        chapter_names = {
            "chapter1": "第一章：深渊之恋",
            "chapter2": "第二章：赌局陷阱",
            "chapter3": "第三章：校园贷危机",
            "chapter4": "第四章：求职陷阱",
            "all": "特殊成就"
        }

        CARDS_PER_ROW = 4
        CARD_WIDTH = int(self.sw * 0.20)
        CARD_HEIGHT = int(self.sh * 0.11)
        GAP_X = int(self.sw * 0.02)
        GAP_Y = int(self.sh * 0.02)
        SECTION_GAP = int(self.sh * 0.03)

        for chapter in chapters:
            chapter_achievements = [a for a in achievements if a.get("chapter") == chapter]
            if not chapter_achievements:
                continue

            # 显示章节标题
            tk.Label(inner_frame, text=chapter_names.get(chapter, chapter),
                     bg="#0f0e17", fg="#ff8906",
                     font=("微软雅黑", 16, "bold")).pack(pady=(15, 5))

            num_cards = len(chapter_achievements)

            # 创建卡片容器（背景与主界面一致）
            cards_frame = tk.Frame(inner_frame, bg="#0f0e17")
            cards_frame.pack(fill=tk.X, pady=(0, SECTION_GAP))

            for idx, achievement in enumerate(chapter_achievements):
                achievement_id = achievement.get("id")
                is_unlocked = self.state_manager.is_achievement_unlocked(achievement_id)

                # 成就卡片背景色
                if is_unlocked:
                    category = achievement.get("category", "normal")
                    if category == "bad":
                        bg_color = "#5d2929"
                        border_color = "#ff6b6b"
                    elif category == "good":
                        bg_color = "#2d5a27"
                        border_color = "#2ed573"
                    elif category == "perfect":
                        bg_color = "#5a4a1a"
                        border_color = "#ffd700"
                    elif category == "special":
                        bg_color = "#4a3a6a"
                        border_color = "#a855f7"
                    else:
                        bg_color = "#2d3436"
                        border_color = "#636e72"
                    text_color = "#ffffff"
                else:
                    bg_color = "#2a2a3e"  # 较浅的深色背景
                    border_color = "#4a4a5e"
                    text_color = "#666666"

                # 创建成就卡片
                card_frame = tk.Frame(cards_frame, bg=border_color, bd=2, relief="solid")
                card_frame.pack_propagate(False)
                card_frame.configure(width=CARD_WIDTH, height=CARD_HEIGHT)

                card_content = tk.Frame(card_frame, bg=bg_color)
                card_content.pack(fill=tk.BOTH, expand=True, padx=3, pady=3)

                icon_text = achievement.get("icon", "") if is_unlocked else ""
                icon_label = tk.Label(card_content, text=icon_text, font=("微软雅黑", 24),
                                      bg=bg_color, fg=text_color)
                icon_label.pack(side=tk.LEFT, padx=8)

                info_frame = tk.Frame(card_content, bg=bg_color)
                info_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

                name_label = tk.Label(info_frame, text=achievement.get("name", "未知成就"),
                                      font=("微软雅黑", 10, "bold"),
                                      bg=bg_color, fg=text_color, anchor="w")
                name_label.pack(fill=tk.X, pady=(5, 2))

                desc_label = tk.Label(info_frame, text=achievement.get("description", ""),
                                      font=("微软雅黑", 8),
                                      bg=bg_color, fg=text_color, anchor="w", wraplength=CARD_WIDTH - 80,
                                      justify="left")
                desc_label.pack(fill=tk.X)

                # 布局卡片（每4个一行）
                col = idx % CARDS_PER_ROW
                card_frame.grid(row=idx // CARDS_PER_ROW, column=col, padx=(GAP_X if col > 0 else 0), pady=GAP_Y,
                                sticky="ew")

            # 更新卡片容器的网格列权重
            for i in range(CARDS_PER_ROW):
                cards_frame.grid_columnconfigure(i, weight=1)

        # 更新滚动区域
        inner_frame.update_idletasks()
        scroll_canvas.configure(scrollregion=scroll_canvas.bbox("all"))

        # 鼠标滚轮事件
        def _on_mousewheel(event):
            scroll_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

        scroll_canvas.bind_all("<MouseWheel>", _on_mousewheel)

    def render_frame(self):
        self.clear_all_widgets()
        self.canvas.delete("all")
        self.effects_manager.clear_all()

        if self.idx == -1 or self.idx >= len(self.script):
            self.render_menu()
            return

        node = self.script[self.idx]

        # 处理隐藏线索
        if "hidden_clue" in node:
            clue_id = node["hidden_clue"]
            if self.state_manager.add_clue(clue_id):
                self.effects_manager.create_clue_particles(self.sw // 2, self.sh // 2)

        # 处理信任值和怀疑值变化（兼容顶层字段与 effect 子对象两种写法）
        node_effect = node.get("effect", {}) or {}

        def _node_get(key):
            if key in node:
                return node[key]
            return node_effect.get(key)

        # 处理金钱变化
        money = _node_get("set_money")
        if money:
            self.state_manager.add_money(money)
            if money < 0:
                self.effects_manager.create_alert_particles(self.sw // 2, self.sh // 2)

        trust = _node_get("trust")
        if trust:
            self.update_trust_with_animation(trust)

        suspicion = _node_get("suspicion")
        if suspicion:
            self.update_suspicion_with_animation(suspicion)

        flag = _node_get("set_flag")
        if flag:
            self.state_manager.add_flag(flag)

        if node.get("type") == "ending":
            self.state_manager.current_ending = node.get("ending_id")
            self.render_ending(node)
            return

        bg_key = node.get("bg", "index")
        self.canvas.create_image(0, 0, image=self.images[bg_key], anchor="nw")

        if bg_key == "pg1":
            self.effects_manager.create_floating_particles(count=20, color="#ffffff")
            self.effects_manager.draw_light_ray(self.sw * 0.3, self.sh * 0.1, intensity=0.15)
            self.effects_manager.draw_light_ray(self.sw * 0.7, self.sh * 0.15, intensity=0.12)
        elif bg_key == "pg2":
            self.effects_manager.create_floating_particles(count=25, color="#ffff99")

        self.render_control_bar()

        if node.get("type") == "choice":
            # 选择框：取消自动播放，等待用户选择
            if self.auto_play_id:
                self.root.after_cancel(self.auto_play_id)
                self.auto_play_id = None

            # 添加渐变背景遮罩，让选择更突出
            self.canvas.create_rectangle(0, 0, self.sw, self.sh, fill="#0f0e17", stipple="gray50")

            # 显示选择提示图标
            self.canvas.create_text(self.sw / 2, self.sh * 0.08, text="🤔 请做出选择", fill="#ff8906",
                                    font=("微软雅黑", 20, "bold"))

            # 显示问题文本（带精美边框和背景）
            self.canvas.create_rectangle(self.sw * 0.08, self.sh * 0.12, self.sw * 0.92, self.sh * 0.30,
                                         fill="#1a1a2e", outline="#ff8906", width=4)
            # 添加上下装饰线
            self.canvas.create_line(self.sw * 0.12, self.sh * 0.15, self.sw * 0.88, self.sh * 0.15,
                                    fill="#ff8906", width=2)
            self.canvas.create_line(self.sw * 0.12, self.sh * 0.27, self.sw * 0.88, self.sh * 0.27,
                                    fill="#ff8906", width=2)

            self.canvas.create_text(self.sw / 2, self.sh * 0.21, text=node["content"], fill="#ffffff",
                                    font=("微软雅黑", 28, "bold"), width=self.sw - 200, justify="center")

            # 渲染选项按钮（美化版本）
            valid_options = []
            for opt in node["options"]:
                # 检查条件（如果有）
                if "condition" in opt:
                    cond = opt["condition"]
                    if "trust_min" in cond and self.state_manager.trust_value < cond["trust_min"]:
                        continue
                    if "suspicion_min" in cond and self.state_manager.suspicion_value < cond["suspicion_min"]:
                        continue
                    if "flag" in cond and not self.state_manager.has_flag(cond["flag"]):
                        continue
                    if "flag_not" in cond and self.state_manager.has_flag(cond["flag_not"]):
                        continue
                valid_options.append(opt)

            option_count = len(valid_options)

            for i, opt in enumerate(valid_options):
                btn_w = int(self.sw * 0.55)

                # 创建按钮容器（模拟渐变边框效果）
                btn_frame = tk.Frame(self.root, bg="#ff8906", bd=0)

                # 选项序号标签
                option_num = chr(65 + i)  # A, B, C, D...
                num_label = tk.Label(btn_frame, text=f"{option_num}", font=("Arial Black", 24, "bold"),
                                     bg="#ff8906", fg="#1a1a2e", padx=15, pady=10)
                num_label.pack(side="left", fill="y")

                # 创建按钮本身
                btn = tk.Label(btn_frame, text=opt["text"], font=("微软雅黑", 22, "bold"),
                               bg="#2d3436", fg="#ffffff",
                               padx=25, pady=22, wraplength=btn_w - 120,
                               justify="left", cursor="hand2",
                               bd=0, relief="flat")

                # 按钮悬停效果 - 使用工厂函数解决闭包问题
                def create_hover_handlers(button, frame, num_lbl):
                    def on_enter(event):
                        button.config(bg="#ff8906", fg="#0a192f")
                        frame.config(bg="#ffa500")
                        num_lbl.config(bg="#ffa500", fg="#ffffff")

                    def on_leave(event):
                        button.config(bg="#2d3436", fg="#ffffff")
                        frame.config(bg="#ff8906")
                        num_lbl.config(bg="#ff8906", fg="#1a1a2e")

                    return on_enter, on_leave

                enter_handler, leave_handler = create_hover_handlers(btn, btn_frame, num_label)

                btn.bind("<Button-1>", lambda e, o=opt: self.go_to(o["next"], o))
                btn.bind("<Enter>", enter_handler)
                btn.bind("<Leave>", leave_handler)

                btn.pack(side="left", fill="both", expand=True)

                # 计算选项位置，均匀分布（从下往上）
                start_y = self.sh * 0.85
                spacing = (self.sh * 0.5) / (option_count + 1)
                y_pos = start_y - (i + 1) * spacing

                self.canvas.create_window(self.sw / 2, y_pos, window=btn_frame, width=btn_w)

            # 底部提示
            self.canvas.create_text(self.sw / 2, self.sh * 0.93,
                                    text="💡 你的选择将影响故事走向", fill="#71717a",
                                    font=("微软雅黑", 16))
        else:
            # 处理特殊节点（如只有 hidden_clue 的节点）
            if "jump" in node:
                self.idx = node["jump"]
                self.render_frame()
                return
            
            # 跳过没有 content 的节点，直接到下一个
            if "content" not in node:
                self.idx += 1
                if self.idx < len(self.script):
                    self.render_frame()
                else:
                    self.render_menu()
                return
            
            # 显示人物立绘
            self.render_character(node)

            # 对话框：创建对话框遮罩
            m, h = 80, 250
            self.canvas.create_rectangle(m, self.sh - h - m, self.sw - m, self.sh - m, fill="black", stipple="gray75",
                                         outline="#ff8906", width=2)
            name = node.get("role", "旁白")
            name_color = "#ff8906" if name != "旁白" else "#71717a"
            self.canvas.create_text(m + 50, self.sh - h - 15, text=f"【{name}】", fill=name_color,
                                    font=("微软雅黑", 22, "bold"), anchor="nw")

            self.typing_text = node["content"]
            self.typing_index = 0

            self.content_text_id = self.canvas.create_text(m + 50, self.sh - h + 60, text="", fill="white",
                                                           font=("微软雅黑", 20), anchor="nw", width=self.sw - 250)
            self.cursor_text_id = self.canvas.create_text(m + 50, self.sh - h + 60, text="|", fill="#ff8906",
                                                          font=("微软雅黑", 20), anchor="nw")

            self.start_typing()

    def render_status_bars(self):
        """渲染信任值和怀疑值状态条（仅显示变化动画）"""
        # 不再直接显示状态条，改为在变化时显示动画效果
        pass

    def show_status_change_animation(self, status_type, change_value):
        """显示状态变化动画
        
        Args:
            status_type: 'trust' 或 'suspicion'
            change_value: 变化值（正数为上升，负数为下降）
        """
        # 计算显示位置（屏幕中央偏上）
        center_x = self.sw // 2
        center_y = self.sh * 0.35
        
        # 根据类型和变化值确定颜色和图标
        if status_type == "trust":
            icon = "❤️"
            color = "#2ed573" if change_value > 0 else "#ff4757"
            text_prefix = "信任"
        else:  # suspicion
            icon = "🔍"
            color = "#ff4757" if change_value > 0 else "#2ed573"
            text_prefix = "怀疑"
        
        # 构建提示文本
        if change_value > 0:
            change_text = f"+{change_value}"
            arrow = "↑"
        else:
            change_text = str(change_value)
            arrow = "↓"
        
        display_text = f"{icon} {text_prefix} {arrow} {change_text}"
        
        # 创建动画文本
        anim_label = tk.Label(self.root, text=display_text, 
                             font=("微软雅黑", 36, "bold"),
                             fg=color, bg="#1a1a2e",
                             padx=30, pady=15,
                             bd=3, relief="raised")
        
        # 将标签放在画布上
        self.canvas.create_window(center_x, center_y, window=anim_label, tags="status_anim")
        
        # 添加光晕效果
        glow_radius = 150
        for i in range(3):
            alpha = 0.3 - i * 0.1
            self.canvas.create_oval(
                center_x - glow_radius - i*20, center_y - glow_radius - i*20,
                center_x + glow_radius + i*20, center_y + glow_radius + i*20,
                outline=color, width=3, stipple=["gray75", "gray50", "gray25"][i],
                tags="status_anim"
            )
        
        # 创建粒子效果
        self.effects_manager.create_floating_particles(count=15, color=color)
        
        # 2秒后淡出并删除
        def fade_out():
            try:
                anim_label.destroy()
                self.canvas.delete("status_anim")
            except:
                pass
        
        self.root.after(2000, fade_out)

    def update_trust_with_animation(self, value):
        """更新信任值并显示动画"""
        old_value = self.state_manager.trust_value
        self.state_manager.update_trust(value)
        change = self.state_manager.trust_value - old_value
        if change != 0:
            self.show_status_change_animation("trust", change)

    def update_suspicion_with_animation(self, value):
        """更新怀疑值并显示动画"""
        old_value = self.state_manager.suspicion_value
        self.state_manager.update_suspicion(value)
        change = self.state_manager.suspicion_value - old_value
        if change != 0:
            self.show_status_change_animation("suspicion", change)

    def render_character(self, node):
        """根据角色渲染人物立绘（支持等比例缩放、多形象切换和多角色叠加）"""
        role = node.get("role", "")
        bg_key = node.get("bg", "index")

        # 优先使用 show_characters 字段（支持多角色叠加显示）
        if "show_characters" in node and node["show_characters"]:
            self._render_multiple_characters(node["show_characters"])
            return

        # 兼容旧逻辑：根据 role 字段显示单个人物
        if role == "林舒学姐":
            char_key = self.get_linshu_character(bg_key)
            x_pos = self.sw * 0.12
        elif role in ["林警官", "神秘声音"]:
            char_key = self.role_to_character.get(role)
            x_pos = self.sw * 0.12
        elif role in ["民警"]:
            char_key = self.role_to_character.get(role)
            x_pos = self.sw * 0.78
        elif role in ["周学长"]:
            char_key = self.role_to_character.get(role)
            x_pos = self.sw * 0.78
        elif role in ["辅导员"]:
            char_key = self.role_to_character.get(role)
            x_pos = self.sw * 0.78
        elif role in ["室友A", "同学"]:
            char_key = self.role_to_character.get(role)
            x_pos = self.sw * 0.12
        elif role in ["室友B", "生科院学生"]:
            char_key = self.role_to_character.get(role)
            x_pos = self.sw * 0.78
        else:
            return

        if char_key and char_key in self.characters:
            char_img = self.characters[char_key]
            info = self.character_info.get(char_key, {"width": int(self.sw * 0.2), "height": int(self.sh * 0.42)})
            char_height = info["height"]

            dialog_top = self.sh - 250 - 80
            y_pos = dialog_top - 60

            self.canvas.create_image(x_pos, y_pos, image=char_img, anchor="sw")

    def _render_multiple_characters(self, char_list):
        """渲染多个角色叠加显示
        
        Args:
            char_list: 角色key列表，如 ["xiaxia", "laodan", "xiaogao"]
        """
        if not char_list:
            return

        dialog_top = self.sh - 250 - 80
        y_pos = dialog_top - 60
        
        # 角色位置策略：根据角色数量动态分配位置
        char_count = len(char_list)
        
        # 定义位置权重（屏幕百分比，从左到右分布）
        # 单角色：居中偏左
        # 双角色：左右分布
        # 三角色：左、中、右分布
        
        if char_count == 1:
            positions = [0.25]  # 单角色靠左
        elif char_count == 2:
            positions = [0.15, 0.45]  # 两个角色左右分布
        elif char_count == 3:
            positions = [0.08, 0.30, 0.52]  # 三个角色从左到右
        else:
            # 超过3个角色，平均分布
            spacing = 0.35 / (char_count - 1)
            positions = [0.08 + i * spacing for i in range(char_count)]
        
        # 角色名字映射
        self.char_name_map = {
            "xiaxia": "小夏",
            "laodan": "老蛋",
            "xiaogao": "小高",
            "fudaoyuan": "辅导员",
            "security_teacher": "保卫处老师"
        }
        
        # 渲染每个角色
        for i, char_key in enumerate(char_list):
            if char_key and char_key in self.characters:
                char_img = self.characters[char_key]
                info = self.character_info.get(char_key, {"width": int(self.sw * 0.2), "height": int(self.sh * 0.42)})
                
                # 缩放高度（后面的角色稍微小一点，增加层次感）
                scale_factor = 1.0 - (i * 0.05) if i > 0 else 1.0
                char_height = int(info["height"] * scale_factor)
                char_width = int(info["width"] * scale_factor)
                
                x_pos = self.sw * positions[i]
                self.canvas.create_image(x_pos, y_pos, image=char_img, anchor="sw")
                
                # 添加人物名字标注
                char_name = self.char_name_map.get(char_key, char_key)
                name_y = y_pos + 20
                # 名字背景
                name_width = len(char_name) * 30 + 20
                self.canvas.create_rectangle(
                    x_pos - name_width//2, name_y,
                    x_pos + name_width//2, name_y + 35,
                    fill="#1a1a2e", outline="#ff8906", width=2
                )
                # 名字文字
                self.canvas.create_text(x_pos, name_y + 18, text=char_name,
                                      fill="#ffffff", font=("微软雅黑", 18, "bold"),
                                      anchor="center")

    def get_linshu_character(self, bg_key):
        """根据场景选择林舒学姐的不同形象"""
        if bg_key == "pg6":
            return "linshu3"
        elif bg_key == "pg3":
            return "linshu2"
        elif bg_key == "pg2":
            self.linshu_index = (self.linshu_index + 1) % 3
            return self.linshu_images[self.linshu_index]
        else:
            self.linshu_index = (self.linshu_index + 1) % len(self.linshu_images)
            return self.linshu_images[self.linshu_index]

    def render_ending(self, ending_node):
        """渲染结局画面"""
        self.clear_all_widgets()
        self.canvas.delete("all")
        self.effects_manager.clear_all()
        if self.auto_play_id:
            self.root.after_cancel(self.auto_play_id)
            self.auto_play_id = None
        self.auto_play = False

        # 解锁对应成就
        ending_id = ending_node.get("ending_id")
        achievement_unlocked = False
        if ending_id and self.current_chapter:
            achievement_id = f"{self.current_chapter}_{ending_id}"
            if self.state_manager.unlock_achievement(achievement_id):
                achievement_unlocked = True
                # 检查是否解锁了所有结局成就
                self._check_all_achievements()

        # 只有好结局才能解锁下一章节
        ending_type = ending_node.get("ending_type", "normal")
        if ending_type in ["good", "best", "hidden", "perfect"]:
            self.unlock_next_chapter()
            chapter_unlocked = True
        else:
            chapter_unlocked = False

        bg_key = ending_node.get("bg", "index")
        self.canvas.create_image(0, 0, image=self.images[bg_key], anchor="nw")

        self.canvas.create_rectangle(0, 0, self.sw, self.sh, fill="black", stipple="gray75")

        if ending_type == "bad":
            title_color = "#ff4757"
            self.effects_manager.create_alert_particles(self.sw // 2, self.sh // 2)
        elif ending_type == "good":
            title_color = "#2ed573"
            self.effects_manager.create_success_particles(self.sw // 2, self.sh // 2)
        elif ending_type == "best":
            title_color = "#2ed573"
            self.effects_manager.create_success_particles(self.sw // 2, self.sh // 2)
            self.effects_manager.draw_light_ray(self.sw // 2, self.sh // 3, intensity=0.4)
        elif ending_type == "hidden":
            title_color = "#ffd700"
            self.effects_manager.create_gold_particles(self.sw // 2, self.sh // 2)
            self.effects_manager.draw_light_ray(self.sw // 2, self.sh // 3, intensity=0.5)
        elif ending_type == "perfect":
            title_color = "#ffd700"
            self.effects_manager.create_gold_particles(self.sw // 2, self.sh // 2)
            self.effects_manager.draw_light_ray(self.sw // 2, self.sh // 3, intensity=0.5)
        else:
            title_color = "#ff8906"
            self.effects_manager.create_particles(self.sw // 2, self.sh // 2)

        # 结局标题
        self.canvas.create_text(self.sw / 2, self.sh * 0.25, text=ending_node.get("ending_name", "结局"),
                                fill=title_color, font=("黑体", 60, "bold"))

        # 结局内容
        content = ending_node.get("content", "")
        self.canvas.create_text(self.sw / 2, self.sh * 0.5, text=content, fill="white",
                                font=("微软雅黑", 20), width=self.sw - 200, justify="center")

        # 显示成就解锁提示
        if achievement_unlocked:
            self.canvas.create_text(self.sw / 2, self.sh * 0.68,
                                    text="🏆 成就解锁！",
                                    fill="#ffd700", font=("微软雅黑", 24, "bold"))
            # 添加金色粒子效果
            self.effects_manager.create_gold_particles(self.sw // 2, self.sh * 0.68)

        # 显示统计信息
        stats_y = self.sh * 0.73 if achievement_unlocked else self.sh * 0.68
        if self.state_manager.money_lost > 0:
            self.canvas.create_text(self.sw / 2, stats_y,
                                    text=f"💰 累计损失: {self.state_manager.money_lost}元",
                                    fill="#ff4757", font=("微软雅黑", 18))
            stats_y += 0.05 * self.sh

        if self.state_manager.clues_collected:
            self.canvas.create_text(self.sw / 2, stats_y,
                                    text=f"🔍 收集线索: {len(self.state_manager.clues_collected)}条",
                                    fill="#ffd700", font=("微软雅黑", 18))
            stats_y += 0.05 * self.sh

        # 检查是否解锁了新章节
        new_chapter_unlocked = False
        chapters = self.chapter_manager.chapters
        for chapter in chapters:
            if chapter["id"] != self.current_chapter and chapter["unlocked"]:
                current_idx = None
                unlock_idx = None
                for i, c in enumerate(chapters):
                    if c["id"] == self.current_chapter:
                        current_idx = i
                    if c["id"] == chapter["id"]:
                        unlock_idx = i
                if current_idx is not None and unlock_idx == current_idx + 1:
                    new_chapter_unlocked = True
                    break

        if new_chapter_unlocked:
            self.canvas.create_text(self.sw / 2, self.sh * 0.75,
                                    text="🎉 恭喜！新章节已解锁！",
                                    fill="#ffd700", font=("微软雅黑", 24, "bold"))
        elif not chapter_unlocked:
            self.canvas.create_text(self.sw / 2, self.sh * 0.75,
                                    text="⚠️ 达成好结局才能解锁下一章\n（good/perfect/best/hidden结局）",
                                    fill="#ff8906", font=("微软雅黑", 18))

        # 返回菜单按钮
        btn_w = 300
        btn = tk.Label(self.root, text="返回主菜单", font=("微软雅黑", 18), bg="#2d3436", fg="white",
                       padx=30, pady=15, cursor="hand2")
        btn.bind("<Button-1>", lambda e: self.reset_and_return_menu())
        btn.bind("<Enter>", lambda e: btn.config(bg="#ff8906"))
        btn.bind("<Leave>", lambda e: btn.config(bg="#2d3436"))
        self.canvas.create_window(self.sw / 2, self.sh * 0.88, window=btn, width=btn_w)

    def reset_and_return_menu(self):
        """重置游戏状态并返回菜单"""
        self.state_manager.reset()
        # 清空选择历史
        self.choice_history = []
        self.render_menu()

    def start_typing(self):
        if self.typing_id:
            self.root.after_cancel(self.typing_id)

        self.typing_index = 0
        self.typing()

    def typing(self):
        if self.typing_index < len(self.typing_text):
            self.typing_index += 1
            current_text = self.typing_text[:self.typing_index]
            self.canvas.itemconfig(self.content_text_id, text=current_text)
            self.canvas.coords(self.cursor_text_id,
                               self.canvas.bbox(self.content_text_id)[2],
                               self.canvas.bbox(self.content_text_id)[1])
            self.typing_id = self.root.after(self.typing_speed, self.typing)
        else:
            self.canvas.delete(self.cursor_text_id)
            m = 80
            self.canvas.create_text(self.sw - 180, self.sh - 120, text="▼ 点击继续", fill="#71717a",
                                    font=("微软雅黑", 14))

    def render_control_bar(self):
        """渲染右上角控制栏（极简版）"""
        # 按钮配置
        buttons = [
            ("⏩", "快进到下一选项", lambda: self.fast_forward_to_next_choice()),
            ("▶" if not self.auto_play else "⏸", "自动播放", lambda: self.toggle_auto_play()),
            ("⏪", "快退到上一选项", lambda: self.fast_backward_to_previous_choice()),
            ("💾", "保存进度", lambda: self.save_game()),
            ("⚙", "游戏设置", lambda: self.show_settings_popup()),
        ]

        # 按钮位置（右上角）
        start_x = self.sw - 30
        start_y = 20
        spacing = 38

        for i, (text, tip, cmd) in enumerate(buttons):
            btn = tk.Label(self.root, text=text, font=("微软雅黑", 12),
                           bg="#2d3436", fg="white", padx=6, pady=3,
                           cursor="hand2")
            btn.bind("<Button-1>", lambda e, c=cmd: c())
            btn.bind("<Enter>", lambda e, b=btn, t=tip: [b.config(bg="#444"), self.show_tooltip(t)])
            btn.bind("<Leave>", lambda e, b=btn: [b.config(bg="#2d3436"), self.hide_tooltip()])
            self.canvas.create_window(start_x - i * spacing, start_y, window=btn)

    def show_tooltip(self, text):
        """显示提示"""
        if hasattr(self, 'tooltip'):
            self.tooltip.destroy()
        self.tooltip = tk.Label(self.root, text=text, font=("微软雅黑", 10),
                                bg="#ffffe0", fg="#333", padx=8, pady=4)
        self.tooltip.place(x=self.sw - 120, y=50)

    def hide_tooltip(self):
        """隐藏提示"""
        if hasattr(self, 'tooltip'):
            self.tooltip.destroy()
            delattr(self, 'tooltip')

    def start_game(self):
        # 重置游戏状态
        self.state_manager.reset()
        self.auto_play = False
        if self.auto_play_id:
            self.root.after_cancel(self.auto_play_id)
            self.auto_play_id = None
        self.idx = 0
        # 清空选择历史
        self.choice_history = []
        self.render_frame()

    def next_scene(self, event):
        if self.idx < 0: return
        node = self.script[self.idx]
        if node.get("type") == "ending":
            return
        if node.get("type") != "choice":
            if self.typing_id and self.typing_index < len(self.typing_text):
                self.skip_typing()
                # 自动播放模式下，打字完成或跳过时自动继续
                if self.auto_play:
                    self.schedule_auto_play()
            else:
                if "jump" in node:
                    self.idx = node["jump"]
                else:
                    self.idx += 1
                self.render_frame()
                # 非选择节点自动播放
                if self.auto_play:
                    self.schedule_auto_play()

    def schedule_auto_play(self):
        """安排自动播放"""
        if self.auto_play_id:
            self.root.after_cancel(self.auto_play_id)
        self.auto_play_id = self.root.after(self.auto_play_delay, self.auto_continue)

    def auto_continue(self):
        """自动继续下一个场景"""
        if not self.auto_play:
            return
        node = self.script[self.idx]
        # 如果是选择节点或结局，停止自动播放
        if node.get("type") == "choice" or node.get("type") == "ending":
            return
        # 模拟点击继续
        if self.typing_id and self.typing_index < len(self.typing_text):
            self.skip_typing()
            self.schedule_auto_play()
        else:
            if "jump" in node:
                self.idx = node["jump"]
            else:
                self.idx += 1
            self.render_frame()
            # 继续检查下一个节点
            if self.auto_play and self.idx < len(self.script):
                next_node = self.script[self.idx]
                if next_node.get("type") == "choice" or next_node.get("type") == "ending":
                    return
                self.schedule_auto_play()

    def toggle_auto_play(self):
        """切换自动播放状态"""
        self.auto_play = not self.auto_play
        if self.auto_play:
            # 开始自动播放，先检查当前节点
            node = self.script[self.idx]
            if node.get("type") == "choice" or node.get("type") == "ending":
                # 如果当前是选择或结局，不自动继续，等待用户选择
                pass
            elif self.typing_id and self.typing_index < len(self.typing_text):
                # 如果正在打字，跳过并继续
                self.skip_typing()
                self.schedule_auto_play()
            else:
                self.schedule_auto_play()
        else:
            # 停止自动播放
            if self.auto_play_id:
                self.root.after_cancel(self.auto_play_id)
                self.auto_play_id = None
        # 更新控制栏显示
        self.render_frame()

    def skip_typing(self):
        if self.typing_id:
            self.root.after_cancel(self.typing_id)
            self.typing_id = None

        self.canvas.itemconfig(self.content_text_id, text=self.typing_text)
        self.canvas.delete(self.cursor_text_id)
        m = 80
        self.canvas.create_text(self.sw - 180, self.sh - 120, text="▼ 点击继续", fill="#71717a",
                                font=("微软雅黑", 14))

    def fast_forward_to_next_choice(self):
        """快进到下一个选项节点"""
        if self.idx < 0 or self.idx >= len(self.script):
            return

        node = self.script[self.idx]
        if node.get("type") == "choice" or node.get("type") == "ending":
            messagebox.showinfo("提示", "当前已经是选择节点或结局，无法继续快进")
            return

        if self.typing_id:
            self.root.after_cancel(self.typing_id)
            self.typing_id = None

        visited = set()
        max_iterations = len(self.script) * 2
        found_choice = False

        while self.idx < len(self.script):
            if self.idx in visited:
                break
            visited.add(self.idx)

            if max_iterations <= 0:
                break
            max_iterations -= 1

            if "jump" in node:
                self.idx = node["jump"]
            else:
                self.idx += 1

            if self.idx >= len(self.script):
                break

            node = self.script[self.idx]

            if node.get("type") == "choice" or node.get("type") == "ending":
                found_choice = True
                break

        if not found_choice:
            messagebox.showinfo("提示", "已到达剧本末尾，没有更多选项节点")
            self.idx = len(self.script) - 1

        self.render_frame()

    def fast_backward_to_previous_choice(self):
        """快退到上一个选项节点（优先使用历史记录，没有则向前搜索）"""
        if self.idx <= 0 or self.idx >= len(self.script):
            messagebox.showinfo("提示", "已到达剧本开头，无法继续回退")
            return

        if self.typing_id:
            self.root.after_cancel(self.typing_id)
            self.typing_id = None
        
        # 策略1: 优先使用历史记录（更准确）
        if len(self.choice_history) > 0:
            previous_choice_idx = self.choice_history.pop()
            print(f"⏪ 使用历史记录回退到节点: {previous_choice_idx}")
            self.idx = previous_choice_idx
            self.render_frame()
            return
        
        # 策略2: 如果没有历史记录，则向前搜索选择节点（备用方案）
        print(f"⏪ 历史记录为空，使用向前搜索，从节点 {self.idx} 开始")
        found_choice = False
        temp_idx = self.idx - 1

        while temp_idx >= 0:
            node = self.script[temp_idx]
            if node.get("type") == "choice":
                self.idx = temp_idx
                found_choice = True
                print(f"⏪ 搜索到选择节点: {temp_idx}")
                break
            temp_idx -= 1

        if found_choice:
            self.render_frame()
        else:
            messagebox.showinfo("提示", "前面没有更多选项节点了")

    def go_to(self, target, option=None):
        """跳转到指定节点"""
        # 边界检查
        if target < 0 or target >= len(self.script):
            print(f"❌ 错误：跳转索引 {target} 超出范围 (0-{len(self.script)-1})")
            messagebox.showerror("错误", f"剧情节点索引错误：{target}\n请联系开发者修复")
            return
        
        # 检查目标节点是否存在
        if target >= len(self.script):
            print(f"❌ 错误：目标节点 {target} 不存在")
            return
        
        # 如果有 option，说明是用户做了选择，记录当前选择节点位置用于回退
        if option:
            self.choice_history.append(self.idx)
            print(f"📝 记录选择历史: 当前节点 {self.idx}")
        
        target_node = self.script[target]
        print(f"✅ 跳转到节点 {target}: {target_node.get('role', 'N/A')} - {target_node.get('content', 'N/A')[:30]}...")
        
        # 处理选项的效果
        if option:
            # 兼容两种写法：顶层字段 与 effect 子对象（chapter1 使用的是 effect 写法）
            effect = option.get("effect", {}) or {}

            def _get(key):
                if key in option:
                    return option[key]
                return effect.get(key)

            # 处理标记
            flag = _get("set_flag")
            if flag:
                self.state_manager.add_flag(flag)

            # 处理金钱
            money = _get("set_money")
            if money:
                self.state_manager.add_money(money)
                if money < 0:
                    self.effects_manager.create_alert_particles(self.sw // 2, self.sh // 2)

            # 处理信任值
            trust = _get("trust")
            if trust:
                self.update_trust_with_animation(trust)

            # 处理怀疑值
            suspicion = _get("suspicion")
            if suspicion:
                self.update_suspicion_with_animation(suspicion)

        self.idx = target
        self.render_frame()

        # 选择后如果自动播放开启，继续自动播放
        if self.auto_play:
            self.schedule_auto_play()

    def confirm_to_menu(self):
        if messagebox.askyesno("提示", "确定要返回主菜单吗？"):
            self.render_menu()

    def show_settings_popup(self):
        """显示设置弹窗，带半透明遮罩"""
        # 创建半透明遮罩层（使用canvas绘制半透明黑色）
        self.popup_canvas = tk.Canvas(self.root, width=self.sw, height=self.sh, highlightthickness=0)
        self.popup_canvas.place(x=0, y=0)
        self.popup_canvas.create_rectangle(0, 0, self.sw, self.sh, fill="#000000", stipple="gray25")

        # 弹窗容器
        popup_w, popup_h = 400, 420
        popup_x = (self.sw - popup_w) // 2
        popup_y = (self.sh - popup_h) // 2

        self.popup_frame = tk.Frame(self.root, bg="#2d3436", width=popup_w, height=popup_h, bd=2, relief="solid")
        self.popup_frame.place(x=popup_x, y=popup_y)

        # 弹窗标题
        title_label = tk.Label(self.popup_frame, text="⚙️ 设置", font=("黑体", 28, "bold"),
                               bg="#2d3436", fg="#ff8906", width=15, pady=20)
        title_label.place(x=0, y=20, width=popup_w)

        # 按钮配置
        btn_configs = [
            ("⚙️ 游戏设置", self.open_game_settings),
            ("🏠 返回主页", self.goto_menu_from_popup),
            ("▶️ 返回游戏", self.close_settings_popup),
            ("🚪 退出游戏", self.quit_game)
        ]

        for i, (text, cmd) in enumerate(btn_configs):
            btn = tk.Label(self.popup_frame, text=text, font=("微软雅黑", 18), bg="#444", fg="white",
                           padx=30, pady=15, cursor="hand2", width=18)
            btn.bind("<Button-1>", lambda e, c=cmd: c())
            btn.bind("<Enter>", lambda e, b=btn: b.config(bg="#ff8906"))
            btn.bind("<Leave>", lambda e, b=btn: b.config(bg="#444"))
            btn.place(x=75, y=100 + i * 70, width=250)

    def close_settings_popup(self):
        """关闭设置弹窗"""
        if hasattr(self, 'popup_frame'):
            self.popup_frame.destroy()
            del self.popup_frame
        if hasattr(self, 'popup_canvas'):
            self.popup_canvas.destroy()
            del self.popup_canvas

    def goto_menu_from_popup(self):
        """从弹窗返回主页"""
        self.close_settings_popup()
        self.render_menu()

    def open_game_settings(self):
        """打开游戏内设置界面"""
        self.close_settings_popup()
        self.render_settings(return_to_game=True)

    def render_settings(self, return_to_game=False):
        """渲染设置界面

        Args:
            return_to_game: 是否显示"返回游戏"按钮（True=从游戏内进入，False=从主页进入）
        """
        self.clear_all_widgets()
        self.canvas.delete("all")
        self.effects_manager.clear_all()

        self.canvas.create_rectangle(0, 0, self.sw, self.sh, fill="#0f0e17", stipple="gray50")

        self.effects_manager.create_floating_particles(count=15, color="#00d4ff")

        # 标题
        self.canvas.create_text(self.sw / 2, self.sh * 0.15, text="游戏设置", fill="#ff8906",
                                font=("黑体", 60, "bold"))

        # BGM音量设置
        self.canvas.create_text(self.sw / 2 - 230, self.sh * 0.35, text="BGM音量", fill="white",
                                font=("微软雅黑", 24), anchor="e")

        # 音量滑块
        self.volume_var = tk.DoubleVar(value=self.audio_manager.get_volume() * 100)
        volume_slider = tk.Scale(self.root, from_=0, to=100, orient=tk.HORIZONTAL,
                                 length=400, variable=self.volume_var,
                                 command=self.on_volume_change,
                                 bg="#2d3436", fg="white", highlightthickness=0,
                                 troughcolor="#555", activebackground="#ff8906",
                                 font=("微软雅黑", 14))
        self.canvas.create_window(self.sw / 2 + 40, self.sh * 0.35, window=volume_slider)

        # 音量数值显示
        self.volume_label = tk.Label(self.root, text=f"{int(self.audio_manager.get_volume() * 100)}%",
                                     font=("微软雅黑", 20), bg="#2d3436", fg="white")
        self.canvas.create_window(self.sw / 2 + 320, self.sh * 0.35, window=self.volume_label)

        # 静音按钮
        mute_text = "🔇" if self.audio_manager.is_muted() else "🔊"
        self.mute_btn = tk.Label(self.root, text=mute_text, font=("微软雅黑", 24),
                                bg="#2d3436", fg="white", padx=10, pady=5, cursor="hand2")
        self.mute_btn.bind("<Button-1>", self.toggle_mute)
        self.mute_btn.bind("<Enter>", lambda e: self.mute_btn.config(bg="#ff8906"))
        self.mute_btn.bind("<Leave>", lambda e: self.mute_btn.config(bg="#2d3436"))
        self.canvas.create_window(self.sw / 2 + 430, self.sh * 0.35, window=self.mute_btn)

        # 自动播放延迟设置
        self.canvas.create_text(self.sw / 2 - 230, self.sh * 0.48, text="自动播放延迟", fill="white",
                                font=("微软雅黑", 24), anchor="e")

        # 自动播放延迟滑块(500-5000,步长100)
        self.auto_play_delay_var = tk.IntVar(value=self.auto_play_delay)
        delay_slider = tk.Scale(self.root, from_=500, to=5000, orient=tk.HORIZONTAL,
                               length=400, variable=self.auto_play_delay_var,
                               command=self.on_auto_play_delay_change,
                               bg="#2d3436", fg="white", highlightthickness=0,
                               troughcolor="#555", activebackground="#ff8906",
                               font=("微软雅黑", 14), resolution=100)
        self.canvas.create_window(self.sw / 2 + 40, self.sh * 0.48, window=delay_slider)
        
        # 自动播放延迟数值显示
        self.delay_label = tk.Label(self.root, text=f"{self.auto_play_delay}ms",
                                    font=("微软雅黑", 20), bg="#2d3436", fg="white")
        self.canvas.create_window(self.sw / 2 + 320, self.sh * 0.48, window=self.delay_label)

        # 返回按钮 - 根据来源显示不同按钮
        if return_to_game:
            back_text = "▶️ 返回游戏"
            back_cmd = lambda: self.render_frame()
        else:
            back_text = "🏠 返回主页"
            back_cmd = self.render_menu

        back_btn = tk.Label(self.root, text=back_text, font=("黑体", 18), bg="#2d3436", fg="white",
                            padx=40, pady=10, cursor="hand2", width=15)
        back_btn.bind("<Button-1>", lambda e: back_cmd())
        back_btn.bind("<Enter>", lambda e: back_btn.config(bg="#ff8906"))
        back_btn.bind("<Leave>", lambda e: back_btn.config(bg="#2d3436"))
        self.canvas.create_window(self.sw / 2, self.sh * 0.65, window=back_btn)

    def on_volume_change(self, value):
        """音量滑块变化时的回调"""
        volume = float(value) / 100
        self.set_bgm_volume(volume)
        self.volume_label.config(text=f"{int(volume * 100)}%")

    def on_auto_play_delay_change(self, value):
        """自动播放延迟滑块变化时的回调"""
        delay = int(value)
        self.auto_play_delay = delay
        self.save_auto_play_delay()
        self.delay_label.config(text=f"{delay}ms")

    def toggle_mute(self, event=None):
        """切换静音状态"""
        is_muted = self.audio_manager.toggle_mute()
        # 更新静音按钮图标
        self.mute_btn.config(text="🔇" if is_muted else "🔊")

    def quit_game(self):
        """退出游戏 - 使用自定义弹窗避免被全屏遮挡"""
        self.show_quit_confirm()

    def show_quit_confirm(self):
        """自定义退出确认弹窗（解决全屏下messagebox被遮挡问题）"""
        # 半透明遮罩
        self.quit_overlay = tk.Canvas(self.root, width=self.sw, height=self.sh, highlightthickness=0)
        self.quit_overlay.place(x=0, y=0)
        self.quit_overlay.create_rectangle(0, 0, self.sw, self.sh, fill="#000000", stipple="gray25")

        # 弹窗容器
        popup_w, popup_h = 420, 260
        popup_x = (self.sw - popup_w) // 2
        popup_y = (self.sh - popup_h) // 2

        self.quit_frame = tk.Frame(self.root, bg="#2d3436", width=popup_w, height=popup_h,
                                   bd=2, relief="solid", highlightbackground="#ff4757", highlightthickness=2)
        self.quit_frame.place(x=popup_x, y=popup_y)

        # 标题
        tk.Label(self.quit_frame, text="⚠️ 退出确认", font=("黑体", 26, "bold"),
                 bg="#2d3436", fg="#ff4757", pady=20).pack()

        # 确认文本
        tk.Label(self.quit_frame, text="确定要离开「咸师反诈迷雾」吗？", font=("微软雅黑", 16),
                 bg="#2d3436", fg="white", pady=10).pack()

        # 按钮容器
        btn_frame = tk.Frame(self.quit_frame, bg="#2d3436")
        btn_frame.pack(pady=25)

        # 确认退出按钮
        confirm_btn = tk.Label(btn_frame, text="确认退出", font=("微软雅黑", 16, "bold"),
                               bg="#c0392b", fg="white", padx=35, pady=10, cursor="hand2")
        confirm_btn.pack(side="left", padx=15)
        confirm_btn.bind("<Button-1>", lambda e: self.do_quit())
        confirm_btn.bind("<Enter>", lambda e: confirm_btn.config(bg="#e74c3c"))
        confirm_btn.bind("<Leave>", lambda e: confirm_btn.config(bg="#c0392b"))

        # 取消按钮
        cancel_btn = tk.Label(btn_frame, text="取消退出", font=("微软雅黑", 16, "bold"),
                              bg="#444", fg="white", padx=35, pady=10, cursor="hand2")
        cancel_btn.pack(side="left", padx=15)
        cancel_btn.bind("<Button-1>", lambda e: self.close_quit_confirm())
        cancel_btn.bind("<Enter>", lambda e: cancel_btn.config(bg="#666"))
        cancel_btn.bind("<Leave>", lambda e: cancel_btn.config(bg="#444"))

    def close_quit_confirm(self):
        """关闭退出确认弹窗"""
        if hasattr(self, 'quit_frame'):
            self.quit_frame.destroy()
            del self.quit_frame
        if hasattr(self, 'quit_overlay'):
            self.quit_overlay.destroy()
            del self.quit_overlay

    def do_quit(self):
        """真正执行退出"""
        self.close_quit_confirm()
        self.root.destroy()

    def clear_all_widgets(self):
        for w in self.root.winfo_children():
            # 跳过主画布，只删除其他控件
            if w == self.canvas:
                continue
            if isinstance(w, (tk.Label, tk.Scale, tk.Frame, tk.Canvas, tk.Scrollbar)):
                w.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    # 隐藏控制台图标（可选）
    # root.iconbitmap('your_icon.ico')
    game = AntiFraudGame(root)
    root.bind("<Escape>", lambda e: root.attributes("-fullscreen", False))
    root.mainloop()