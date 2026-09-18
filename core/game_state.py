"""
游戏状态管理器
负责管理游戏的所有状态数据，包括信任值、怀疑值、金钱、线索等
"""
import json
import os


class GameStateManager:
    def __init__(self):
        # 多结局系统状态
        self.flags = set()  # 标记集合：追踪玩家选择
        self.clues_collected = []  # 收集的隐藏线索
        self.money_lost = 0  # 累计损失金额
        self.current_ending = None  # 当前结局ID

        # 信任值和怀疑值系统
        self.trust_value = 50  # 信任值 0-100
        self.suspicion_value = 20  # 怀疑值 0-100
        
        # 成就系统
        self.unlocked_achievements = set()  # 已解锁的成就ID集合
        self.achievement_file = "achievements.json"  # 成就数据文件
        self._load_achievements()

    def update_trust(self, value):
        """更新信任值（自动限制在0-100范围）"""
        self.trust_value = max(0, min(100, self.trust_value + value))

    def update_suspicion(self, value):
        """更新怀疑值（自动限制在0-100范围）"""
        self.suspicion_value = max(0, min(100, self.suspicion_value + value))

    def add_money(self, amount):
        """添加金钱变化（负数表示损失，正数表示收入/返还）"""
        if amount < 0:
            self.money_lost += abs(amount)
        # 正数表示收入/返还，不增加损失
        return self.money_lost

    def add_flag(self, flag):
        """添加标记"""
        self.flags.add(flag)

    def has_flag(self, flag):
        """检查是否有某个标记"""
        return flag in self.flags

    def add_clue(self, clue_id):
        """添加线索"""
        if clue_id not in self.clues_collected:
            self.clues_collected.append(clue_id)
            return True
        return False

    def reset(self):
        """重置所有状态到初始值"""
        self.flags = set()
        self.clues_collected = []
        self.money_lost = 0
        self.current_ending = None
        self.trust_value = 50
        self.suspicion_value = 20

    def save_to_file(self, filepath, idx=0, current_chapter="chapter1"):
        """保存游戏状态到文件"""
        try:
            save_data = {
                "idx": idx,
                "current_chapter": current_chapter,
                "flags": list(self.flags),
                "clues": self.clues_collected,
                "money_lost": self.money_lost,
                "trust_value": self.trust_value,
                "suspicion_value": self.suspicion_value
            }
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(save_data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"保存游戏状态失败: {e}")
            return False

    def load_from_file(self, filepath):
        """从文件加载游戏状态"""
        if not os.path.exists(filepath):
            return None

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)

            self.flags = set(data.get("flags", []))
            self.clues_collected = data.get("clues", [])
            self.money_lost = data.get("money_lost", 0)
            self.trust_value = data.get("trust_value", 50)
            self.suspicion_value = data.get("suspicion_value", 20)
            return {
                "idx": data.get("idx", 0),
                "current_chapter": data.get("current_chapter", "chapter1")
            }
        except Exception as e:
            print(f"加载游戏状态失败: {e}")
            return None

    def get_state_dict(self):
        """获取状态的字典形式（用于存档）"""
        return {
            "flags": list(self.flags),
            "clues": self.clues_collected,
            "money_lost": self.money_lost,
            "trust_value": self.trust_value,
            "suspicion_value": self.suspicion_value
        }
    
    # ==================== 成就系统方法 ====================
    
    def _load_achievements(self):
        """从文件加载已解锁的成就"""
        if os.path.exists(self.achievement_file):
            try:
                with open(self.achievement_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.unlocked_achievements = set(data.get('unlocked', []))
            except Exception as e:
                print(f"加载成就失败: {e}")
                self.unlocked_achievements = set()
    
    def _save_achievements(self):
        """保存已解锁的成就到文件"""
        try:
            data = {
                'unlocked': list(self.unlocked_achievements)
            }
            with open(self.achievement_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"保存成就失败: {e}")
            return False
    
    def unlock_achievement(self, achievement_id):
        """解锁一个成就"""
        if achievement_id and achievement_id not in self.unlocked_achievements:
            self.unlocked_achievements.add(achievement_id)
            self._save_achievements()
            return True
        return False
    
    def is_achievement_unlocked(self, achievement_id):
        """检查成就是否已解锁"""
        return achievement_id in self.unlocked_achievements
    
    def get_all_unlocked_achievements(self):
        """获取所有已解锁的成就"""
        return list(self.unlocked_achievements)
    
    def reset_achievements(self):
        """重置所有成就（慎用）"""
        self.unlocked_achievements = set()
        self._save_achievements()
