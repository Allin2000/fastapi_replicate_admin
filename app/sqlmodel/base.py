from enum import Enum
from tortoise import models



class BaseModel(models.Model):
    class Meta:
        abstract = True



class LogType(str, Enum):
    ApiLog = "1"
    UserLog = "2"
    AdminLog = "3"
    SystemLog = "4"


class LogDetailType(str, Enum):
    """
    1000-1999 内置
    1100-1199 系统
    1200-1299 用户
    1400-1499 菜单
    1500-1599 角色
    1600-1699 用户
    """
    SystemStart = "1101"
    SystemStop = "1102"

    UserLoginSuccess = "1201"
    UserAuthRefreshTokenSuccess = "1202"
    UserLoginGetUserInfo = "1203"
    UserLoginUserNameVaild = "1211"
    UserLoginErrorPassword = "1212"
    UserLoginForbid = "1213"

    MenuGetList = "1401"
    MenuGetTree = "1402"
    MenuGetPages = "1403"
    MenuGetButtonsTree = "1404"

    MenuGetOne = "1411"
    MenuCreateOne = "1412"
    MenuUpdateOne = "1413"
    MenuDeleteOne = "1414"
    MenuBatchDeleteOne = "1415"

    RoleGetList = "1501"
    RoleGetMenus = "1502"
    RoleUpdateMenus = "1503"
    RoleGetButtons = "1504"
    RoleUpdateButtons = "1505"
    RoleGetApis = "1506"
    RoleUpdateApis = "1507"

    RoleGetOne = "1511"
    RoleCreateOne = "1512"
    RoleUpdateOne = "1513"
    RoleDeleteOne = "1514"
    RoleBatchDeleteOne = "1515"

    UserGetList = "1601"
    UserGetOne = "1611"
    UserCreateOne = "1612"
    UserUpdateOne = "1613"
    UserDeleteOne = "1614"
    UserBatchDeleteOne = "1615"


class StatusType(str, Enum):
    enable = "1"
    disable = "2"


class GenderType(str, Enum):
    male = "1"
    female = "2"
    unknow = "3"  # Soybean上没有


class MenuType(str, Enum):
    catalog = "1"  # 目录
    menu = "2"  # 菜单


class IconType(str, Enum):
    iconify = "1"
    local = "2"