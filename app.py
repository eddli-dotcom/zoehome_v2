import streamlit as st
import json
import os
import random
import time
import uuid
from datetime import datetime
import base64
import mimetypes

# --- 1. 頁面設定 ---
st.set_page_config(page_title="Zoe's Coin Bank RPG", page_icon="⚔️", layout="centered")

# --- 2. CSS ---
st.markdown("""
<style>
    .stApp { background-color: #fffaf0 !important; }
    html, body, p, h1, h2, h3, h4, span, label, div { color: #333333 !important; }
    .zoe-container { display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 10px 0; }
    .zoe-circular { width: 140px; height: 140px; border-radius: 50%; object-fit: cover; border: none !important; display: block; box-shadow: 0 0 20px rgba(255, 215, 0, 0.4) !important; }
    @keyframes coin-pulse { 0% { transform: scale(1); } 50% { transform: scale(1.08); } 100% { transform: scale(1); } }
    .animated-coins { animation: coin-pulse 2s infinite ease-in-out; display: inline-block; }
    div.stButton > button { background-color: #ffffff !important; color: #B8860B !important; border: 2px solid #FFD700 !important; border-radius: 12px !important; box-shadow: 0 4px 6px rgba(0,0,0,0.05) !important; font-weight: bold !important; transition: all 0.15s; }
    div.stButton > button:active { transform: scale(0.92) !important; background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%) !important; color: #ffffff !important; }
    .badge-base { color: white !important; padding: 4px 8px; border-radius: 20px; font-weight: bold; font-size: 0.75rem; display: inline-block; margin: 2px; }
    .bg-gold { background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%); }
    .bg-red { background: #e74c3c; }
    .bg-orange { background: #ff7e5f; }
    .bg-blue { background: #3498db; }
    .chore-name { font-size: 1.05rem; font-weight: bold; color: #2c3e50 !important; display: inline-block; margin-bottom: 4px;}
    .history-track { font-size: 0.8rem; margin-top: 4px; color: #555; background: #fff5e6; padding: 2px 8px; border-radius: 8px; display: inline-block; }
    .metric-container { background: white; padding: 15px; border-radius: 15px; border: 2px solid #FFD700; text-align: center; box-shadow: 0 4px 10px rgba(255,215,0,0.15); margin-bottom: 15px;}
    .coin-val { font-size: 2rem; font-weight: 900; color: #B8860B !important; margin: 5px 0; }
    .goal-text { text-align: center; font-size: 1.1rem; font-weight: 800; color: #B8860B !important; margin-bottom: 5px;}
    .zoe-bubble { background-color: white; border: 2px dashed #FFD700; border-radius: 15px; padding: 10px; margin-top: 15px; text-align: center; font-weight: bold; color: #B8860B !important; font-size: 0.9rem; }
    .gacha-box { background: linear-gradient(135deg, #a8c0ff 0%, #3f2b96 100%); color: white !important; padding: 15px; border-radius: 15px; text-align: center; border: 3px solid #FFD700;}
    .bingo-box { background: #e8f8f5; border: 2px dashed #1abc9c; padding: 10px; border-radius: 10px; margin-bottom: 15px;}
    .zoe-summon-box { background: linear-gradient(135deg, #FFD700 0%, #ff8c00 100%); padding: 15px; border-radius: 15px; text-align: center; margin-bottom: 15px; box-shadow: 0 4px 15px rgba(255,215,0,0.4); animation: coin-pulse 2s infinite ease-in-out; }
    .boss-box { background: linear-gradient(135deg, #ff416c 0%, #ff4b2b 100%); padding: 15px; border-radius: 15px; text-align: center; margin-bottom: 15px; color: white !important; box-shadow: 0 4px 15px rgba(255,65,108,0.4); }
    .profile-card { background: white; border: 1px solid #eee; border-radius: 12px; padding: 15px; box-shadow: 0 2px 8px rgba(0,0,0,0.05); }
    .inventory-emojis { font-size: 1.1rem; letter-spacing: 2px; color: #555; background: #fdfbf7; padding: 5px 10px; border-radius: 8px; border: 1px dashed #ddd; margin-top: 5px; }
    .hot-chore { background: linear-gradient(to right, #ffecd2 0%, #fcb69f 100%); padding: 10px; border-radius: 10px; border: 2px dashed #ff7e5f; margin-bottom: 10px;}
</style>
""", unsafe_allow_html=True)

# --- 3. 系統資料定義 (裝備/職業/世界BOSS/撩人話語) ---
DATA_FILE = "coin_data_v15.json"

CLASS_DATA = {
    "大便大王路線 💩": {"chores": ["放狗", "擦狗", "洗厠所"], "tiers": [(1, "💩 鏟屎官", 1), (10, "💩 大便達人", 3), (25, "👑 大便大王", 6)]},
    "聖騎士路線 ⚔️": {"chores": ["拖/掃地", "洗浴缸", "洗衣服"], "tiers": [(1, "🛡️ 士兵", 1), (10, "🗡️ 騎士", 3), (25, "⚔️ 聖騎士", 6)]},
    "鍊金術士路線 🧪": {"chores": ["煲水", "買菜/飯", "喂狗吃飯"], "tiers": [(1, "🧪 學徒", 1), (10, "🔬 研究員", 3), (25, "🔮 鍊金術士", 6)]},
    "馴獸師路線 🦁": {"chores": ["放狗", "幫狗刷牙", "剪指甲"], "tiers": [(1, "🐾 動物之友", 1), (10, "🐕 遛狗員", 3), (25, "🦁 馴獸師", 6)]},
    "空間大師路線 🌌": {"chores": ["收拾家居", "扔垃圾"], "tiers": [(1, "📦 搬運工", 1), (10, "🧹 整理達人", 3), (25, "🌌 空間大師", 6)]},
    "海洋祭司路線 🌊": {"chores": ["洗浴缸", "洗厠所", "洗衣服"], "tiers": [(1, "💧 挑水工", 1), (10, "🛁 浴室領主", 3), (25, "🌊 海洋祭司", 6)]},
    "暗影大師路線 🌑": {"chores": ["扔垃圾", "買菜/飯"], "tiers": [(1, "🥷 見習隱者", 1), (10, "🗡️ 刺客", 3), (25, "🌑 暗影大師", 6)]},
    "地獄廚神路線 👨‍🍳": {"chores": ["買菜/飯", "煲水", "喂狗吃飯"], "tiers": [(1, "🍳 洗碗工", 1), (10, "🔪 二廚", 3), (25, "👨‍🍳 地獄廚神", 6)]},
    "機甲導師路線 🤖": {"chores": ["收拾家居", "洗浴缸"], "tiers": [(1, "🛠️ 學徒工", 1), (10, "⚙️ 工匠", 3), (25, "🤖 機甲導師", 6)]},
    "大魔導士路線 🌟": {"chores": ["ALL"], "tiers": [(1, "🪄 魔法學徒", 0), (10, "🧙 巫師", 1), (25, "🌟 大魔導士", 2)]}
}

GEAR_DATA = {
    # 傳說
    "黃金掃把 🧹": {"desc": "10% 機率結算金幣翻倍", "max_dur": 30, "bonus_coins": 0, "target": [], "special": "rng_double", "rarity": "Legendary"},
    "賢者之石 💎": {"desc": "所有任務金幣 +5", "max_dur": 8, "bonus_coins": 5, "target": ["ALL"], "special": None, "rarity": "Legendary"},
    "時間沙漏 ⏳": {"desc": "永遠觸發最高 +5 獵人賞金", "max_dur": 15, "bonus_coins": 0, "target": [], "special": "max_bounty", "rarity": "Legendary"},
    "Zoe 的秘密零食罐 🥫": {"desc": "狗狗任務 +3 幣，Zoe 心情大幅增加", "max_dur": 12, "bonus_coins": 3, "target": ["狗"], "special": "zoe_hap_10", "rarity": "Legendary"},
    "幸運扭蛋幣 🪙": {"desc": "20% 機率結算金幣翻倍", "max_dur": 5, "bonus_coins": 0, "target": ["ALL"], "special": "rng_double_20", "rarity": "Legendary"},
    # 史詩
    "神聖馬桶刷 🚽": {"desc": "洗厠所金幣 +8", "max_dur": 12, "bonus_coins": 8, "target": ["洗厠所"], "special": None, "rarity": "Epic"},
    "狂戰士手套 🥊": {"desc": "困難任務額外 +5 幣", "max_dur": 15, "bonus_coins": 5, "target": ["HARD_ONLY"], "special": None, "rarity": "Epic"},
    "Zoe 的金項圈 🐶": {"desc": "狗狗任務 +4，Zoe心情 +5", "max_dur": 20, "bonus_coins": 4, "target": ["狗"], "special": "zoe_hap_5", "rarity": "Epic"},
    "疾風拖鞋 🩴": {"desc": "連擊加成額外 +2", "max_dur": 25, "bonus_coins": 0, "target": ["ALL"], "special": "streak_plus_2", "rarity": "Epic"},
    "尋寶羅盤 🧭": {"desc": "完成任務 5% 機率天降 10 金幣", "max_dur": 30, "bonus_coins": 0, "target": ["ALL"], "special": "rng_10_coins", "rarity": "Epic"},
    "Zoe 的專屬飛盤 🥏": {"desc": "放狗 +6 幣，Zoe心情 +5", "max_dur": 15, "bonus_coins": 6, "target": ["放狗"], "special": "zoe_hap_5", "rarity": "Epic"},
    "Zoe 的超級潔牙骨 🦴": {"desc": "幫狗刷牙 +6 幣", "max_dur": 15, "bonus_coins": 6, "target": ["刷牙"], "special": "zoe_hap_5", "rarity": "Epic"},
    "強力吸塵機 🌪️": {"desc": "拖/掃地 +5 幣", "max_dur": 20, "bonus_coins": 5, "target": ["拖/掃地"], "special": None, "rarity": "Epic"},
    # 稀有
    "幸運四葉草 🍀": {"desc": "所有任務額外 +2 幣", "max_dur": 35, "bonus_coins": 2, "target": ["ALL"], "special": None, "rarity": "Rare"},
    "魔法洗衣精 🧴": {"desc": "洗/收晾衣服 +4 幣", "max_dur": 20, "bonus_coins": 4, "target": ["衣服"], "special": None, "rarity": "Rare"},
    "主廚的圍裙 👨‍🍳": {"desc": "買菜/喂狗/煲水 +3 幣", "max_dur": 25, "bonus_coins": 3, "target": ["買菜", "喂狗", "煲水"], "special": None, "rarity": "Rare"},
    "馴獸師的口哨 🪈": {"desc": "放狗 +3 幣", "max_dur": 30, "bonus_coins": 3, "target": ["放狗"], "special": None, "rarity": "Rare"},
    "鋼鐵指甲剪 ✂️": {"desc": "剪指甲 +5 幣", "max_dur": 10, "bonus_coins": 5, "target": ["剪指甲"], "special": None, "rarity": "Rare"},
    "附魔拖把 🧹": {"desc": "拖/掃地 +3 幣", "max_dur": 20, "bonus_coins": 3, "target": ["拖/掃地"], "special": None, "rarity": "Rare"},
    "鈦合金垃圾袋 🗑️": {"desc": "扔垃圾 +2 幣", "max_dur": 40, "bonus_coins": 2, "target": ["垃圾"], "special": None, "rarity": "Rare"},
    "Zoe 的毛茸茸刷子 🖌️": {"desc": "擦狗 +3 幣，Zoe心情 +5", "max_dur": 25, "bonus_coins": 3, "target": ["擦狗"], "special": "zoe_hap_5", "rarity": "Rare"},
    "萬能瑞士刀 🔪": {"desc": "買菜/煲水 +3 幣", "max_dur": 30, "bonus_coins": 3, "target": ["買菜", "煲水"], "special": None, "rarity": "Rare"},
    "潔癖者的口罩 😷": {"desc": "扔垃圾/洗厠所 +3 幣", "max_dur": 25, "bonus_coins": 3, "target": ["垃圾", "洗厠所"], "special": None, "rarity": "Rare"},
    # 普通
    "破舊的抹布 🧽": {"desc": "所有任務 +1 幣", "max_dur": 15, "bonus_coins": 1, "target": ["ALL"], "special": None, "rarity": "Common"},
    "洗碗機的祝福 🍽️": {"desc": "收拾家居 +1 幣", "max_dur": 25, "bonus_coins": 1, "target": ["收拾"], "special": None, "rarity": "Common"},
    "購物狂的布袋 🛍️": {"desc": "買菜/飯 +2 幣", "max_dur": 20, "bonus_coins": 2, "target": ["買菜/飯"], "special": None, "rarity": "Common"},
    "狗零食背包 🎒": {"desc": "狗狗任務 +1 幣", "max_dur": 25, "bonus_coins": 1, "target": ["狗"], "special": None, "rarity": "Common"},
    "泡澡小黃鴨 🦆": {"desc": "洗浴缸 +2 幣", "max_dur": 20, "bonus_coins": 2, "target": ["洗浴缸"], "special": None, "rarity": "Common"},
    "懶骨頭沙發 🛋️": {"desc": "金幣 -1，Zoe 心情 +10", "max_dur": 20, "bonus_coins": -1, "target": ["ALL"], "special": "zoe_hap_10", "rarity": "Common"},
    "Zoe 的保暖小毯毯 🛌": {"desc": "狗狗任務 +1 幣，Zoe心情 +5", "max_dur": 30, "bonus_coins": 1, "target": ["狗"], "special": "zoe_hap_5", "rarity": "Common"},
    "主婦的洗碗手套 🧤": {"desc": "收拾家居 +2 幣", "max_dur": 30, "bonus_coins": 2, "target": ["收拾"], "special": None, "rarity": "Common"}
}

DEFAULT_CHORES_INFO = {
    "🐶 放狗 (Zoe)": {"base": 4, "frequent": True, "last_done": None, "last_person": None, "streak": 0},
    "🧼 擦狗": {"base": 3, "frequent": True, "last_done": None, "last_person": None, "streak": 0},
    "🍚 喂狗吃飯": {"base": 1, "frequent": True, "last_done": None, "last_person": None, "streak": 0},
    "🪥 幫狗刷牙": {"base": 3, "frequent": False, "last_done": None, "last_person": None, "streak": 0},
    "✂️ 剪指甲": {"base": 7, "frequent": False, "last_done": None, "last_person": None, "streak": 0},
    "👕 洗衣服": {"base": 2, "frequent": False, "last_done": None, "last_person": None, "streak": 0},
    "🧺 收晾衣服": {"base": 2, "frequent": False, "last_done": None, "last_person": None, "streak": 0},
    "🗑️ 扔垃圾": {"base": 2, "frequent": True, "last_done": None, "last_person": None, "streak": 0},
    "🫖 煲水": {"base": 1, "frequent": True, "last_done": None, "last_person": None, "streak": 0},
    "🧹 拖/掃地": {"base": 4, "frequent": False, "last_done": None, "last_person": None, "streak": 0},
    "🚽 洗厠所": {"base": 10, "frequent": False, "last_done": None, "last_person": None, "streak": 0}
}
STORE_ITEMS = {"免做家事金牌 🛡️": 40, "幫我泡杯咖啡/茶 ☕": 20, "今晚電視控制權 📺": 30, "搥背 10 分鐘 💆": 30, "指定對方做一件家事 👉": 50}

ZOE_MESSAGES = [
    "Zoe 滿心期待地搖著尾巴！🐾 快去做家事吧！", "家裡乾淨的話，Zoe 會在地上開心地打滾喔！✨",
    "汪汪！記得檢查裝備的耐久度，去鐵匠鋪可以修復！🔨", "累積滿 200 金幣，Zoe 就會降臨並帶來超大禮盒喔！🌟",
    "今天誰是家事大師呢？Zoe 正在盯著你們看！👀", "連續做同一個任務會有連擊加成，越做越賺喔！🔥",
    "每日發燒任務有 1.5 倍加成，千萬別錯過啦！📈", "收到伴侶送的禮物了嗎？記得說聲謝謝！💖",
    "稀有裝備『黃金掃把』可是能讓金幣翻倍的神器喔！🧹", "打敗突發的世界 BOSS 可以獲得大量金幣喔！🐉",
    "沒人想做的任務會自動累積賞金，快去當賞金獵人吧！🎯", "多餘的普通裝備可以去鐵匠鋪合成稀有神器喔！🧪"
]

GIFT_MSGS = [
    "為你獻上我的傳家寶！ 💎", "看你這麼辛苦，賞你的！別太愛我 😏",
    "這可是我千辛萬苦打來的，好好珍惜啊！ ⚔️", "我的心和這個裝備，現在都歸你了 ❤️",
    "拿去吧！這就是強者的餘裕 😎", "寶貝，這個超適合你，快戴上給大爺/老娘看看！ 😘",
    "收下吧，這是我們愛情的結晶 (大誤) 🤣"
]

BOSS_LIST = [
    {"name": "✨ 提升居家風水大掃除", "chores": ["🧹 拖/掃地", "🏠 收拾家居", "🗑️ 扔垃圾"], "reward": 60},
    {"name": "🐶 Zoe 狗狗聚會準備", "chores": ["👕 洗衣服", "🧼 擦狗", "✂️ 剪指甲"], "reward": 50},
    {"name": "🐾 Zoe 渴望出街瘋玩", "chores": ["🐶 放狗 (Zoe)", "🍚 喂狗吃飯", "🧼 擦狗"], "reward": 50},
    {"name": "🦠 擊退季節性過敏原", "chores": ["🧹 拖/掃地", "👕 洗衣服", "🛁 洗浴缸"], "reward": 60},
    {"name": "🍽️ 浪漫燭光晚餐準備", "chores": ["🛍️ 買菜/飯", "🏠 收拾家居", "🚽 洗厠所"], "reward": 70},
    {"name": "👑 迎接岳父母/貴客降臨", "chores": ["🧹 拖/掃地", "🏠 收拾家居", "🚽 洗厠所"], "reward": 100},
    {"name": "🛁 終極衛浴保衛戰", "chores": ["🛁 洗浴缸", "🚽 洗厠所", "🗑️ 扔垃圾"], "reward": 60},
    {"name": "🧺 換季衣物大作戰", "chores": ["👕 洗衣服", "🧺 收晾衣服", "🏠 收拾家居"], "reward": 50}
]

def generate_gear(gear_name):
    g_data = GEAR_DATA[gear_name]
    return {"uid": str(uuid.uuid4()), "name": gear_name, "durability": g_data["max_dur"], "max_durability": g_data["max_dur"]}

def get_emoji(item_name):
    return item_name.split()[-1] if " " in item_name else "📦"

# --- 4. 數據庫初始化與遷移 ---
def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f: return json.load(f)
        except: pass
    return {"老公": 0, "老婆": 0, "history": [], "chores_info": DEFAULT_CHORES_INFO, "users": {}}

app_data = load_data()

for p in ["老公", "老婆"]:
    if "users" not in app_data: app_data["users"] = {}
    if p not in app_data["users"]: 
        app_data["users"][p] = {"inventory": [], "last_daily": None, "exp": 0, "level": 1, "active_class": "大便大王路線 💩", "equipped_gear": None, "gear_inventory": []}
    u = app_data["users"][p]
    
    if "stats" not in u: 
        u["stats"] = {"chores": {}, "total_chores": 0, "total_earned": 0, "gacha_pulls": 0, "gear_broken": 0, "bingos": 0, "zoe_100": 0, "store_bought": 0, "max_streak": 0, "max_bounty": 0, "night_owl": False, "hard_mode": False}
    if "achievements" not in u: u["achievements"] = ["新手村村民 🐣"]
    if "active_title" not in u: u["active_title"] = "新手村村民 🐣"
    if "exp" not in u: u.update({"exp": 0, "level": 1, "active_class": "大便大王路線 💩", "equipped_gear": None, "gear_inventory": []})
    
    new_gear_inv = []
    for g in u.get("gear_inventory", []):
        if isinstance(g, str) and g in GEAR_DATA: new_gear_inv.append(generate_gear(g))
        elif isinstance(g, dict) and "uid" in g: new_gear_inv.append(g)
    u["gear_inventory"] = new_gear_inv
    
    if isinstance(u.get("equipped_gear"), str):
        found = False
        for g in new_gear_inv:
            if g["name"] == u["equipped_gear"]: u["equipped_gear"] = g["uid"]; found = True; break
        if not found: u["equipped_gear"] = None

for c_name, c_props in DEFAULT_CHORES_INFO.items():
    if c_name not in app_data["chores_info"]: app_data["chores_info"][c_name] = c_props

current_time = datetime.now()
current_date_str = current_time.strftime("%Y-%m-%d")
current_month_str = current_time.strftime("%Y-%m")
current_week_str = current_time.strftime("%Y-%W")
current_hour = current_time.hour

# 初始化新功能資料庫
if "zoe_happiness" not in app_data: app_data["zoe_happiness"] = {"score": 50, "last_decay": current_date_str}
if "monthly_data" not in app_data: app_data["monthly_data"] = {"month": current_month_str, "老公": 0, "老婆": 0, "mvp": "尚無"}
if "weekly_bingo" not in app_data: app_data["weekly_bingo"] = {"week": current_week_str, "chores": random.sample(list(app_data["chores_info"].keys()), 3), "done_by": {"老公": [], "老婆": []}}
if "daily_hot_chores" not in app_data: app_data["daily_hot_chores"] = {"date": "", "chores": []}
if "world_boss" not in app_data: app_data["world_boss"] = {"active": False, "name": "", "chores_needed": [], "chores_done": [], "reward": 0}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f: json.dump(data, f, ensure_ascii=False, indent=4)

def check_achievements(person):
    u = app_data["users"][person]
    s = u["stats"]; ach = u["achievements"]
    new_ach = []
    def award(title):
        if title not in ach: ach.append(title); new_ach.append(title)
            
    if s["chores"].get("🚽 洗厠所", 0) >= 3: award("廁所守護者 🚽")
    if sum(v for k, v in s["chores"].items() if "狗" in k) >= 10: award("汪星人摯友 🐾")
    if sum(v for k, v in s["chores"].items() if "衣服" in k) >= 5: award("洗衣大師 👕")
    if s["total_chores"] >= 20: award("家務狂人 🌪️")
    if s["max_streak"] >= 3: award("連擊大師 ⚡")
    if s["max_bounty"] >= 5: award("賞金獵人 🎯")
    if s["night_owl"]: award("深夜勞工 🦉")
    if s["hard_mode"]: award("硬核玩家 ☠️")
    if s["gacha_pulls"] >= 5: award("盲盒成癮者 🎰")
    if s["gear_broken"] >= 1: award("裝備破壞王 💥")
    if s["bingos"] >= 1: award("完美Bingo 🎯")
    if s["zoe_100"] >= 1: award("Zoe的信徒 🙏")
    if s["store_bought"] >= 5: award("課金大佬 💸")
    if u["level"] >= 10: award("滿級大佬 👑")
    if s["total_earned"] >= 500: award("財富自由 💰")
    
    if new_ach:
        save_data(app_data)
        for title in new_ach: st.toast(f"🏆 {person} 解鎖新稱號：{title}！", icon="🎉")

# 每日自動排程 (刷新與觸發事件)
if app_data["zoe_happiness"]["last_decay"] != current_date_str:
    days = (current_time.date() - datetime.strptime(app_data["zoe_happiness"]["last_decay"], "%Y-%m-%d").date()).days
    app_data["zoe_happiness"]["score"] = max(0, app_data["zoe_happiness"]["score"] - (10 * days))
    app_data["zoe_happiness"]["last_decay"] = current_date_str; save_data(app_data)

if app_data["monthly_data"]["month"] != current_month_str:
    winner = "老公" if app_data["monthly_data"]["老公"] > app_data["monthly_data"]["老婆"] else "老婆" if app_data["monthly_data"]["老婆"] > app_data["monthly_data"]["老公"] else "平手"
    if winner in ["老公", "老婆"]:
        app_data[winner] += 20
        app_data["history"].insert(0, {"time": current_time.strftime("%m/%d %H:%M"), "person": winner, "chore": "👑 榮獲上月 MVP 獎勵", "coins": 20})
    app_data["monthly_data"] = {"month": current_month_str, "老公": 0, "老婆": 0, "mvp": winner}; save_data(app_data)

if app_data["weekly_bingo"]["week"] != current_week_str:
    app_data["weekly_bingo"] = {"week": current_week_str, "chores": random.sample(list(app_data["chores_info"].keys()), 3), "done_by": {"老公": [], "老婆": []}}
    save_data(app_data)

if app_data["daily_hot_chores"]["date"] != current_date_str:
    app_data["daily_hot_chores"] = {"date": current_date_str, "chores": random.sample(list(app_data["chores_info"].keys()), 2)}
    # 每天 15% 機率自動觸發世界 BOSS (如果沒有存在的)
    if not app_data["world_boss"]["active"] and random.random() < 0.15:
        boss_data = random.choice(BOSS_LIST)
        app_data["world_boss"] = {"active": True, "name": boss_data["name"], "chores_needed": boss_data["chores"], "chores_done": [], "reward": boss_data["reward"]}
    save_data(app_data)

random.seed(current_date_str); flash_item = random.choice(list(STORE_ITEMS.keys())); random.seed()

# --- 5. UI 主畫面與儀表板 ---
st.markdown('<div class="zoe-container">', unsafe_allow_html=True)
possible_photos = ["zoe.png", "zoe.jpg", "zoe.jpeg"]
found_photo = next((p for p in possible_photos if os.path.exists(p)), None)
if found_photo:
    try:
        with open(found_photo, "rb") as image_file: encoded_string = base64.b64encode(image_file.read()).decode()
        mime_type, _ = mimetypes.guess_type(found_photo)
        st.markdown(f'<img src="data:{mime_type or "image/png"};base64,{encoded_string}" class="zoe-circular">', unsafe_allow_html=True)
    except: pass
else: st.image("https://images.unsplash.com/photo-1552053831-71594a27632d?auto=format&fit=crop&w=400&q=80", width=140)

hap_score = app_data["zoe_happiness"]["score"]
st.progress(hap_score / 100.0, text=f"❤️ Zoe 的心情指數：{hap_score}%")
st.markdown(f'<div class="zoe-bubble">💬 <b>Zoe 說：</b> {random.choice(ZOE_MESSAGES)}</div></div>', unsafe_allow_html=True)

# 🐲 世界 BOSS 橫幅
if app_data["world_boss"]["active"]:
    wb = app_data["world_boss"]
    st.markdown(f"""<div class='boss-box'>
        <h2 style='margin:0;'>🐲 世界 BOSS 襲來：{wb['name']}</h2>
        <p style='margin:5px 0 0 0; font-weight:bold;'>共同完成以下任務，擊敗魔王獲得 {wb['reward']} 🪙 獎勵！</p>
        <p style='font-size:0.9rem; margin:0;'>任務要求：{', '.join([f"~~{c}~~" if c in wb['chores_done'] else c for c in wb['chores_needed']])}</p>
    </div>""", unsafe_allow_html=True)

# 📊 主頁金幣視覺化儀表板
col_h, col_w = st.columns(2)
with col_h:
    st.markdown(f"<div class='metric-container'><p style='margin:0; font-size:1rem; color:#666 !important; font-weight:bold;'>👨 老公金幣庫</p><p class='animated-coins coin-val'>🪙 {app_data['老公']}</p></div>", unsafe_allow_html=True)
with col_w:
    st.markdown(f"<div class='metric-container'><p style='margin:0; font-size:1rem; color:#666 !important; font-weight:bold;'>👩 老婆金幣庫</p><p class='animated-coins coin-val'>🪙 {app_data['老婆']}</p></div>", unsafe_allow_html=True)

# 🌟 Zoe 降臨
total_coins = app_data["老公"] + app_data["老婆"]
st.markdown(f'<p class="goal-text">🎯 終極目標：召喚 Zoe 降臨！(滿 200 幣)</p>', unsafe_allow_html=True)
st.progress(min(total_coins / 200.0, 1.0), text=f"能量進度：{total_coins} / 200 🪙")

if total_coins >= 200:
    st.markdown("""<div class='zoe-summon-box'>
        <h2 style='margin:0; color:white !important;'>🌟 能量全滿！Zoe 準備好降臨了！🌟</h2>
        <p style='margin:0; color:white !important;'>開啟大禮盒，雙方必得「史詩」或「傳說」級稀有裝備！</p>
    </div>""", unsafe_allow_html=True)
    if st.button("🎁 立即召喚 Zoe 並開啟大禮盒 (-200 總金幣)", use_container_width=True):
        h_deduct = int(200 * (app_data["老公"] / total_coins))
        app_data["老公"] -= h_deduct; app_data["老婆"] -= (200 - h_deduct)
        epic_leg_pool = [name for name, d in GEAR_DATA.items() if d["rarity"] in ["Epic", "Legendary"]]
        for p in ["老公", "老婆"]:
            prize = random.choice(epic_leg_pool)
            app_data["users"][p]["gear_inventory"].append(generate_gear(prize))
            app_data["history"].insert(0, {"time": datetime.now().strftime("%m/%d %H:%M"), "person": p, "chore": f"🎁 Zoe 降臨大禮：獲得稀有裝備【{prize}】", "coins": 0})
        save_data(app_data); st.balloons(); st.snow()
        st.success("🎉 Zoe 降臨啦！快去裝備庫看看你們獲得了什麼稀有神器！"); time.sleep(2); st.rerun()
st.divider()

def get_user_class_info(person):
    u = app_data["users"][person]
    c_route = CLASS_DATA[u["active_class"]]
    current_title, bonus = c_route["tiers"][0][1], c_route["tiers"][0][2]
    for lvl_req, title, bon in c_route["tiers"]:
        if u["level"] >= lvl_req: current_title, bonus = title, bon
    return current_title, bonus, c_route["chores"]

def get_monthly_visual_track(chore_name):
    prefix = datetime.now().strftime("%m/")
    h_count = sum(1 for r in app_data["history"] if r["chore"].startswith(chore_name) and r["time"].startswith(prefix) and r["person"] == "老公")
    w_count = sum(1 for r in app_data["history"] if r["chore"].startswith(prefix) and r["person"] == "老婆")
    if h_count == 0 and w_count == 0: return "<span style='color:#bbb; font-size:0.8rem;'>本月暫無紀錄</span>"
    return f"<div class='history-track'>本月印章：{'👨' * h_count}{'👩' * w_count}</div>"

def handle_dynamic_completion(person, chore, diff_level):
    u = app_data["users"][person]
    s = u["stats"]
    info = app_data["chores_info"][chore]
    gear = next((g for g in u["gear_inventory"] if g["uid"] == u["equipped_gear"]), None)
    g_data = GEAR_DATA.get(gear["name"]) if gear else None
    
    multiplier = {"Easy": 1.0, "Moderate": 1.5, "Hard": 2.0}[diff_level]
    base_reward = int(info["base"] * multiplier)
    
    is_target_gear = False
    if g_data:
        if "ALL" in g_data["target"]: is_target_gear = True
        elif "HARD_ONLY" in g_data["target"] and diff_level == "Hard": is_target_gear = True
        else:
            for t in g_data["target"]:
                if t in chore: is_target_gear = True; break

    hunter_bonus = 5 if (g_data and g_data["special"] == "max_bounty") else 0
    if not hunter_bonus:
        if not info.get("last_done"): hunter_bonus = 2
        else:
            days_passed = (datetime.now().date() - datetime.strptime(info["last_done"], "%Y-%m-%d").date()).days
            if days_passed > 1: hunter_bonus = min(days_passed - 1, 5)
            
    streak_bonus = min(info.get("streak", 0), 3) if info.get("last_person") == person else 0
    if g_data and g_data["special"] == "streak_plus_2": streak_bonus += 2
    
    _, class_bonus_amt, favored_chores = get_user_class_info(person)
    class_bonus = class_bonus_amt if ("ALL" in favored_chores or any(fav in chore for fav in favored_chores)) else 0
    gear_bonus = g_data["bonus_coins"] if is_target_gear else 0
    
    total_earned = base_reward + hunter_bonus + streak_bonus + class_bonus + gear_bonus
    
    # 🌟 每日發燒任務加成 1.5 倍
    is_hot_chore = chore in app_data["daily_hot_chores"]["chores"]
    if is_hot_chore:
        total_earned = int(total_earned * 1.5)
        st.toast("🔥 發燒任務加成！金幣與 EXP 1.5 倍！", icon="📈")
    
    if g_data and g_data["special"] == "rng_double" and random.random() < 0.10: total_earned *= 2; st.toast("✨ 黃金掃把觸發！收益翻倍！", icon="🧹")
    if g_data and g_data["special"] == "rng_double_20" and random.random() < 0.20: total_earned *= 2; st.toast("✨ 幸運扭蛋幣觸發！收益翻倍！", icon="🪙")
    if g_data and g_data["special"] == "rng_10_coins" and random.random() < 0.05: total_earned += 10; st.toast("🧭 尋寶羅盤觸發！天降 10 金幣！", icon="💰")

    # 狀態寫入
    info["streak"] = info.get("streak", 0) + 1 if info.get("last_person") == person else 1
    info["last_person"] = person
    info["last_done"] = datetime.now().strftime("%Y-%m-%d")
    
    # 統計更新
    s["chores"][chore] = s["chores"].get(chore, 0) + 1
    s["total_chores"] += 1
    s["total_earned"] += total_earned
    s["max_streak"] = max(s["max_streak"], info["streak"])
    s["max_bounty"] = max(s["max_bounty"], hunter_bonus)
    if diff_level == "Hard": s["hard_mode"] = True
    if current_hour >= 22 or current_hour < 4: s["night_owl"] = True

    app_data[person] += total_earned
    app_data["monthly_data"][person] += total_earned
    
    old_lvl = u["level"]
    exp_gained = max(1, total_earned * 2) 
    u["exp"] += exp_gained
    u["level"] = (u["exp"] // 100) + 1
    
    gear_broke = False
    if gear:
        gear["durability"] -= 1
        if gear["durability"] <= 0:
            u["gear_inventory"] = [g for g in u["gear_inventory"] if g["uid"] != gear["uid"]]
            u["equipped_gear"] = None
            gear_broke = True
            s["gear_broken"] += 1

    log_txt = f"{chore} ({diff_level})"
    if class_bonus > 0: log_txt += f" [職+{class_bonus}]"
    if gear_bonus != 0: log_txt += f" [裝{'+' if gear_bonus > 0 else ''}{gear_bonus}]"
    if gear_broke: log_txt += " 💥(碎裂)"
    app_data["history"].insert(0, {"time": datetime.now().strftime("%m/%d %H:%M"), "person": person, "chore": log_txt, "coins": total_earned})
    
    zoe_boost = 10
    if g_data and g_data["special"] == "zoe_hap_5" and is_target_gear: zoe_boost += 5
    if g_data and g_data["special"] == "zoe_hap_10": zoe_boost += 10
    
    app_data["zoe_happiness"]["score"] = min(100, app_data["zoe_happiness"]["score"] + zoe_boost)
    if app_data["zoe_happiness"]["score"] == 100:
        app_data["zoe_happiness"]["score"] = 50
        app_data["老公"] += 5; app_data["老婆"] += 5
        app_data["users"]["老公"]["stats"]["zoe_100"] += 1; app_data["users"]["老婆"]["stats"]["zoe_100"] += 1
        app_data["history"].insert(0, {"time": datetime.now().strftime("%m/%d %H:%M"), "person": "雙方", "chore": "🐾 Zoe 心情滿點獎勵", "coins": 5})

    # 世界 BOSS 推進
    if app_data["world_boss"]["active"]:
        wb = app_data["world_boss"]
        # 允許模糊比對，例如做了 "🧹 拖/掃地"，包含在 "拖/掃地" 中
        for req_chore in wb["chores_needed"]:
            if req_chore in chore and req_chore not in wb["chores_done"]:
                wb["chores_done"].append(req_chore)
                st.toast(f"🐉 對世界 BOSS 造成了打擊！(完成 {req_chore})", icon="⚔️")
                break
        
        # 檢查是否擊敗 BOSS
        if len(wb["chores_done"]) == len(wb["chores_needed"]):
            reward = wb["reward"]
            app_data["老公"] += reward; app_data["老婆"] += reward
            app_data["history"].insert(0, {"time": datetime.now().strftime("%m/%d %H:%M"), "person": "雙方", "chore": f"🐉 擊敗世界 BOSS【{wb['name']}】！", "coins": reward})
            app_data["world_boss"]["active"] = False
            st.toast(f"🎉 成功擊敗世界 BOSS！雙方各獲得 {reward} 金幣！", icon="🏆")
            st.balloons()

    if chore in app_data["weekly_bingo"]["chores"] and chore not in app_data["weekly_bingo"]["done_by"][person]:
        app_data["weekly_bingo"]["done_by"][person].append(chore)
        if len(app_data["weekly_bingo"]["done_by"][person]) == 3:
            app_data[person] += 15
            s["bingos"] += 1
            app_data["history"].insert(0, {"time": datetime.now().strftime("%m/%d %H:%M"), "person": person, "chore": "🎯 完成本週 Bingo！", "coins": 15})

    save_data(app_data)
    st.toast(f"✅ 入帳 {total_earned} 幣！(+{exp_gained} EXP)", icon="🪙")
    if gear_broke: st.error(f"💥 你的裝備【{gear['name']}】耐久度耗盡，已經碎裂了！")
    if u["level"] > old_lvl:
        lvl_bonus = (u["level"] - old_lvl) * 10; app_data[person] += lvl_bonus; save_data(app_data)
        st.toast(f"🎉 {person} 升級至 Level {u['level']}！獲得 {lvl_bonus} 金幣！", icon="⭐")
        st.balloons()
    
    check_achievements(person)
    time.sleep(1.2 if gear_broke else 0.8); st.rerun()

# --- 6. 功能分頁 ---
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["💰 任務", "⚔️ RPG", "🛍️ 抽卡", "⚒️ 鐵匠", "📜 紀錄", "🛠️ 管理"])

with tab1:
    b_chores = app_data["weekly_bingo"]["chores"]
    st.markdown(f"<div class='bingo-box'><p style='margin:0; font-weight:bold; color:#1abc9c;'>🎯 本週 Bingo 組合 (獎勵 15 🪙)</p>"
                f"<p style='margin:0; font-size:0.85rem; color:#555;'>1. {b_chores[0]} | 2. {b_chores[1]} | 3. {b_chores[2]}</p></div>", unsafe_allow_html=True)

    for chore, info in app_data["chores_info"].items():
        is_hot = chore in app_data["daily_hot_chores"]["chores"]
        wrapper_class = "hot-chore" if is_hot else ""
        
        st.markdown(f"<div class='{wrapper_class}'>", unsafe_allow_html=True)
        c_info, c_actions = st.columns([1.1, 0.9])
        hunter_bounty = 0
        if not info.get("last_done"): hunter_bounty = 2
        else:
            days_passed = (datetime.now().date() - datetime.strptime(info["last_done"], "%Y-%m-%d").date()).days
            if days_passed > 1: hunter_bounty = min(days_passed - 1, 5)
        streak = info.get("streak", 0)
        
        bounty_html = f"<span class='badge-base bg-red'>🔥 賞金 +{hunter_bounty}</span>" if hunter_bounty > 0 else ""
        streak_html = f"<span class='badge-base bg-orange'>🔥x{streak}</span>" if streak > 1 else ""
        hot_html = f"<span class='badge-base bg-blue'>🌟 發燒 1.5x</span>" if is_hot else ""
        visual_track = get_monthly_visual_track(chore)
        
        with c_info:
            st.markdown(f"<div><span class='chore-name'>{chore}</span><br><span class='badge-base bg-gold'>Base: {info['base']}</span>{bounty_html}{streak_html}{hot_html}</div>", unsafe_allow_html=True)
            st.markdown(visual_track, unsafe_allow_html=True)
            
        with c_actions:
            diff = st.select_slider("難度", options=["Easy", "Moderate", "Hard"], value="Easy", key=f"sl_{chore}", label_visibility="collapsed")
            diff_bonus = int(info["base"] * {"Easy": 1.0, "Moderate": 1.5, "Hard": 2.0}[diff]) - info["base"]
            if diff_bonus > 0: st.markdown(f"<div style='text-align:center; font-size:0.75rem; color:#e74c3c; font-weight:bold; margin-top:-10px; margin-bottom:5px;'>✨ 加成: +{diff_bonus} 🪙</div>", unsafe_allow_html=True)
            
            cb1, cb2 = st.columns(2)
            if cb1.button("👨", key=f"h_{chore}", use_container_width=True): handle_dynamic_completion("老公", chore, diff)
            if cb2.button("👩", key=f"w_{chore}", use_container_width=True): handle_dynamic_completion("老婆", chore, diff)
        st.markdown("</div>", unsafe_allow_html=True)

with tab2:
    for person, icon in [("老公", "👨"), ("老婆", "👩")]:
        u = app_data["users"][person]
        title, bonus, _ = get_user_class_info(person)
        selected_title = u.get("active_title", "新手村村民 🐣")
        
        inv_emojis = " ".join([get_emoji(item) for item in u["inventory"]]) if u["inventory"] else "空"
        gear_emojis = " ".join([f"{get_emoji(g['name'])}({g['durability']})" for g in u["gear_inventory"]]) if u["gear_inventory"] else "空"
        
        st.markdown(f"""<div class='profile-card'>
            <h3 style='margin:0;'>{icon} {person}</h3>
            <p style='margin:0; font-size:0.9rem; color:#888; font-weight:bold;'>職業: {title} | 稱號: <span style='color:#B8860B;'>{selected_title}</span></p>
            <div class='inventory-emojis'>🎒 消耗品: {inv_emojis}</div>
            <div class='inventory-emojis'>🛡️ 裝備庫: {gear_emojis}</div>
        </div>""", unsafe_allow_html=True)
        
        st.progress((u['exp'] % 100) / 100.0, text=f"⭐ Level {u['level']} ({u['exp'] % 100}/100 EXP 升級)")
        
        with st.expander(f"🛠️ {person} 的設定 (換稱號/職業/裝備)"):
            new_title = st.selectbox("裝備成就稱號", u["achievements"], index=u["achievements"].index(u["active_title"]) if u["active_title"] in u["achievements"] else 0, key=f"ttl_{person}")
            new_class = st.selectbox("切換職業路線", list(CLASS_DATA.keys()), index=list(CLASS_DATA.keys()).index(u["active_class"]), key=f"cls_{person}")
            gear_opts = [None] + u["gear_inventory"]
            def format_gear(g): return "無裝備" if g is None else f"{g['name']} (耐久度: {g['durability']}/{g['max_durability']})"
            curr_idx = next((i for i, g in enumerate(gear_opts) if g and g["uid"] == u["equipped_gear"]), 0)
            new_gear = st.selectbox("穿戴裝備", gear_opts, index=curr_idx, format_func=format_gear, key=f"gr_{person}")

            if st.button("💾 儲存設定", key=f"sv_{person}", use_container_width=True):
                u["active_title"] = new_title; u["active_class"] = new_class; u["equipped_gear"] = new_gear["uid"] if new_gear else None
                save_data(app_data); st.rerun()
                
            if u["last_daily"] != current_date_str:
                if st.button(f"🎁 領取今日配給金", key=f"daily_{person}", use_container_width=True):
                    bonus = random.randint(1, 3); app_data[person] += bonus; u["last_daily"] = current_date_str
                    app_data["history"].insert(0, {"time": datetime.now().strftime("%m/%d %H:%M"), "person": person, "chore": "🎁 每日登入配給", "coins": bonus})
                    save_data(app_data); st.rerun()

        # 🎁 撩人贈禮系統
        if u["inventory"] or u["gear_inventory"]:
            with st.expander(f"🎁 送禮物給伴侶"):
                partner = "老婆" if person == "老公" else "老公"
                gift_type = st.radio("選擇類型", ["消耗品", "裝備"], key=f"gtype_{person}", horizontal=True)
                
                if gift_type == "消耗品" and u["inventory"]:
                    gift_item = st.selectbox("選擇要送的消耗品", u["inventory"], key=f"gitem_{person}")
                elif gift_type == "裝備" and u["gear_inventory"]:
                    gift_item = st.selectbox("選擇要送的裝備", u["gear_inventory"], format_func=format_gear, key=f"ggear_{person}")
                else:
                    gift_item = None
                    st.info("此分類下沒有物品可以贈送喔！")
                
                gift_msg = st.selectbox("附上撩人/有趣的話語", GIFT_MSGS, key=f"gmsg_{person}")
                
                if gift_item and st.button(f"💌 寄送給 {partner}", key=f"send_{person}", use_container_width=True):
                    if gift_type == "消耗品":
                        u["inventory"].remove(gift_item)
                        app_data["users"][partner]["inventory"].append(gift_item)
                        log_name = gift_item
                    else:
                        if gift_item["uid"] == u["equipped_gear"]: u["equipped_gear"] = None
                        u["gear_inventory"] = [g for g in u["gear_inventory"] if g["uid"] != gift_item["uid"]]
                        app_data["users"][partner]["gear_inventory"].append(gift_item)
                        log_name = gift_item["name"]
                        
                    app_data["history"].insert(0, {"time": datetime.now().strftime("%m/%d %H:%M"), "person": person, "chore": f"🎁 贈禮給 {partner}：{log_name} (留言：{gift_msg})", "coins": 0})
                    save_data(app_data); st.success(f"禮物已成功送達 {partner} 的背包！"); time.sleep(1); st.rerun()

        if u["inventory"]:
            with st.expander(f"🎒 使用 {person} 的消耗品"):
                for idx, item in enumerate(u["inventory"]):
                    ic1, ic2 = st.columns([3, 1])
                    ic1.write(f"▪️ {item}")
                    if ic2.button("使用", key=f"use_{person}_{idx}"):
                        used_item = u["inventory"].pop(idx)
                        app_data["history"].insert(0, {"time": datetime.now().strftime("%m/%d %H:%M"), "person": person, "chore": f"✨ 使用了：{used_item}", "coins": 0})
                        save_data(app_data); st.rerun()
        st.markdown("<br>", unsafe_allow_html=True)

with tab3:
    st.markdown("""<div class='gacha-box'>
        <h2 style='margin:0; color:white !important;'>🎁 神秘盲盒 (15 🪙)</h2>
        <p style='margin:0; font-size:0.9rem;'>可能抽出消耗品或 31 種擁有耐久度的附魔裝備！</p>
    </div>""", unsafe_allow_html=True)
    
    gc1, gc2 = st.columns(2)
    def pull_gacha(person):
        if app_data[person] >= 15:
            app_data[person] -= 15; app_data["users"][person]["stats"]["gacha_pulls"] += 1
            if random.random() < 0.40:
                prize = random.choice(["免做家事金牌 🛡️", "跑腿券 🏃", "搥背券 💆", "謝謝惠顧 (Zoe 的飛吻 💋)"])
                if "謝謝惠顧" not in prize: app_data["users"][person]["inventory"].append(prize)
            else:
                r_roll = random.random()
                if r_roll < 0.05: rarity = "Legendary"
                elif r_roll < 0.20: rarity = "Epic"
                elif r_roll < 0.50: rarity = "Rare"
                else: rarity = "Common"
                pool = [name for name, d in GEAR_DATA.items() if d["rarity"] == rarity]
                prize = random.choice(pool)
                app_data["users"][person]["gear_inventory"].append(generate_gear(prize))

            app_data["history"].insert(0, {"time": datetime.now().strftime("%m/%d %H:%M"), "person": person, "chore": f"🎰 盲盒獲得：{prize}", "coins": -15})
            save_data(app_data); check_achievements(person)
            st.success(f"🎉 抽中：{prize}！"); time.sleep(1.5); st.rerun()
        else: st.error("餘額不足！")

    if gc1.button("👨 抽盲盒 (-15🪙)", use_container_width=True): pull_gacha("老公")
    if gc2.button("👩 抽盲盒 (-15🪙)", use_container_width=True): pull_gacha("老婆")
    
    st.divider()
    st.markdown("<p style='font-weight:bold; color:#B8860B !important;'>🛒 消耗品快閃店 (每日隨機一件半價)</p>", unsafe_allow_html=True)
    for item, base_price in STORE_ITEMS.items():
        is_flash = (item == flash_item)
        price = base_price // 2 if is_flash else base_price
        flash_badge = "<span class='badge-base bg-red'>⚡ 半價快閃</span>" if is_flash else ""
        st.markdown(f"<div style='background: white; padding: 10px; border-radius: 8px; border: 1px solid #eee; margin-bottom: 5px;'>"
                    f"<span style='font-weight:bold;'>{item}</span> (💰 {price}) {flash_badge}</div>", unsafe_allow_html=True)
        bc1, bc2 = st.columns(2)
        def buy_item(person, item, price):
            if app_data[person] >= price:
                app_data[person] -= price; app_data["users"][person]["inventory"].append(item)
                app_data["users"][person]["stats"]["store_bought"] += 1
                app_data["history"].insert(0, {"time": datetime.now().strftime("%m/%d %H:%M"), "person": person, "chore": f"🛒 購買：{item}", "coins": -price})
                save_data(app_data); check_achievements(person); st.success("購買成功！"); time.sleep(0.8); st.rerun()
            else: st.error("餘額不足！")
            
        if bc1.button(f"👨 購買", key=f"b_h_{item}", use_container_width=True): buy_item("老公", item, price)
        if bc2.button(f"👩 購買", key=f"b_w_{item}", use_container_width=True): buy_item("老婆", item, price)

with tab4:
    st.markdown("<h3 style='color:#B8860B !important;'>⚒️ 鐵匠鋪</h3>", unsafe_allow_html=True)
    
    # 區塊 1: 修復裝備
    st.markdown("#### 🔧 修復裝備 (花費 20 🪙)")
    st.markdown("<p style='font-size:0.9rem; color:#666;'>可以將裝備的耐久度補滿！</p>", unsafe_allow_html=True)
    repair_person = st.radio("誰要修復裝備？", ["老公", "老婆"], horizontal=True, key="rep_person")
    repair_inv = [g for g in app_data["users"][repair_person]["gear_inventory"] if g["durability"] < g["max_durability"]]
    
    if repair_inv:
        gear_to_repair = st.selectbox("選擇要修復的裝備", repair_inv, format_func=lambda g: f"{g['name']} (目前: {g['durability']}/{g['max_durability']})")
        if st.button("🔨 進行修復 (-20🪙)", use_container_width=True):
            if app_data[repair_person] >= 20:
                app_data[repair_person] -= 20
                gear_to_repair["durability"] = gear_to_repair["max_durability"]
                app_data["history"].insert(0, {"time": datetime.now().strftime("%m/%d %H:%M"), "person": repair_person, "chore": f"🔧 鐵匠鋪修復：{gear_to_repair['name']}", "coins": -20})
                save_data(app_data); st.success("修復成功！裝備煥然一新！"); time.sleep(1); st.rerun()
            else: st.error("餘額不足 20 金幣！")
    else: st.info(f"💡 {repair_person} 目前沒有需要修復的破損裝備。")
    
    st.divider()
    
    # 區塊 2: 合成爐
    st.markdown("#### 🧪 煉金合成爐")
    st.markdown("<p style='font-size:0.9rem; color:#666;'>選擇 3 件<b>普通 (Common)</b>裝備，必定煉成 1 件<b>稀有 (Rare)</b>裝備！</p>", unsafe_allow_html=True)
    merge_person = st.radio("誰要進行合成？", ["老公", "老婆"], horizontal=True, key="merge_person")
    
    common_gears = [g for g in app_data["users"][merge_person]["gear_inventory"] if GEAR_DATA[g["name"]]["rarity"] == "Common"]
    if len(common_gears) >= 3:
        selected_to_merge = st.multiselect("選擇 3 件祭品", common_gears, format_func=lambda g: f"{g['name']} ({g['uid'][:4]})", max_selections=3)
        if len(selected_to_merge) == 3:
            if st.button("🔥 立即合成", use_container_width=True):
                # 刪除祭品
                u_inv = app_data["users"][merge_person]["gear_inventory"]
                remove_uids = [g["uid"] for g in selected_to_merge]
                app_data["users"][merge_person]["gear_inventory"] = [g for g in u_inv if g["uid"] not in remove_uids]
                # 確保卸下
                if app_data["users"][merge_person]["equipped_gear"] in remove_uids: app_data["users"][merge_person]["equipped_gear"] = None
                
                # 隨機稀有
                rare_pool = [name for name, d in GEAR_DATA.items() if d["rarity"] == "Rare"]
                new_rare = random.choice(rare_pool)
                app_data["users"][merge_person]["gear_inventory"].append(generate_gear(new_rare))
                
                app_data["history"].insert(0, {"time": datetime.now().strftime("%m/%d %H:%M"), "person": merge_person, "chore": f"🧪 煉金合成，獲得稀有裝備：{new_rare}", "coins": 0})
                save_data(app_data); st.balloons(); st.success(f"合成成功！獲得稀有神器：【{new_rare}】！"); time.sleep(2); st.rerun()
    else: st.info(f"💡 {merge_person} 背包內的普通裝備不足 3 件，無法進行合成。")

with tab5:
    for i, r in enumerate(app_data["history"][:40]):
        col_text, col_undo = st.columns([3.5, 1.5])
        icon = "👨" if r["person"] == "老公" else "👩" if r["person"] == "老婆" else "🐾"
        coin_color = "#e74c3c" if r["coins"] < 0 else "#B8860B"
        sign = "" if r["coins"] <= 0 else "+"
        
        col_text.markdown(f"<span style='color:#888; font-size:0.75rem;'>{r['time']}</span><br><span style='color:#333 !important; font-size:0.9rem;'>{icon} **{r['person']}** {r['chore']}</span> <span style='color:{coin_color}; font-weight:bold; font-size:0.9rem;'>🪙 {sign}{r['coins']}</span>", unsafe_allow_html=True)
        if col_undo.button("退回", key=f"del_{i}", use_container_width=True):
            if r['person'] in ["老公", "老婆"]: app_data[r['person']] -= r['coins']
            app_data["history"].pop(i); save_data(app_data); st.rerun()
        st.markdown("<div style='border-bottom:1px solid #eee; margin-bottom:10px;'></div>", unsafe_allow_html=True)

with tab6:
    st.subheader("🐉 手動召喚世界 BOSS")
    st.markdown("<p style='font-size:0.85rem; color:#666;'>(例如：過年大掃除魔王、岳母突襲檢查)</p>", unsafe_allow_html=True)
    custom_boss_name = st.text_input("輸入 BOSS 名稱")
    custom_boss_chores = st.multiselect("選擇通關需要的任務", list(app_data["chores_info"].keys()))
    custom_boss_reward = st.number_input("通關獎勵金幣", min_value=10, value=100)
    
    if st.button("🚨 立即發佈世界 BOSS！", use_container_width=True):
        if not custom_boss_name or not custom_boss_chores:
            st.error("請填寫 BOSS 名稱並至少選擇一個任務！")
        elif app_data["world_boss"]["active"]:
            st.error("目前已經有活躍的世界 BOSS，請先擊敗牠！")
        else:
            app_data["world_boss"] = {"active": True, "name": custom_boss_name, "chores_needed": custom_boss_chores, "chores_done": [], "reward": custom_boss_reward}
            save_data(app_data); st.success(f"世界 BOSS【{custom_boss_name}】已降臨！"); time.sleep(1); st.rerun()

    st.divider()

    st.subheader("✨ 新增自訂家事")
    new_chore_name = st.text_input("家事名稱 (例如: 🧼 擦桌子)", placeholder="請輸入家事名稱...")
    new_chore_base = st.number_input("基礎獎勵金幣", min_value=1, max_value=50, value=3)
    
    if st.button("➕ 新增至任務列表", use_container_width=True):
        if not new_chore_name.strip(): st.error("請輸入有效的家事名稱！")
        elif new_chore_name in app_data["chores_info"]: st.error("此家事已存在！")
        else:
            app_data["chores_info"][new_chore_name] = {"base": int(new_chore_base), "frequent": False, "last_done": None, "last_person": None, "streak": 0}
            save_data(app_data); st.success(f"成功新增任務：{new_chore_name}！"); time.sleep(0.5); st.rerun()
            
    st.divider(); st.subheader("🗑️ 刪除自訂家事")
    custom_chores = [c for c in app_data["chores_info"].keys() if c not in DEFAULT_CHORES_INFO]
    
    if custom_chores:
        chore_to_delete = st.selectbox("選擇要移除的自訂家事", custom_chores)
        if st.button("❌ 確實刪除此任務", use_container_width=True):
            del app_data["chores_info"][chore_to_delete]; save_data(app_data); st.success(f"已成功移除：{chore_to_delete}"); time.sleep(0.5); st.rerun()
    else: st.info("💡 目前沒有自訂家事。預設的系統家事受到保護，無法被刪除。")