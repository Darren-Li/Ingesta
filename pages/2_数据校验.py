import streamlit as st
import json
import ast
from datetime import datetime
from core.db import get_conn, delete_task, delete_template
from core.data_validator import validate_excel


st.set_page_config(page_title="Ingesta", layout="wide", initial_sidebar_state="expanded")
st.header("Data Validation Tool")

if "page" not in st.session_state:
    st.session_state.page = "Validator"

page = st.sidebar.radio("导航", ["Validator", "Tasks", "Templates"], 
    key="dv_page")

# -----------------------------
# Validator
# -----------------------------
if page == "Validator":

    st.subheader("🚧 Data Verification")

    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT id,name,schema_json FROM dv_templates")
    templates = c.fetchall()
    conn.close()

    if st.session_state.page == "Validator" and len(templates) == 0:
        st.warning("⚠ No templates found. Please create a template first.")
        st.stop()

    template_map = {f"{t[1]} (id:{t[0]})": t for t in templates}
    selected = st.selectbox("Select Template", list(template_map.keys()))
    template = template_map[selected]

    with st.expander(f"📄 Data Validation Template"):
        schema_json = json.loads(template[2])
        st.json(schema_json, expanded=True)

    file = st.file_uploader("Upload Excel", type=["xlsx"])

    if file:

        success, errors = validate_excel(file, schema_json)

        if success:
            st.success("Validation Passed")
        else:
            st.error("Validation Failed")
            st.warning("Please check the data validation result in the module 「Tasks」 ")
            # 登录才能查看结果哈:)
            # for num, e in enumerate(errors):
            #     st.error(f"🚨ERROR: {num} \n\nRow: {e['row']} | Col: '{e['column']}' | Error: {e['message']} | Error value: {e['value']} | Check rule: {e['rule']}")

        conn = get_conn()
        c = conn.cursor()

        c.execute("""
            INSERT INTO dv_tasks(user_id,template_id,status,error,file_name,created_at)
            VALUES (?,?,?,?,?,?)
        """,(
            st.session_state.user[0],
            template[0],
            "SUCCESS" if success else "FAILED",
            str(errors),
            file.name,
            datetime.now().isoformat()
        ))

        conn.commit()
        conn.close()

# -----------------------------
# TASKS
# -----------------------------
if page == "Tasks":
    
    st.subheader("📋 Task List")

    loggedin_user = st.session_state.get("user", None)

    if not loggedin_user:
        st.warning("Please login first!")
    else:
        conn = get_conn()
        c = conn.cursor()

        c.execute("SELECT * FROM dv_tasks WHERE user_id=? ORDER BY created_at DESC", (st.session_state.user[0],))
        rows = c.fetchall()
        conn.close()

        headers = ["ID", "File", "Status", "Created At", "Action"]
        col_widths = [1/4, 1, 1, 1, 1/2]
        cols = st.columns(col_widths)

        for col, h in zip(cols, headers):
            col.markdown(f"**{h}**")

        st.markdown('<hr style="margin:1px 0">', unsafe_allow_html=True)  # 表头分隔线

        # =========================
        # 数据行
        # =========================
        for r in rows:

            cols = st.columns(col_widths)

            # 状态颜色
            status_icon = "🟢" if r[3] == "SUCCESS" else "🔴"

            cols[0].write(r[0])
            cols[1].write(r[5])
            cols[2].write(f"{status_icon} {r[3]}")
            cols[3].write(datetime.fromisoformat(r[6]).strftime("%Y-%m-%d %H:%M:%S"))

            # 详情按钮 + 展开
            if r[4] and r[3] == "FAILED":
                with st.expander("Details:"):
                    errors = ast.literal_eval(r[4])
                    for num, e in enumerate(errors):
                        st.error(f"🚨ERROR: {num} \n\nRow: **{e['row']}** | Col: **{e['column']}** | Error: **{e['message']}** | Error value: **{e['value']}** | Check rule: **{e['rule']}**")
            else:
                st.write(None)

            with cols[4]:
                if st.button("🗑️", key=f"delete_{r[0]}"):
                    delete_task("dv_tasks",r[0])

                    st.success(f"Task {r[0]} deleted")
                    st.rerun()

            st.markdown('<hr style="margin:1px 0">', unsafe_allow_html=True)  # 行分隔线

# -----------------------------
# TEMPLATE BUILDER
# -----------------------------
if page == "Templates":

    st.subheader("📃 Template Builder")

    tab1, tab2 = st.tabs(["📃 Coding Model", "🧩 UI Model"])

    with tab1:
        name = st.text_input("Template Name", key="Coding1")

        schema_input = st.text_area(
            "Schema JSON",
            value="""{"email":{"type":"string","format":"email"},"status":{"type":"string","enum":["A","B"]}}""",
            key="Coding2"
        )

        if st.button("💾 Save Template", key="Coding3"):
            conn = get_conn()
            c = conn.cursor()
            c.execute(
                "INSERT INTO dv_templates(name,schema_json,created_at) VALUES (?,?,?)",
                (name, schema_input, datetime.now().isoformat())
            )
            conn.commit()
            conn.close()
            st.success("Template saved")

    with tab2:
        name = st.text_input("Template Name", key="UI1")

        # =========================
        # 初始化字段列表
        # =========================
        if "fields" not in st.session_state:
            st.session_state.fields = []

        # =========================
        # 添加字段按钮
        # =========================
        if st.button("➕ Add Field", key="UI2"):
            st.session_state.fields.append({})

        # =========================
        # 字段配置 UI
        # =========================
        schema = {}

        for i, field in enumerate(st.session_state.fields):

            st.markdown(f"### Field {i+1}")

            col1, col2, col3, col4, col5, col6, col7 = st.columns(7)

            # 字段名
            field_name = col1.text_input("Field Name", key=f"name_{i}")

            # 字段类型
            field_type = col2.selectbox(
                "Type",
                ["string", "int", "float"],
                key=f"type_{i}"
            )

            # 语义类型
            semantic = col3.selectbox(
                "Semantic",
                ["none", "email", "person", "company", "address", "phone", "location"],
                key=f"semantic_{i}"
            )

            # 是否必填
            required = col4.checkbox("Required", key=f"req_{i}")

            # 最小值
            min_val = col5.text_input("Min", key=f"min_{i}")

            # 最大值
            max_val = col6.text_input("Max", key=f"max_{i}")

            # 枚举值
            with col7:
                enum_input = st.text_input("Enum (comma separated)", key=f"enum_{i}")

            # =========================
            # 组装 schema
            # =========================
            if field_name:

                schema[field_name] = {
                    "type": field_type,
                    "nullable": not required
                }

                if semantic != "none":
                    schema[field_name]["semantic"] = semantic

                if min_val:
                    schema[field_name]["min"] = float(min_val)

                if max_val:
                    schema[field_name]["max"] = float(max_val)

                if enum_input:
                    schema[field_name]["enum"] = [
                        x.strip() for x in enum_input.split(",")
                    ]

        # =========================
        # JSON 预览（非常关键）
        # =========================
        st.subheader("📄 Generated Schema")
        st.json(schema)

        # =========================
        # 保存
        # =========================
        if st.button("💾 Save Template", key="UI3"):

            conn = get_conn()
            c = conn.cursor()

            c.execute(
                "INSERT INTO dv_templates(name,schema_json,created_at) VALUES (?,?,?)",
                (name, json.dumps(schema), datetime.now().isoformat())
            )

            conn.commit()
            conn.close()

            st.success("Template saved")
