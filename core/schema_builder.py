import pandera as pa
import re
import pandas as pd


# 预编译正则提升性能
EMAIL_REGEX = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")
PERSON_REGEX = re.compile(r"^[A-Za-z\s\u4e00-\u9fa5]+$")

def _safe_str(value):
    """安全提取字符串，NaN/None 返回 None"""
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return None
    s = str(value).strip()
    return s if s else None

def is_email(x):
    val = _safe_str(x)
    if val is None: 
        return True  # 空值交由 nullable 参数控制
    return bool(EMAIL_REGEX.match(val))

def is_company(x):
    val = _safe_str(x)
    if val is None: 
        return True
    return len(val) >= 2

def is_person(x):
    val = _safe_str(x)
    if val is None: 
        return True
    return bool(PERSON_REGEX.match(val))

def is_location(x):
    val = _safe_str(x)
    if val is None: 
        return True
    return len(val) > 2

def is_address(x):
    val = _safe_str(x)
    if val is None: 
        return True
    return len(val) > 5

# -----------------------------
# Build Pandera Schema
# -----------------------------
def build_schema(schema_json):
    columns = {}

    for col, rule in schema_json.items():
        col_type = rule.get("type", "string")
        checks = []

        # EMAIL
        if rule.get("format") == "email":
            checks.append(pa.Check(is_email, element_wise=True))

        # ENUM
        if "enum" in rule:
            checks.append(pa.Check.isin(rule["enum"]))

        if col_type == "string":
            # STRING LENGTH
            if "min_length" in rule:
                checks.append(
                    pa.Check.str_length(
                        min_value=rule["min"]
                    )
                )
            if "max_length" in rule:
                checks.append(
                    pa.Check.str_length(
                        max_value=rule["max"]
                    )
                )
        else: 
            # RANGE
            if "min" in rule:
                checks.append(pa.Check.ge(rule["min"]))
            if "max" in rule:
                checks.append(pa.Check.le(rule["max"]))

        # DATE RANGE
        if "start_date" in rule:
            checks.append(
                pa.Check.ge(pd.Timestamp(rule["start_date"]))
            )
        if "end_date" in rule:
            checks.append(
                pa.Check.le(pd.Timestamp(rule["end_date"]))
            )

        # REGX
        if "pattern" in rule:
            regex = re.compile(rule["pattern"])

            checks.append(
                pa.Check(
                    lambda x: (
                        pd.isna(x)
                        or bool(regex.match(str(x)))
                    ),
                    element_wise=True
                )
            )

        # SEMANTIC
        semantic_map = {
            "company": is_company,
            "person": is_person,
            "location": is_location,
            "address": is_address
        }
        
        semantic_func = semantic_map.get(rule.get("semantic"))

        if semantic_func:
            checks.append(pa.Check(semantic_func, element_wise=True))

        dtype_map = {
            "string": pa.String,
            "int": pa.Int64,
            "float": pa.Float,
            "date": pa.DateTime
        }

        # is_date_col = (col_type == "datetime")

        columns[col] = pa.Column(
            dtype_map.get(col_type, pa.String),
            checks=checks,
            nullable=rule.get("nullable", False),
            unique=rule.get("unique", False),
            # coerce=is_date_col
        )

    return pa.DataFrameSchema(columns,strict=False,coerce=True)