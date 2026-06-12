import streamlit as st
import pandas as pd
import json
import os
import time
from core.data_generator import generate_data


st.set_page_config(page_title="Ingesta", layout="wide", initial_sidebar_state="expanded")
st.header("Data Generation Tool")

OUTPUT_DIR = "outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)
TEMPLATE_FILE = f"{OUTPUT_DIR}/saved_templates.json"

# 初始化 Session State
if 'templates' not in st.session_state:
    if os.path.exists(TEMPLATE_FILE):
        with open(TEMPLATE_FILE, "r", encoding="utf-8") as f:
            st.session_state.templates = json.load(f)
    else:
        st.session_state.templates = {}

if 'tasks' not in st.session_state:
    st.session_state.tasks = []

if 'current_config' not in st.session_state:
    # 默认给几行空配置
    df = pd.DataFrame({
        "行号": [1, 2, 3],
        "字段名": ["姓名", "年龄", "性别"],
        "数据类型": ["person_name", "age", "gender"],
        "显示格式": ["", "", ""], 
        "最小值/起始时间": ["", "18", ""],
        "最大值/结束时间": ["", "65", ""],
        "自定义值列表(英文逗号分隔)": ["", "", ""],
        "缺失率(%)": [0, 0, 0]
    })
    st.session_state.current_config = df

# 映射中英文类型名称，方便用户理解
TYPE_MAPPING = {
    "seq_id": "ID", "udf_sequence": "自定义值列表", 
    "person_name": "姓名", "age": "年龄", "gender": "性别",
    "phone_number": "手机号", "email": "邮箱", 
    "number": "整数", "float_number": "浮点数", "boolean": "布尔值", 
    "date_between": "日期", "datetime_between": "时间", 
    "company": "公司", "address": "详细地址",
}

REVERSE_TYPE_MAPPING = {v: k for k, v in TYPE_MAPPING.items()}
AVAILABLE_TYPES = list(TYPE_MAPPING.values())

def save_templates():
    with open(TEMPLATE_FILE, "w", encoding="utf-8") as f:
        json.dump(st.session_state.templates, f, ensure_ascii=False, indent=4)

# ================= 侧边栏路由 =================
if "page" not in st.session_state:
    st.session_state.page = "数据生成器"

page = st.sidebar.radio(
    "导航",
    ["数据生成器", "模板管理", "任务管理"],
    # index=["数据生成器", "模板管理", "任务管理"].index(st.session_state.get("page", "数据生成器")),
    key="dg_page"
)

# ================= 页面1：数据生成器 =================
if page == "数据生成器":
    st.subheader("✨ 数据生成器")
    st.write("通过表格快速添加所需字段，配置数据类型与约束条件。")

    # 1. 动态表格编辑器
    edited_df = st.data_editor(
        st.session_state.current_config,
        num_rows="dynamic",
        width='stretch',
        hide_index=True, # 隐藏物理索引
        column_config={
            "行号": st.column_config.NumberColumn("行号", disabled=True, width=30, format="%d"),
            "字段名": st.column_config.TextColumn("字段名 (必填)", required=True),
            "数据类型": st.column_config.SelectboxColumn(
                "数据类型(必填)", options=list(TYPE_MAPPING.keys()), required=True,
                default=list(TYPE_MAPPING.keys())[0],  # 默认选第一个类型
                help="支持：person_name, age, number, date_between, 自定义枚举值 等"
            ),
            "缺失率(%)": st.column_config.NumberColumn("缺失率(%)", min_value=0, max_value=100, default=0, 
                step=5, width=60)
        }
    )

    st.session_state.current_config = edited_df
    
    # 2. 生成与保存控制区
    row_num = st.number_input("生成行数", min_value=1, value=10, step=100)
    col1, col2 = st.columns([2,8])
    auto_save = col1.checkbox("生成后自动保存任务", value=False)
    if col2.button("🚀 立即生成数据", type="primary", width='stretch'):
        with st.spinner("数据生成中..."):
            try:
                fun_params = []
                for _, row in edited_df.iterrows():
                    edited_df.at[_, "行号"] = _+1
                    field_name = row.get("字段名")
                    if not field_name or pd.isna(field_name): 
                        continue
                    
                    raw_miss_rate = row.get("缺失率(%)")
                    miss_rate = 0 if pd.isna(raw_miss_rate) else raw_miss_rate
                    
                    params = {
                        "col_name": field_name,
                        "miss_rate": miss_rate
                    }
                    
                    def get_safe_val(val, default, is_float=False):
                        if pd.isna(val) or str(val).strip() == "":
                            return default
                        try:
                            return float(val) if is_float else int(float(val))
                        except:
                            return default

                    t = row["数据类型"]

                    if t in ["seq_id", "boolean"]:
                        params["display_format"] = row.get("显示格式")
                    elif t in ["age", "number"]:
                        params["min"] = get_safe_val(row.get("最小值/起始时间"), 0)
                        params["max"] = get_safe_val(row.get("最大值/结束时间"), 100)
                    elif t == "float_number":
                        params["min"] = get_safe_val(row.get("最小值/起始时间"), 0.0, True)
                        params["max"] = get_safe_val(row.get("最大值/结束时间"), 100.0, True)
                        params["ndigits"] = 2
                    elif t == ["date_between", "datetime_between"]:
                        start = row.get("最小值/起始时间")
                        end = row.get("最大值/结束时间")
                        params["start_date"] = start if (not pd.isna(start) and str(start).strip()) else "-3y"
                        params["end_date"] = end if (not pd.isna(end) and str(end).strip()) else "today"
                    elif t == "udf_sequence":
                        ext = row.get("自定义值列表(英文逗号分隔)")
                        params["ext_words"] = ext if (not pd.isna(ext) and str(ext).strip()) else "A,B,C"

                    fun_params.append({"fun": t, "params": params})

                if not fun_params:
                    st.warning("请至少完整填写一行有效的字段配置！")
                else:
                    start_time = time.time()
                    df_res = generate_data(row_num, fun_params)
                    cost_time = round(time.time() - start_time, 2)
                    
                    st.success(f"生成成功！共 {row_num} 行数据，耗时 {cost_time} 秒。")
                    st.dataframe(df_res.head(10), hide_index=True, width='stretch')

                    if auto_save:
                        task_id = time.strftime("%Y%m%d_%H%M%S")
                        file_path = os.path.join(OUTPUT_DIR, f"task_{task_id}.csv")
                        df_res.to_csv(file_path, index=False, encoding="utf-8-sig")
                        
                        st.session_state.tasks.insert(0, {
                            "task_id": task_id,
                            "rows": row_num,
                            "time": time.strftime("%Y-%m-%d %H:%M:%S"),
                            "cost": cost_time,
                            "file_path": file_path,
                            "dataframe": df_res.head(50)
                        })
                        st.success(f"任务ID: **{task_id}** 已保存！请前往「任务管理」查看或下载。")
            except Exception as e:
                st.error(f"生成失败: {str(e)}")
    
    col1, col2 = st.columns([1,3])
    template_name = col1.text_input("模板名称", placeholder="如：电商用户表测试数据")
    template_desc = col2.text_input("模板介绍", placeholder="如：用户ID，订单号，订单金额等")
        
    if st.button("💾 保存为模板", type="secondary", width='stretch'):
        if template_name.strip() == "":
            st.warning("请填写模板名称！")
        else:
            config_list = edited_df.to_dict(orient="records")
            st.session_state.templates[template_name] = config_list
            save_templates()
            st.success(f"模板 '{template_name}' 保存成功！")

# ================= 页面2：模板管理 =================
elif page == "模板管理":
    st.subheader("📋 模板管理")
    st.markdown("管理已保存的字段配置模板。")

    if not st.session_state.templates:
        st.info("暂无保存的模板!")
    else:
        for name, config in list(st.session_state.templates.items()):
            with st.expander(f"📄 {name}"):

                st.dataframe(pd.DataFrame(config), width='stretch', hide_index=True)
                
                col1, col2 = st.columns(2)
                with col1:
                    # 💡 优化 3：点击载入后，利用独立状态锁记录，完美破除嵌套
                    if st.button("载入", key=f"load_{name}", width='stretch'):
                        st.session_state.current_config = pd.DataFrame(config)
                        st.session_state.active_template = name # 记录当前被激活的模板名
                        st.rerun()
                with col2:
                    if st.button("删除", key=f"del_{name}", width='stretch'):
                        if st.session_state.get("active_template") == name:
                            st.session_state.active_template = None
                        del st.session_state.templates[name]
                        save_templates()
                        st.rerun()
                
                # 💡 优化 4：跳出 columns 限制，由状态控制提示框和跳转按钮的渲染
                if st.session_state.get("active_template") == name:
                    st.success(f"已载入 '{name}'！配置已同步至后台。")
                    # if st.button("🚀 立即前往数据生成器", key=f"goto_gen_{name}", type="primary"):
                    #     st.session_state.page = "数据生成器" # 改变路由
                    #     st.session_state.active_template = None # 阅后即焚，清除提示状态
                    #     st.rerun()

# ================= 页面3：任务管理 =================
elif page == "任务管理":
    st.subheader("#️⃣ 任务管理")
    st.markdown("查看历史生成任务、预览数据并下载。")

    loggedin_user = st.session_state.get("user", None)

    if not loggedin_user:
        st.warning("Please login first!")
    else:
        if not st.session_state.tasks:
            st.info("暂无生成任务历史!")
        else:
            for task in st.session_state.tasks:
                st.write(f"任务ID: **{task['task_id']}**")
                cols = st.columns([1,2,1,1])
                cols[0].metric("生成行数", task['rows'])
                cols[1].metric("生成时间", task['time'])
                cols[2].metric("耗时(秒)", task['cost'])
                
                with cols[3]:
                    if os.path.exists(task['file_path']):
                        with open(task['file_path'], "rb") as f:
                            st.download_button(
                                label="⬇️ 下载完整数据（CSV文件）",
                                data=f,
                                file_name=f"{task['task_id']}.csv",
                                mime="text/csv",
                                key=f"dl_{task['task_id']}"
                            )
                    else:
                        st.warning("文件已清理")

                st.caption("数据预览 (Top 50 行)")
                st.dataframe(task['dataframe'], height=200, width='stretch', hide_index=True)
                st.divider()