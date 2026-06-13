import streamlit as st
from core.db import init_db
from core.auth import login, register


init_db()

st.set_page_config(page_title="Ingesta", layout="wide", initial_sidebar_state="expanded")
st.title("🧪 Ingesta")
st.header("A Data Ingestion and Validation Platform")

# =========================
# 卡片组件
# =========================
def render_card(features, cols_per_row=3):
    with st.container():
        for i in range(0, len(features), cols_per_row):
            cols = st.columns(cols_per_row)
            for col, feature in zip(cols, features[i:i+cols_per_row]):
              with col:
                st.markdown(f"""
                  <div style="
                    border:1px solid #ddd; 
                    border-radius:10px; 
                    padding:15px; 
                    display:flex; 
                    align-items:flex-start; 
                    height:180px; 
                    background-color:#f9f9f9;
                    overflow:hidden;
                    ">
                    <div style="font-size:40px; margin-right:15px;">{feature['icon']}</div>
                    <div style="flex:1; display:flex; flex-direction:column; justify-content:space-between;">
                        <h4 style="margin:0;">
                            <a href="{feature['url']}" style="text-decoration:none; color:#000;">
                                {feature['title']}
                            </a>
                        </h4>
                        <p style="margin:0; font-size:16px; color:#555; overflow-y:auto;">{feature['description']}</p>
                    </div>
                  </div>""", unsafe_allow_html=True)
            st.markdown("")

# =========================
# 模块定义（产品级）
# =========================
feature_groups = {
    "数据准备与治理": [
        {
          "title": "数据生成",
          "icon": "🔢",
          "url": "/数据生成",
          "description": "类似于真实场景的模拟数据可以帮助你更好地实现产品性能测试、演示环境搭建、BI报表设计和Demo搭建"
        },
        {
          "title": "数据校验",
          "icon": "🚧",
          "url": "/数据校验",
          "description": "自定义字段级、表级校验规则，批量校验数据质量、确认数据规范性"
        }
    ],}


# -----------------------------
# SESSION
# -----------------------------
if "user" not in st.session_state:
    st.session_state.user = None

# =============================
# LOGIN / REGISTER
# =============================
if not st.session_state.user:
    tab1, tab2 = st.tabs(["Login", "Register"])

    with tab1:
        u = st.text_input("Username", "Ingesta")
        p = st.text_input("Password", "Ingesta", type="password")

        # u = st.text_input("Username", "Please enter username")
        # p = st.text_input("Password", "Please enter password", type="password")

        if st.button("Login"):
            user = login(u, p)
            if user:
                st.session_state.user = user
                st.rerun()
            else:
                st.error("Invalid login")

    with tab2:
        ru = st.text_input("New Username")
        rp = st.text_input("New Password", type="password")

        if st.button("Register"):
            if register(ru, rp):
                st.success("Registered successfully")
            else:
                st.error("User already exists")

else:
    st.sidebar.success(f"User: {st.session_state.user[1]}")

    # Logout button
    if st.sidebar.button("🚪 Logout", type="secondary"):
        st.session_state.user = None
        st.rerun()

    for group_name, features in feature_groups.items():
            st.markdown(f"### {group_name}")
            render_card(features, cols_per_row=3)

st.divider()

st.markdown(
    """
    <div style="text-align: center; margin-top: 50px; color: gray; font-size: 16px;">
        Copyright©2026 南京秉智数据科技有限公司
    </div>
    """,
    unsafe_allow_html=True
)
