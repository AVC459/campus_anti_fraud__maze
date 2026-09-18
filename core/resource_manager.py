"""
资源管理器
负责统一管理所有图片资源的加载和访问
"""
import sys
import os
from PIL import Image, ImageTk


def resource_path(relative_path):
    """获取资源文件的绝对路径，支持开发环境和打包后的环境"""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


class ResourceManager:
    def __init__(self, screen_width, screen_height):
        self.sw = screen_width
        self.sh = screen_height
        self.images = {}
        self.characters = {}
        self.character_info = {}

    def load_backgrounds(self, bg_paths):
        """
        批量加载背景图
        bg_paths: dict, 例如 {"index": "assets/first/index.jpg", ...}
        """
        for key, path in bg_paths.items():
            try:
                img = Image.open(resource_path(path))
                img = img.resize((self.sw, self.sh), Image.Resampling.LANCZOS)
                self.images[key] = ImageTk.PhotoImage(img)
            except Exception as e:
                print(f"无法加载图片 {path}: {e}")
                placeholder = Image.new('RGB', (self.sw, self.sh), color='#1a1c2c')
                self.images[key] = ImageTk.PhotoImage(placeholder)

    def load_characters(self, char_paths, target_ratio=0.42):
        """
        批量加载角色立绘（等比例缩放）
        char_paths: dict, 例如 {"linshu1": "assets/first/character/girl1.png", ...}
        target_ratio: 角色高度占屏幕高度的比例
        """
        target_height = int(self.sh * target_ratio)

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

    def get_background(self, key):
        """获取背景图"""
        return self.images.get(key)

    def get_character(self, key):
        """获取角色立绘"""
        return self.characters.get(key)

    def get_character_info(self, key):
        """获取角色信息（宽高）"""
        return self.character_info.get(key, {"width": int(self.sw * 0.2), "height": int(self.sh * 0.42)})

    def has_image(self, key):
        """检查图片是否存在"""
        return key in self.images
