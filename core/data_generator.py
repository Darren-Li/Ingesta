import time
import random
import math
import pandas as pd
from faker import Faker
from faker.providers import internet


class DataGenerator:
    def __init__(self, locale_args=['zh_CN'], row_num=100, miss_value=None):
        self.fake = Faker(locale_args)
        self.fake.add_provider(internet)
        self.row_num = row_num
        self.miss_value = miss_value

    def set_missing_values(self, v, miss_rate):
        if miss_rate <= 0: return v
        miss_rate = miss_rate / 100 if miss_rate > 1 else miss_rate
        miss_records = math.floor(self.row_num * miss_rate)
        
        indices = random.sample(range(self.row_num), miss_records)
        for idx in indices:
            v[idx] = self.miss_value
        return v

    def seq_id(self, col_name="ID", prefix="aha-", display_format="unique", miss_rate=0, 
               start_num=1000000, end_num=999999, **kwargs):
        if display_format == "unique":
            v = [prefix+str(start_num+i) for i in range(self.row_num)]
        else:
            if end_num < self.row_num:
                v = [prefix+str(start_num+random.randint(0, end_num-1)) for i in range(self.row_num)]
            else:
                v = [prefix+str(start_num+random.randint(0, self.row_num-1)) for i in range(self.row_num)]
        return {col_name: v}

    def person_name(self, col_name="姓名", miss_rate=0, **kwargs):
        v = [self.fake.name() for _ in range(self.row_num)]
        return {col_name: self.set_missing_values(v, miss_rate)}

    def user_name(self, col_name="用户名", miss_rate=0, **kwargs):
        v = [self.fake.user_name() for _ in range(self.row_num)]
        return {col_name: self.set_missing_values(v, miss_rate)}

    def age(self, col_name="年龄", min=18, max=65, miss_rate=0, **kwargs):
        v = [random.randint(int(min), int(max)) for _ in range(self.row_num)]
        return {col_name: self.set_missing_values(v, miss_rate)}

    def gender(self, col_name="性别", miss_rate=0, **kwargs):
        c = ["男", "女"]
        v = [random.choice(c) for _ in range(self.row_num)]
        return {col_name: self.set_missing_values(v, miss_rate)}

    def phone_number(self, col_name="手机号", miss_rate=0, **kwargs):
        v = [self.fake.phone_number() for _ in range(self.row_num)]
        return {col_name: self.set_missing_values(v, miss_rate)}

    def email(self, col_name="邮箱", miss_rate=0, **kwargs):
        v = [self.fake.email() for _ in range(self.row_num)]
        return {col_name: self.set_missing_values(v, miss_rate)}

    def number(self, col_name="整数", min=0, max=100, miss_rate=0, **kwargs):
        v = [random.randint(int(min), int(max)) for _ in range(self.row_num)]
        return {col_name: self.set_missing_values(v, miss_rate)}
        
    def float_number(self, col_name="浮点数", min=0.0, max=100.0, ndigits=2, miss_rate=0, **kwargs):
        v = [round(random.uniform(float(min), float(max)), int(ndigits)) for _ in range(self.row_num)]
        return {col_name: self.set_missing_values(v, miss_rate)}

    def boolean(self, col_name="布尔值", display_format=0, miss_rate=0):
        if display_format == 0:
            c = ["是", "否"]
        elif display_format == 1:
            c = ["False", "True"]
        elif display_format == 2:
            c = [1, 0]
        elif display_format == 3:
            c = ["Yes", "No"]
        else:
            c = ["Y", "N"]
        v = [random.choice(c) for _ in range(self.row_num)]
        return {col_name: self.set_missing_values(v, miss_rate)}

    def date_between(self, col_name="日期", start_date='-3y', end_date='today', miss_rate=0, **kwargs):
        v = [self.fake.date_between(start_date=start_date, end_date=end_date).strftime('%Y-%m-%d') for _ in range(self.row_num)]
        return {col_name: self.set_missing_values(v, miss_rate)}

    def datetime_between(self, col_name="时间", start_date='-3y', end_date='now',  miss_rate=0, **kwargs):
        v = [self.fake.date_time_between(start_date=start_date, end_date=end_date) for _ in range(self.row_num)]
        return {col_name: self.set_missing_values(v, miss_rate)}

    def address(self, col_name="详细地址", miss_rate=0, **kwargs):
        v = [self.fake.address() for _ in range(self.row_num)]
        return {col_name: self.set_missing_values(v, miss_rate)}
        
    def company(self, col_name="公司", miss_rate=0, **kwargs):
        v = [self.fake.company() for _ in range(self.row_num)]
        return {col_name: self.set_missing_values(v, miss_rate)}

    def udf_sequence(self, col_name="自定义值列表", ext_words="A,B,C", miss_rate=0, **kwargs):
        # 将前端传来的逗号分隔字符串转为列表
        choices = [w.strip() for w in str(ext_words).split(",")] if ext_words else ["N/A"]
        v = [random.choice(choices) for _ in range(self.row_num)]
        return {col_name: self.set_missing_values(v, miss_rate)}

def generate_data(row_num, fun_params):
    """
    使用 getattr 安全调用类方法，替代 exec
    fun_params 格式: [{"fun": "person_name", "params": {"col_name": "客户姓名", "miss_rate": 5}}, ...]
    """
    gen = DataGenerator(row_num=row_num)
    result_dict = {}
    
    for item in fun_params:
        func_name = item.get("fun")
        params = item.get("params", {})
        
        # 安全反射调用
        if hasattr(gen, func_name):
            func = getattr(gen, func_name)
            col_data = func(**params)
            result_dict.update(col_data)
        else:
            raise ValueError(f"不支持的生成函数: {func_name}")
            
    df = pd.DataFrame(result_dict)
    # df.insert(0, "序号", range(1, len(df) + 1))
    return df
    