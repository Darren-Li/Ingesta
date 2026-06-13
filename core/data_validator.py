import pandas as pd
from pandera.errors import SchemaError, SchemaErrors
from core.schema_builder import build_schema


def validate_excel(file, schema_json):
    df = pd.read_excel(file)

    # for col, rule in schema_json.items():
    #     if "start_date" in rule or "end_date" in rule:
    #         if col in df.columns:
    #             # errors='coerce' 会将无法解析的字符串安全地转为 NaT
    #             df[col] = pd.to_datetime(df[col], errors='coerce')
    #             # print(f"列 {col} 转换后的数据类型: {df[col].dtype}")

    schema = build_schema(schema_json)

    try:
        schema.validate(df, lazy=True)
        return True, []

    except (SchemaError, SchemaErrors) as e:
        errors = []
        failure_cases = e.failure_cases

        for item in failure_cases.to_dict(orient="records"):
            row_index = item.get("index")
            raw_value = item.get("failure_case")
            if pd.isna(raw_value):
                safe_value = None
            elif isinstance(raw_value, pd.Timestamp):
                safe_value = str(raw_value)  # 转成 '2026-01-04 00:00:00'
            else:
                safe_value = raw_value

            errors.append({
                "row": int(row_index)+1 if isinstance(row_index, (int, float)) else None,
                "column": item.get("column") or "DATAFRAME",
                "value": safe_value,  # 使用清洗后的安全值
                "rule": str(item.get("check")),
                "message": f"Value '{safe_value}' failed rule '{item.get('check')}'"
            })

        return False, errors
