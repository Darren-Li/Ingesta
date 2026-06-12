import pandas as pd
from pandera.errors import SchemaError, SchemaErrors
from core.schema_builder import build_schema


def validate_excel(file, schema_json):
    df = pd.read_excel(file)

    schema = build_schema(schema_json)

    try:
        schema.validate(df, lazy=True)
        return True, []

    except (SchemaError, SchemaErrors) as e:

        errors = []

        failure_cases = e.failure_cases

        for item in failure_cases.to_dict(orient="records"):
            # errors.append({
            #     "row": int(item.get("index")),
            #     "column": item.get("column"),
            #     "value": item.get("failure_case"),
            #     "rule": item.get("check"),
            #     "message": f"Value '{item.get('failure_case')}' not in allowed list"
            # })

            row_index = item.get("index")
            errors.append({
                "row": int(row_index) if isinstance(row_index, (int, float)) else None,
                "column": item.get("column") or "DATAFRAME",
                "value": item.get("failure_case"),
                "rule": item.get("check"),
                "message": f"Value '{item.get('failure_case')}' failed rule '{item.get('check')}'"
            })

        return False, errors
