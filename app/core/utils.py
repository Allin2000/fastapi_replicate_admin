# import datetime

# import time

# import orjson

import re
from app.core.ctx import CTX_USER_ID
from app.sqlmodel.admin import  Log
from app.sqlmodel.base import LogType, LogDetailType
from datetime import datetime
from uuid import UUID
from tortoise import models


def to_lower_camel_case(x):
    """
    转小驼峰法命名, 首单词首字母小写, 其他单词首字母大写, userLoginCount
    :param x:
    :return:
    """
    s = re.sub('_([a-zA-Z])', lambda m: (m.group(1).upper()), x)
    return s[0].lower() + s[1:]

async def model_to_dict(
    model_instance: models.Model,
    include_fields: list[str] | None = None,
    exclude_fields: list[str] | None = None,
    m2m: bool = False
) -> dict:
    """
    将模型实例转换为字典。

    :param model_instance: Tortoise ORM 模型实例
    :param include_fields: 要包含在字典中的字段名列表
    :param exclude_fields: 要从字典中排除的字段名列表
    :param m2m: 是否包含多对多关系字段
    :return: 包含模型字段和值的字典
    """
    include_fields = include_fields or []
    exclude_fields = exclude_fields or []

    d = {}
    for field in model_instance._meta.db_fields:
        if (not include_fields or field in include_fields) and (not exclude_fields or field not in exclude_fields):
            value = getattr(model_instance, field)
            if isinstance(value, datetime):
                value = value.strftime("%Y-%m-%d %H:%M:%S")  # 使用你的 DATETIME_FORMAT
            elif isinstance(value, UUID):
                value = str(value)
            d[to_lower_camel_case(field)] = value

    if m2m:
        for field in model_instance._meta.m2m_fields:
            if (not include_fields or field in include_fields) and (not exclude_fields or field not in exclude_fields):
                values = [value for value in await getattr(model_instance, field).all().values()]
                for value in values:
                    _value = value.copy()
                    for k, v in _value.items():
                        if isinstance(v, datetime):
                            v = v.strftime("%Y-%m-%d %H:%M:%S")  # 使用你的 DATETIME_FORMAT
                        elif isinstance(v, UUID):
                            v = str(v)
                        value.pop(k)
                        value[to_lower_camel_case(k)] = v
                d[to_lower_camel_case(field)] = values

    return d


async def insert_log(log_type: LogType, log_detail_type: LogDetailType, by_user_id: int | None = None):
    """
    插入日志
    :param log_type:
    :param log_detail_type:
    :param by_user_id: 0为从上下文获取当前用户id, 需要请求携带token
    :return:
    """
    if by_user_id == 0 and (by_user_id := CTX_USER_ID.get()) == 0:
        by_user_id = None

    await Log.create(log_type=log_type, log_detail_type=log_detail_type, by_user_id=by_user_id)




def check_url(url: str = "/api/v1/system-manage/roles/{role_id}/buttons", url2: str = "/api/v1/system-manage/roles/1/buttons") -> bool:
    pattern = re.sub(r'\{.*?}', '[^/]+', url)
    if re.match(pattern, url2):
        return True
    return False


# LAYOUT_PREFIX = 'layout.'
# VIEW_PREFIX = 'view.'
# FIRST_LEVEL_ROUTE_COMPONENT_SPLIT = '$'



# def get_layout_and_page(component=None):
#     layout = ''
#     page = ''

#     if component:
#         layout_or_page, page_item = component.split(FIRST_LEVEL_ROUTE_COMPONENT_SPLIT)
#         layout = get_layout(layout_or_page)
#         page = get_page(page_item or layout_or_page)

#     return layout, page


# def get_layout(layout):
#     return layout.replace(LAYOUT_PREFIX, '') if layout.startswith(LAYOUT_PREFIX) else ''


# def get_page(page):
#     return page.replace(VIEW_PREFIX, '') if page.startswith(VIEW_PREFIX) else ''


# def transform_layout_and_page_to_component(layout, page):
#     if layout and page:
#         return f"{LAYOUT_PREFIX}{layout}{FIRST_LEVEL_ROUTE_COMPONENT_SPLIT}{VIEW_PREFIX}{page}"
#     elif layout:
#         return f"{LAYOUT_PREFIX}{layout}"
#     elif page:
#         return f"{VIEW_PREFIX}{page}"
#     else:
#         return ''


# def get_route_path_by_route_name(route_name):
#     return f"/{route_name.replace('_', '/')}"


# def get_path_param_from_route_path(route_path):
#     path, param = route_path.split('/:')
#     return path, param


# def get_route_path_with_param(route_path, param):
#     if param.strip():
#         return f"{route_path}/:{param}"
#     else:
#         return route_path


# def camel_case_convert(data: dict):
#     """
#     转换字典key为小驼峰格式
#     :param data:
#     :return:
#     """
#     converted_data = {}
#     for key, value in data.items():
#         converted_key = ''.join(word.capitalize() if i else word for i, word in enumerate(key.split('_')))
#         converted_data[converted_key] = value
#         # converted_data[to_snake_case(key)] = value
#     return converted_data


# def snake_case_convert(data: dict):
#     """
#     转换字典key为下划线格式
#     :param data:
#     :return:
#     """
#     converted_data = {}
#     for key, value in data.items():
#         converted_data[to_snake_case(key)] = value
#     return converted_data


# def to_snake_case(x):
#     """
#     驼峰转下划线命名
#     :param x:
#     :return:
#     """
#     return re.sub(r'(?<=[a-z])[A-Z]|(?<!^)[A-Z](?=[a-z])', '_\\g<0>', x).lower()


# def to_camel_case(x):
#     """
#     转驼峰法命名, 首单词不变, 其他单词首字母大写, userLoginCount
#     :param x:
#     :return:
#     """
#     return re.sub('_([a-zA-Z])', lambda m: (m.group(1).upper()), x)


# def to_upper_camel_case(x):
#     """
#     转大驼峰法命名, 全部单词首字母大写, userLoginCount
#     :param x:
#     :return:
#     """
#     s = re.sub('_([a-zA-Z])', lambda m: (m.group(1).upper()), x)
#     return s[0].upper() + s[1:]



# # 这里可以处理一些原本处理不了的格式（ObjectId）或者自定义显示格式（datetime）
# def _default(obj):
#     if isinstance(obj, datetime.datetime):
#         if obj != obj:
#             return None
#         if obj.hour == 0 and obj.minute == 0:
#             return obj.strftime("%Y-%m-%d")
#         return obj.strftime("%Y-%m-%d %H:%M:%S")
#     elif isinstance(obj, datetime.date):
#         return obj.isoformat()
#     # elif isinstance(obj, ObjectId):
#     #     return obj.__str__()
#     elif hasattr(obj, "asdict"):
#         return obj.asdict()
#     elif hasattr(obj, "_asdict"):  # namedtuple
#         return obj._asdict()
#     elif hasattr(obj, '__dict__'):
#         return obj.__dict__
#     else:
#         raise TypeError(f"Unsupported json dump type: {type(obj)}")


# def orjson_dumps(data):
#     # 这里的样式通过 | 的方式叠加， 其实每个对应的是一个数字， 更多的样式可以见上面的 github 链接
#     option = orjson.OPT_PASSTHROUGH_DATETIME | orjson.OPT_SERIALIZE_NUMPY | orjson.OPT_INDENT_2
#     rv = orjson.dumps(data, default=_default, option=option)
#     # rv = orjson.dumps(data, default=_default)
#     return rv.decode(encoding='utf-8')


# def timestamp_to_time(timestamp):
#     time_struct = time.localtime(timestamp)
#     time_string = time.strftime("%Y-%m-%d %H:%M:%S", time_struct)
#     return time_string


# def time_to_timestamp(dt="2023-06-01 00:00:00"):
#     timeArray = time.strptime(dt, "%Y-%m-%d %H:%M:%S")
#     timestamp = time.mktime(timeArray)
#     return str(int(timestamp))
