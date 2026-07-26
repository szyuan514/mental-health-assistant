import streamlit as st
from openai import OpenAI
from risk import detect_risk, CRISIS_RESPONSE

API_KEY = "sk-30adfeead85647148d24a16e37f399c0"
APPOINTMENT_URL = "http://xl.psyedu.cn/gzu/login"

st.set_page_config(page_title="AI心理陪伴助手", page_icon="❤️")
st.title("❤️ AI心理陪伴助手")

@st.dialog("🔐 登录提示")
def show_login_tips():
    st.markdown("""
    **请使用以下信息登录学校心理中心官网：**
    
    - 登录地址：`http://xl.psyedu.cn/gzu/login`
    - 账号：学号
    - 初始密码：`Gdpc` + 出生日期（例如 `Gdpc20010203`）
    
    **若提示密码错误，请尝试：**
    - `Gdpc` + 个人学号（例如 `Gdpc322078123156`）
    - `Gdpc12345`
    - 或使用你之前修改过的密码
    """)
    st.link_button("✅ 我知道了，去登录", APPOINTMENT_URL, type="primary")

client = OpenAI(api_key=API_KEY, base_url="https://api.deepseek.com")

st.markdown("""
<style>
    /* 全局背景 */
    .stApp > div:first-child, .main > div,
    [data-testid="stChatMessageListContainer"],
    [data-testid="stChatMessage"] {
        background-color: #FFF5E6 !important;
    }

    /* 侧边栏 */
    section[data-testid="stSidebar"] {
        background-color: #F0F0F0 !important;
    }

    /* 消息气泡圆角 + 边框 */
    [data-testid="stChatMessageContent"] {
        border-radius: 18px;
        padding: 10px;
        border: 1px solid #E0C9A6;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05);
    }

    /* 用户气泡 */
    [data-testid="stChatMessage"][kind="user"] [data-testid="stChatMessageContent"] {
        background-color: #E6F7FF !important;
    }

    /* AI 气泡 */
    [data-testid="stChatMessage"][kind="assistant"] [data-testid="stChatMessageContent"] {
        background-color: #FFF0E0 !important;
    }

    /* 输入框区域背景 */
    .stChatInputContainer, .stChatInputContainer > div,
    .stChatInputContainer > div > div {
        background-color: #FFF5E6 !important;
    }
    .stChatInputContainer textarea {
        background-color: #FFFFFF !important;
        border-radius: 25px !important;
        border: 1px solid #E0E0E0 !important;
    }

    /* 顶部栏、底部保持 */
    header, .stApp footer, .stBottom {
        background-color: #FFF5E6 !important;
    }

    /* 隐藏默认菜单和页脚 */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    /* 强制用户消息头像在右，消息靠右 */
    [data-testid="stChatMessage"][kind="user"] {
        flex-direction: row-reverse !important;
        justify-content: flex-end !important;
    }

    /* 强制助手消息头像在左，消息靠左 */
[   data-testid="stChatMessage"][kind="assistant"] {
        flex-direction: row !important;
        justify-content: flex-start !important;
    }

    /* 确保消息气泡内部文字对齐正常 */
    [data-testid="stChatMessageContent"] {
        text-align: left !important;
    }
    
</style>
""", unsafe_allow_html=True)

# ========== 初始化会话状态 ==========
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "你是一个温和的心理陪伴助手。"},
        {"role": "assistant", "content": "你好，我是你的 AI 心理陪伴助手。你今天心情怎么样？"}
    ]
    st.session_state.asked_for_appointment = False
    st.session_state.refused_hotline = False
# ========== 侧边栏==========
with st.sidebar:
    st.markdown("### 📞 紧急求助")
    st.markdown("**全国心理援助热线：12356**")
    if st.button("🏥 学校心理中心预约"):
        show_login_tips()
    st.caption("⚠️ 我是AI助手，不能替代专业心理咨询。")
    
    st.markdown("---")
    st.markdown("### 🎨 个性化设置")
    st.markdown("**你的头像**")
    user_avatar_mode = st.radio(
        "选择方式",
        options=["使用预设", "自定义"],
        key="user_avatar_mode",
        horizontal=True
    )
    
    if user_avatar_mode == "使用预设":
        user_avatar = st.selectbox(
            "选择预设头像",
            options=["💬", "🗣️", "📝", "🧑", "👩", "🙋", "🐱", "⭐", "🌸", "💙"],
            index=0,
            key="user_avatar_preset",
            label_visibility="collapsed"
        )
    else:
        user_avatar = st.text_input(
            "输入自定义头像",
            value="💬",
            max_chars=2,
            key="user_avatar_custom",
            help="输入任意 emoji 或文字，如 😊、🐱、🌟",
            label_visibility="collapsed"
        )
    
    st.markdown("---")

    st.markdown("**AI 的头像**")
    ai_avatar_mode = st.radio(
        "选择方式",
        options=["使用预设", "自定义"],
        key="ai_avatar_mode",
        horizontal=True
    )
    
    if ai_avatar_mode == "使用预设":
        ai_avatar = st.selectbox(
            "选择预设头像",
            options=["🤔", "🤖", "🌸", "💙", "⭐", "🐱", "🦊", "💬"],
            index=0,
            key="ai_avatar_preset",
            label_visibility="collapsed"
        )
    else:
        ai_avatar = st.text_input(
            "输入自定义头像",
            value="🤔",
            max_chars=2,
            key="ai_avatar_custom",
            help="输入任意 emoji 或文字，如 🌸、💙、🦊",
            label_visibility="collapsed"
        )
    
# ========== 显示历史消息 ==========
for msg in st.session_state.messages:
    if msg["role"] == "user":
        with st.chat_message("user", avatar=user_avatar):
            st.write(msg["content"])
    elif msg["role"] == "assistant":
        with st.chat_message("assistant", avatar=ai_avatar):
            st.write(msg["content"])

user_input = st.chat_input("你说，我在听")

if user_input:
    with st.chat_message("user", avatar=user_avatar):
        st.write(user_input)
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    with st.status("🤔 正在倾听你的心事...", expanded=False) as status:
        risk_level = detect_risk(user_input, client)
        
        if risk_level == 'high':
          response = client.chat.completions.create(
            model="deepseek-chat",
            messages=st.session_state.messages
    )
          empathy_reply = response.choices[0].message.content
          resource_message = CRISIS_RESPONSE
    
          reply = empathy_reply + resource_message
          st.session_state.refused_hotline = True

        else:
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=st.session_state.messages
            )
            reply = response.choices[0].message.content
            if risk_level == 'medium':
                reply += "\n\n---\n💙 如果心里太难受，可以拨打 **12356** 心理援助热线。"
        
        status.update(label="✅ 回答已准备好", state="complete")
    
    st.session_state.messages.append({"role": "assistant", "content": reply})

    with st.chat_message("assistant", avatar=ai_avatar):
        st.write(reply)
        if risk_level == 'medium' and not st.session_state.asked_for_appointment:
            col1, col2 = st.columns(2)
            with col1:
                if st.button("📞 需要联系学校心理中心", key="need_appointment"):
                    show_login_tips()
                    st.session_state.asked_for_appointment = True
                    st.rerun()
            with col2:
                if st.button("❌ 不需要，继续对话", key="no_appointment"):
                    st.session_state.asked_for_appointment = True
                    st.rerun()
        elif risk_level == 'high':
            st.warning("如果你需要立即联系学校心理中心，请点击下方按钮：")
            if st.button("立即预约", key="high_risk_button"):
                show_login_tips()
            if st.button("❌ 不再显示资源信息", key="dismiss_high"):
                st.session_state.refused_hotline = True
                st.rerun()

    st.session_state.messages.append({"role": "assistant", "content": reply})
