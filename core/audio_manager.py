"""
音频管理器
负责统一管理背景音乐和音效
"""
import sys
import os
import json
import pygame


def resource_path(relative_path):
    """获取资源文件的绝对路径，支持开发环境和打包后的环境"""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


class AudioManager:
    def __init__(self, settings_file=".claude/settings.local.json"):
        self.settings_file = settings_file
        self.bgm_volume = self.load_bgm_volume()
        self.bgm_muted = self.load_bgm_muted()
        self.last_volume = self.bgm_volume  # 保存静音前的音量
        self.initialized = False

    def init_bgm(self, music_path="music/The Search - Richard Harvey.mp3"):
        """初始化并循环播放背景音乐"""
        try:
            pygame.mixer.init()
            pygame.mixer.music.load(resource_path(music_path))
            pygame.mixer.music.set_volume(self.bgm_volume if not self.bgm_muted else 0)
            pygame.mixer.music.play(-1)  # -1 表示循环播放
            self.initialized = True
            return True
        except Exception as e:
            print(f"无法播放背景音乐: {e}")
            self.initialized = False
            return False

    def set_volume(self, volume):
        """设置BGM音量"""
        self.bgm_volume = volume
        if not self.bgm_muted:
            self.last_volume = volume
        if self.initialized:
            pygame.mixer.music.set_volume(volume if not self.bgm_muted else 0)
        self.save_bgm_volume()

    def get_volume(self):
        """获取当前音量"""
        return self.bgm_volume

    def load_bgm_volume(self):
        """从配置文件加载BGM音量"""
        try:
            with open(self.settings_file, 'r', encoding='utf-8') as f:
                settings = json.load(f)
                return settings.get("game_settings", {}).get("bgm_volume", 0.5)
        except Exception as e:
            print(f"无法读取音量设置: {e}")
            return 0.5

    def save_bgm_volume(self):
        """保存BGM音量到配置文件"""
        try:
            settings = {}
            try:
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
            except:
                pass

            if "game_settings" not in settings:
                settings["game_settings"] = {}
            settings["game_settings"]["bgm_volume"] = self.bgm_volume

            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"无法保存音量设置: {e}")

    def load_bgm_muted(self):
        """从配置文件加载静音状态"""
        try:
            with open(self.settings_file, 'r', encoding='utf-8') as f:
                settings = json.load(f)
                return settings.get("game_settings", {}).get("bgm_muted", False)
        except Exception as e:
            print(f"无法读取静音设置: {e}")
            return False

    def save_bgm_muted(self):
        """保存静音状态到配置文件"""
        try:
            settings = {}
            try:
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    settings = json.load(f)
            except:
                pass

            if "game_settings" not in settings:
                settings["game_settings"] = {}
            settings["game_settings"]["bgm_muted"] = self.bgm_muted

            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"无法保存静音设置: {e}")

    def toggle_mute(self):
        """切换静音状态"""
        self.bgm_muted = not self.bgm_muted
        if self.initialized:
            if self.bgm_muted:
                pygame.mixer.music.set_volume(0)
            else:
                pygame.mixer.music.set_volume(self.last_volume)
        self.save_bgm_muted()
        return self.bgm_muted

    def is_muted(self):
        """获取当前静音状态"""
        return self.bgm_muted
