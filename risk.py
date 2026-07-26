CRISIS_HOTLINE_1 = "12356"
CRISIS_HOTLINE_2 = "96525"
""
HIGH_RISK_KEYWORDS = [
    '自杀', '自残', '跳楼', '割腕', '不想活了',
    '活着没意思', '结束生命', '不想再活下去了', '死了算了',
    '轻生', '杀了我自己'
]

AMBIGUOUS_KEYWORDS = [
    '死了', '活不下去', '撑不下去了', '受不了了',
    '崩溃了', '绝望', '没救了', '想死', '担心', '害怕',
    '紧张', '心慌', '睡不着', '停不下来', '控制不住',
    '突然心慌', '喘不上气', '要死了', '失控',
    '听到声音', '有人说话', '被跟踪', '被控制', '幻觉', '妄想',
    '不真实', '像梦', '机械', '灵魂出窍',
    '不懂别人', '社交困难', '重复动作', '固定模式',
    '几天不睡', '精力旺盛', '跌入谷底', '情绪波动大',
    '反复检查', '反复想', '控制不住', '洁癖',
    '暴食', '催吐', '怕胖', '不吃东西',
    '噩梦', '闪回', '回避', '惊醒'
]

ANXIETY_KEYWORDS = []
PANIC_KEYWORDS = []
PSYCHOSIS_KEYWORDS = []
DEPERSONALIZATION_KEYWORDS = []
AUTISM_KEYWORDS = []
BIPOLAR_KEYWORDS = []
OCD_KEYWORDS = []
ED_KEYWORDS = []
PTSD_KEYWORDS = []


CRISIS_RESPONSE = f"""
我听到你现在非常痛苦。

⚠️ 我不是专业心理咨询师，无法提供专业帮助。
请你立刻联系以下专业机构：

📞 广州市阳光成功热线：{CRISIS_HOTLINE_2}(24小时免费)
📞 全国心理援助热线：{CRISIS_HOTLINE_1}(24小时免费)
🏫 也可以点击侧边的预约按钮联系学校心理健康教育与咨询中心

如果你现在有伤害自己的冲动，请立即拨打 110 或告诉身边的人。
你不需要一个人承受这些。
"""

import re

def is_high_risk_keyword(text):
    text_lower = text.lower()
    for keyword in HIGH_RISK_KEYWORDS:
        if keyword in text_lower:
            return True
    return False

def is_ambiguous_keyword(text):
    text_lower = text.lower()
    for keyword in AMBIGUOUS_KEYWORDS:
        if keyword in text_lower:
            return True
    return False

def get_risk_prompt(user_input):
    """构造AI判断风险用的提示词"""
    return f"""判断下面这句话是"夸张发泄"还是"真实危机"。
你是一名三甲医院心理科的高级主任医师兼心理咨询专家。请根据以下规则判断用户的一句话是"夸张发泄"(low)还是"真实危机"(high)还是"中度"(medium)。

用户说的是："{user_input}"
【判断规则】
1. 如果句子中同时出现【具体的外部压力源】（作业/考试/工作/吵架/被骂/迟到/打游戏输了等）和【死亡相关词】（想死/死了算了/不想活），则判定为 low(夸张发泄)。
2. 如果句子中【没有】具体外部压力源，而是【虚无性表达】（活着没意思、人生无望、一切都没有意义）或【自我否定】（我是废物、没人需要我），则判定为 high。
3. 如果只有【死亡相关词】但没有任何原因或虚无表达，例如单纯的“我好想死”，则判定为 medium(中度)。
4. 如果句子中有【告别语】（照顾好自己、来世再见）或【具体方法】（割腕、跳楼），直接 high。

夸张发泄：有具体原因（如作业多、考试差、吵架），只是发泄情绪，不是真想死。
例子："我真是要死了，作业这么多" 返回low

真实危机：没有具体原因的绝望，或自我否定，或告别语言，或想结束生命。
例子："我不想活了，活着没意义" 返回 high

只返回一个词:low、medium 或 high。

不要返回其他内容。"""

def judge_by_ai(user_input, client):
    try:
        response = client.chat.completions.create(
            model="deepseek-v4-pro",
            messages=[{"role": "user", "content": get_risk_prompt(user_input)}],
            temperature=0
        )
        result = response.choices[0].message.content.strip().lower()
        if result in ['high', 'medium', 'low']:
            return result
        return 'medium'
    except:
        return 'medium'

def detect_risk(user_input, client=None):
    has_high = is_high_risk_keyword(user_input)
    has_ambiguous = is_ambiguous_keyword(user_input)
    
    if not has_high and not has_ambiguous:
        return 'low'
    
    if client is not None:
        return judge_by_ai(user_input, client)
    
    if has_high:
        return 'high'
    return 'medium'
