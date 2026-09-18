import json
import os
import glob
import sys

def resource_path(relative_path):
    """获取资源文件的绝对路径，支持开发环境和打包后的环境"""
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

class ChapterManager:
    CHAPTERS_DIR = resource_path("data/chapters")
    CHAPTERS_FILE = resource_path("chapters.json")
    
    def __init__(self):
        self.chapters = []
        self.current_chapter_data = None
        self.load_all_chapters()
    
    def load_all_chapters(self):
        json_pattern = os.path.join(self.CHAPTERS_DIR, "*.json")
        chapter_files = glob.glob(json_pattern)
        
        print(f"[*] Scanning chapters in: {self.CHAPTERS_DIR}")
        print(f"[*] Found {len(chapter_files)} chapter files: {[os.path.basename(f) for f in chapter_files]}")
        
        if not chapter_files:
            print("[!] No chapter files found, loading defaults")
            self._load_default_chapters()
            return
        
        self.chapters = []
        for filepath in chapter_files:
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    chapter_info = {
                        "id": data["id"],
                        "name": data["name"],
                        "description": data["description"],
                        "icon": data.get("icon", "📖"),
                        "unlocked": False,
                        "filepath": filepath
                    }
                    self.chapters.append(chapter_info)
                    print(f"    [+] Loaded: {chapter_info['id']} - {chapter_info['name']}")
            except Exception as e:
                print(f"[ERROR] Failed to load chapter file {filepath}: {e}")
                import traceback
                traceback.print_exc()
        
        self.chapters.sort(key=lambda x: x["id"])
        print(f"[*] Total chapters loaded: {len(self.chapters)}")
        self.load_progress()
    
    def _load_default_chapters(self):
        self.chapters = [
            {"id": "chapter1", "name": "深渊之恋", "description": "网恋诈骗陷阱", "icon": "💕", "unlocked": True, "filepath": ""},
            {"id": "chapter2", "name": "赌局陷阱", "description": "网络赌博诈骗", "icon": "🎲", "unlocked": False, "filepath": ""},
            {"id": "chapter3", "name": "校园贷危机", "description": "不良网贷诈骗", "icon": "💳", "unlocked": False, "filepath": ""},
            {"id": "chapter4", "name": "求职陷阱", "description": "兼职刷单诈骗", "icon": "💼", "unlocked": False, "filepath": ""}
        ]
    
    def load_progress(self):
        print(f"[*] Loading chapter progress: {self.CHAPTERS_FILE}")
        if os.path.exists(self.CHAPTERS_FILE):
            try:
                with open(self.CHAPTERS_FILE, 'r', encoding='utf-8') as f:
                    progress_list = json.load(f)
                    print(f"[OK] Found save file with {len(progress_list)} chapters")
                    for saved in progress_list:
                        for chapter in self.chapters:
                            if chapter["id"] == saved["id"]:
                                old_unlocked = chapter["unlocked"]
                                chapter["unlocked"] = saved.get("unlocked", False)
                                if chapter["unlocked"] and not old_unlocked:
                                    print(f"    [+] Restored: {chapter['id']} - {chapter['name']}")
                                break
                    print(f"[OK] Chapter progress loaded")
            except Exception as e:
                print(f"[ERROR] Failed to load progress: {e}")
                import traceback
                traceback.print_exc()
                self.chapters[0]["unlocked"] = True
                print(f"    [!] Default: Chapter 1 unlocked")
        else:
            print(f"[!] Save file not found, default: Chapter 1 unlocked")
            self.chapters[0]["unlocked"] = True
    
    def save_progress(self):
        progress_list = []
        for chapter in self.chapters:
            progress_list.append({
                "id": chapter["id"],
                "name": chapter["name"],
                "description": chapter["description"],
                "icon": chapter["icon"],
                "unlocked": chapter["unlocked"]
            })
        try:
            print(f"[*] Saving chapter progress to: {self.CHAPTERS_FILE}")
            with open(self.CHAPTERS_FILE, 'w', encoding='utf-8') as f:
                json.dump(progress_list, f, indent=2, ensure_ascii=False)
            print(f"[OK] Chapter progress saved")
            unlocked_count = 0
            for ch in progress_list:
                if ch["unlocked"]:
                    unlocked_count += 1
                    print(f"    [+] {ch['id']} - {ch['name']} (unlocked)")
            print(f"    [STATS] Unlocked: {unlocked_count}/{len(progress_list)} chapters")
            
            if os.path.exists(self.CHAPTERS_FILE):
                with open(self.CHAPTERS_FILE, 'r', encoding='utf-8') as f:
                    verify_data = json.load(f)
                    print(f"[OK] File verified, {len(verify_data)} records")
            else:
                print(f"[ERROR] Warning: file does not exist after save!")
        except Exception as e:
            print(f"[ERROR] Failed to save progress: {e}")
            import traceback
            traceback.print_exc()
    
    def unlock_next_chapter(self, current_chapter_id):
        print(f"🔍 尝试解锁下一章 (当前章节: {current_chapter_id})")
        current_idx = None
        for i, chapter in enumerate(self.chapters):
            if chapter["id"] == current_chapter_id:
                current_idx = i
                break
        
        if current_idx is not None and current_idx + 1 < len(self.chapters):
            next_chapter = self.chapters[current_idx + 1]
            if next_chapter["unlocked"]:
                print(f"ℹ️ 章节已解锁，无需重复: {next_chapter['id']} - {next_chapter['name']}")
            else:
                print(f"🔓 解锁章节: {next_chapter['id']} - {next_chapter['name']}")
                next_chapter["unlocked"] = True
                self.save_progress()
        else:
            print(f"⚠️ 无法解锁下一章 (当前: {current_chapter_id}, 索引: {current_idx}, 总章节数: {len(self.chapters)})")

    def get_chapter_script(self, chapter_id):
        for chapter in self.chapters:
            if chapter["id"] == chapter_id:
                if chapter["filepath"]:
                    try:
                        with open(chapter["filepath"], 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            self.current_chapter_data = data
                            return data.get("script", [])
                    except Exception as e:
                        print(f"加载章节脚本失败 {chapter_id}: {e}")
                        return []
                return []
        return []
    
    def get_chapter_info(self, chapter_id):
        for chapter in self.chapters:
            if chapter["id"] == chapter_id:
                return chapter
        return None
    
    def is_chapter_unlocked(self, chapter_id):
        chapter = self.get_chapter_info(chapter_id)
        return chapter["unlocked"] if chapter else False
    
    def get_total_chapters(self):
        return len(self.chapters)
    
    def get_unlocked_count(self):
        return sum(1 for c in self.chapters if c["unlocked"])