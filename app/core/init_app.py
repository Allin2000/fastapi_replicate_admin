
from pathlib import Path

from fastapi import FastAPI
from aerich import Command
from tortoise.contrib.fastapi import register_tortoise
from loguru import logger
from fastapi.middleware import Middleware
from fastapi.middleware.cors import CORSMiddleware
from aerich.migrate import Migrate

from app.settings.config import APP_SETTINGS
from app.services.role import role_controller
from app.services.user import UserCreate, user_controller
from app.core.exceptions import (
    DoesNotExist,
    DoesNotExistHandle,
    HTTPException,
    HttpExcHandle,
    IntegrityError,
    IntegrityHandle,
    RequestValidationError,
    RequestValidationHandle,
    ResponseValidationError,
    ResponseValidationHandle,
)
from app.core.middlewares import BackGroundTaskMiddleware, APILoggerMiddleware, APILoggerAddResponseMiddleware
from app.sqlmodel.admin import Menu, Role, User, Button
from app.sqlmodel.base import StatusType, IconType, MenuType




def make_middlewares():
    middleware = [
        Middleware(
            CORSMiddleware,
            allow_origins=APP_SETTINGS.CORS_ORIGINS,
            allow_credentials=APP_SETTINGS.CORS_ALLOW_CREDENTIALS,
            allow_methods=APP_SETTINGS.CORS_ALLOW_METHODS,
            allow_headers=APP_SETTINGS.CORS_ALLOW_HEADERS,
        ),
        Middleware(BackGroundTaskMiddleware),
        Middleware(APILoggerMiddleware),
        Middleware(APILoggerAddResponseMiddleware),
    ]
    return middleware



def register_exceptions(app: FastAPI):
    app.add_exception_handler(DoesNotExist, DoesNotExistHandle)
    app.add_exception_handler(HTTPException, HttpExcHandle)  # type: ignore
    app.add_exception_handler(IntegrityError, IntegrityHandle)
    app.add_exception_handler(RequestValidationError, RequestValidationHandle)
    app.add_exception_handler(ResponseValidationError, ResponseValidationHandle)





def register_db(app: FastAPI):
    register_tortoise(
        app,
        config=APP_SETTINGS.TORTOISE_ORM,
        generate_schemas=True,
    )



async def modify_db():
    command = Command(tortoise_config=APP_SETTINGS.TORTOISE_ORM, app="app_system")


    # 第二步：检查是否已有迁移目录，没有才 init
    migrations_path = Path('migrations')  # 可能是 "migrations"
    if not migrations_path.exists():
        logger.info("Step 2: No migrations directory found. Initializing migrations...")
        await command.init_db(safe=True)
        await command.init()
        await command.migrate()
        await command.upgrade(run_in_transaction=True)
        
    else:
        logger.info("Migrations directory already exists.")
        Migrate.migrate_location = "migrations"

        # 生成迁移（如果模型变了才会生成）
        try:
            logger.info("Checking for model changes and generating migrations...")
            await command.migrate()
        except Exception as e:
            logger.warning(f"No migration generated or error occurred: {e}")

        # 应用迁移
        try:
            logger.info("Applying migration upgrades...")
            await command.upgrade()
            logger.info("Database upgrade complete.")
        except Exception as e:
            logger.error(f"Database upgrade failed: {e}")



async def init_menus():
    menus = await Menu.exists()
    if menus:
        return

    constant_menu = [
        Menu(
            status=StatusType.enable,
            parent_id=0,
            menu_type=MenuType.catalog,
            menu_name="login",
            route_name="login",
            route_path="/login",
            component="layout.blank$view.login",
            order=1,
            i18n_key="route.login",
            props=True,
            constant=True,
            hide_in_menu=True,
        ),
        Menu(
            status=StatusType.enable,
            parent_id=0,
            menu_type=MenuType.catalog,
            menu_name="403",
            route_name="403",
            route_path="/403",
            component="layout.blank$view.403",
            order=2,
            i18n_key="route.403",
            constant=True,
            hide_in_menu=True,
        ),
        Menu(
            status=StatusType.enable,
            parent_id=0,
            menu_type=MenuType.catalog,
            menu_name="404",
            route_name="404",
            route_path="/404",
            component="layout.blank$view.404",
            order=3,
            i18n_key="route.404",
            constant=True,
            hide_in_menu=True,
        ),
        Menu(
            status=StatusType.enable,
            parent_id=0,
            menu_type=MenuType.catalog,
            menu_name="500",
            route_name="500",
            route_path="/500",
            component="layout.blank$view.500",
            order=4,
            i18n_key="route.500",
            constant=True,
            hide_in_menu=True,
        ),
    ]
    await Menu.bulk_create(constant_menu)

    # 1
    await Menu.create(
        status=StatusType.enable,
        parent_id=0,
        menu_type=MenuType.menu,
        menu_name="首页",
        route_name="home",
        route_path="/home",
        component="layout.base$view.home",
        order=1,
        i18n_key="route.home",
        icon="mdi:monitor-dashboard",
        icon_type=IconType.iconify,
    )

    # 2
    root_menu = await Menu.create(
        status=StatusType.enable,
        parent_id=0,
        menu_type=MenuType.catalog,
        menu_name="功能",
        route_name="function",
        route_path="/function",
        component="layout.base",
        order=2,
        i18n_key="route.function",
        icon="icon-park-outline:all-application",
        icon_type=IconType.iconify,
    )

    parent_menu = await Menu.create(
        status=StatusType.enable,
        parent_id=root_menu.id,
        menu_type=MenuType.menu,
        menu_name="切换权限",
        route_name="function_toggle-auth",
        route_path="/function/toggle-auth",
        component="view.function_toggle-auth",
        order=4,
        i18n_key="route.function_toggle-auth",
        icon="ic:round-construction",
        icon_type=IconType.iconify,
    )

    button_code1 = await Button.create(button_code="B_CODE1", button_desc="超级管理员可见")
    await parent_menu.buttons.add(button_code1)
    button_code2 = await Button.create(button_code="B_CODE2", button_desc="管理员可见")
    await parent_menu.buttons.add(button_code2)
    button_code3 = await Button.create(button_code="B_CODE3", button_desc="管理员和用户可见")
    await parent_menu.buttons.add(button_code3)

    children_menu = [
        Menu(
            status=StatusType.enable,
            parent_id=root_menu.id,
            menu_type=MenuType.menu,
            menu_name="请求",
            route_name="function_request",
            route_path="/function/request",
            component="view.function_request",
            order=3,
            i18n_key="route.function_request",
            icon="carbon:network-overlay",
            icon_type=IconType.iconify,
        ),
        Menu(
            status=StatusType.enable,
            parent_id=root_menu.id,
            menu_type=MenuType.menu,
            menu_name="超级管理员可见",
            route_name="function_super-page",
            route_path="/function/super-page",
            component="view.function_super-page",
            order=5,
            i18n_key="route.function_super-page",
            icon="ic:round-supervisor-account",
            icon_type=IconType.iconify,
        ),
        Menu(
            status=StatusType.enable,
            parent_id=root_menu.id,
            menu_type=MenuType.menu,
            menu_name="多标签页",
            route_name="function_multi-tab",
            route_path="/function/multi-tab",
            component="view.function_multi-tab",
            order=1,
            i18n_key="route.function_multi-tab",
            icon="ic:round-tab",
            icon_type=IconType.iconify,
            multi_tab=True,
            hide_in_menu=True,
            active_menu="function_tab",
        ),
        Menu(
            status=StatusType.enable,
            parent_id=root_menu.id,
            menu_type=MenuType.menu,
            menu_name="标签页",
            route_name="function_tab",
            route_path="/function/tab",
            component="view.function_tab",
            order=2,
            i18n_key="route.function_tab",
            icon="ic:round-tab",
            icon_type=IconType.iconify,
        ),
    ]
    await Menu.bulk_create(children_menu)

    parent_menu = await Menu.create(
        status=StatusType.enable,
        parent_id=root_menu.id,
        menu_type=MenuType.catalog,
        menu_name="隐藏子菜单",
        route_name="function_hide-child",
        route_path="/function/hide-child",
        redirect="/function/hide-child/one",
        order=2,
        i18n_key="route.function_hide-child",
        icon="material-symbols:filter-list-off",
        icon_type=IconType.iconify,
    )

    children_menu = [
        Menu(
            status=StatusType.enable,
            parent_id=parent_menu.id,
            menu_type=MenuType.menu,
            menu_name="隐藏子菜单1",
            route_name="function_hide-child_one",
            route_path="/function/hide-child/one",
            component="view.function_hide-child_one",
            order=1,
            i18n_key="route.function_hide-child_one",
            icon="material-symbols:filter-list-off",
            icon_type=IconType.iconify,
            hide_in_menu=True,
            active_menu="function_hide-child",
        ),
        Menu(
            status=StatusType.enable,
            parent_id=parent_menu.id,
            menu_type=MenuType.menu,
            menu_name="隐藏子菜单2",
            route_name="function_hide-child_two",
            route_path="/function/hide-child/two",
            component="view.function_hide-child_two",
            order=2,
            i18n_key="route.function_hide-child_two",
            hide_in_menu=True,
            active_menu="function_hide-child",
        ),
        Menu(
            status=StatusType.enable,
            parent_id=parent_menu.id,
            menu_type=MenuType.menu,
            menu_name="隐藏子菜单3",
            route_name="function_hide-child_three",
            route_path="/function/hide-child/three",
            component="view.function_hide-child_three",
            order=3,
            i18n_key="route.function_hide-child_three",
            hide_in_menu=True,
            active_menu="function_hide-child",
        )
    ]
    await Menu.bulk_create(children_menu)

    # 5
    root_menu = await Menu.create(
        status=StatusType.enable,
        parent_id=0,
        menu_type=MenuType.catalog,
        menu_name="异常页",
        route_name="exception",
        route_path="/exception",
        component="layout.base",
        order=3,
        i18n_key="route.exception",
        icon="ant-design:exception-outlined",
        icon_type=IconType.iconify,
    )
    children_menu = [
        Menu(
            status=StatusType.enable,
            parent_id=root_menu.id,
            menu_type=MenuType.menu,
            menu_name="403",
            route_name="exception_403",
            route_path="/exception/403",
            component="view.403",
            order=1,
            i18n_key="route.exception_403",
            icon="ic:baseline-block",
            icon_type=IconType.iconify,
        ),
        Menu(
            status=StatusType.enable,
            parent_id=root_menu.id,
            menu_type=MenuType.menu,
            menu_name="404",
            route_name="exception_404",
            route_path="/exception/404",
            component="view.404",
            order=2,
            i18n_key="route.exception_404",
            icon="ic:baseline-web-asset-off",
            icon_type=IconType.iconify,
        ),
        Menu(
            status=StatusType.enable,
            parent_id=root_menu.id,
            menu_type=MenuType.menu,
            menu_name="500",
            route_name="exception_500",
            route_path="/exception/500",
            component="view.500",
            order=3,
            i18n_key="route.exception_500",
            icon="ic:baseline-wifi-off",
            icon_type=IconType.iconify,
        ),
    ]
    await Menu.bulk_create(children_menu)

    # 9
    root_menu = await Menu.create(
        status=StatusType.enable,
        parent_id=0,
        menu_type=MenuType.catalog,
        menu_name="多级菜单",
        route_name="multi-menu",
        route_path="/multi-menu",
        component="layout.base",
        order=4,
        i18n_key="route.multi-menu",
        icon="mdi:menu",
        icon_type=IconType.iconify,
    )
    parent_menu = await Menu.create(
        status=StatusType.enable,
        parent_id=root_menu.id,
        menu_type=MenuType.catalog,
        menu_name="一级子菜单1",
        route_name="multi-menu_first",
        route_path="/multi-menu/first",
        order=1,
        i18n_key="route.multi-menu_first",
        icon="mdi:menu",
        icon_type=IconType.iconify,
    )
    await Menu.create(
        status=StatusType.enable,
        parent_id=parent_menu.id,
        menu_type=MenuType.menu,
        menu_name="二级子菜单",
        route_name="multi-menu_first_child",
        route_path="/multi-menu/first/child",
        component="view.multi-menu_first_child",
        order=1,
        i18n_key="route.multi-menu_first_child",
        icon="mdi:menu",
        icon_type=IconType.iconify,
    )

    parent_menu = await Menu.create(
        status=StatusType.enable,
        parent_id=root_menu.id,
        menu_type=MenuType.catalog,
        menu_name="一级子菜单2",
        route_name="multi-menu_second",
        route_path="/multi-menu/second",
        order=13,
        i18n_key="route.multi-menu_second",
        icon="mdi:menu",
        icon_type=IconType.iconify,
    )

    parent_menu = await Menu.create(
        status=StatusType.enable,
        parent_id=parent_menu.id,
        menu_type=MenuType.catalog,
        menu_name="二级子菜单2",
        route_name="multi-menu_second_child",
        route_path="/multi-menu/second/child",
        order=1,
        i18n_key="route.multi-menu_second_child",
        icon="mdi:menu",
        icon_type=IconType.iconify,
    )

    await Menu.create(
        status=StatusType.enable,
        parent_id=parent_menu.id,
        menu_type=MenuType.menu,
        menu_name="三级菜单",
        route_name="multi-menu_second_child_home",
        route_path="/multi-menu/second/child/home",
        component="view.multi-menu_second_child_home",
        order=1,
        i18n_key="route.multi-menu_second_child_home",
        icon="mdi:menu",
        icon_type=IconType.iconify,
    )

    # 16
    root_menu = await Menu.create(
        status=StatusType.enable,
        parent_id=0,
        menu_type=MenuType.catalog,
        menu_name="系统管理",
        route_name="manage",
        route_path="/manage",
        component="layout.base",
        order=5,
        i18n_key="route.manage",
        icon="carbon:cloud-service-management",
        icon_type=IconType.iconify,
    )

    parent_menu = await Menu.create(
        status=StatusType.enable,
        parent_id=root_menu.id,
        menu_type=MenuType.menu,
        menu_name="日志管理",
        route_name="manage_log",
        route_path="/manage/log",
        component="view.manage_log",
        order=1,
        i18n_key="route.manage_log",
        icon="material-symbols:list-alt-outline",
        icon_type=IconType.iconify,
    )
    button_add_del_batch_del = await Button.create(
        button_code="B_Add_Del_Batch-del",
        button_desc="新增_删除_批量删除"
    )

    await parent_menu.buttons.add(button_add_del_batch_del)


    children_menu = [
        Menu(
            status=StatusType.enable,
            parent_id=root_menu.id,
            menu_type=MenuType.menu,
            menu_name="用户管理",
            route_name="manage_user",
            route_path="/manage/user",
            component="view.manage_user",
            order=3,
            i18n_key="route.manage_user",
            icon="ic:round-manage-accounts",
            icon_type=IconType.iconify,
        ),
        Menu(
            status=StatusType.enable,
            parent_id=root_menu.id,
            menu_type=MenuType.menu,
            menu_name="角色管理",
            route_name="manage_role",
            route_path="/manage/role",
            component="view.manage_role",
            order=4,
            i18n_key="route.manage_role",
            icon="carbon:user-role",
            icon_type=IconType.iconify,
        ),
        Menu(
            status=StatusType.enable,
            parent_id=root_menu.id,
            menu_type=MenuType.menu,
            menu_name="菜单管理",
            route_name="manage_menu",
            route_path="/manage/menu",
            component="view.manage_menu",
            order=5,
            i18n_key="route.manage_menu",
            icon="material-symbols:route",
            icon_type=IconType.iconify,
        ),
        Menu(
            status=StatusType.enable,
            parent_id=root_menu.id,
            menu_type=MenuType.menu,
            menu_name="用户详情",
            route_name="manage_user-detail",
            route_path="/manage/user-detail/:id",
            component="view.manage_user-detail",
            order=6,
            i18n_key="route.manage_user-detail",
            hide_in_menu=True,
        ),
    ]
    await Menu.bulk_create(children_menu)

    await Menu.create(
        status=StatusType.enable,
        parent_id=0,
        menu_type=MenuType.menu,
        menu_name="关于",
        route_name="about",
        route_path="/about",
        component="layout.base$view.about",
        order=6,
        i18n_key="route.about",
        icon="fluent:book-information-24-regular",
        icon_type=IconType.iconify,
    )


async def init_users():
    role_exist = await role_controller.model.exists()
    if not role_exist:
        # 超级管理员拥有所有菜单
        role_super = await Role.create(role_name="超级管理员", role_code="R_SUPER", role_desc="超级管理员")
        await Role.get(role_code="R_SUPER")

        role_super_menu_objs = await Menu.filter(constant=False)  # 过滤常量路由(公共路由)
        for menu_obj in role_super_menu_objs:
            await role_super.menus.add(menu_obj)

        button_code1 = await Button.get(button_code="B_CODE1")
        await role_super.buttons.add(button_code1)

        # 管理员拥有 首页 关于 系统管理-API管理 系统管理-用户管理
        role_admin = await Role.create(role_name="管理员", role_code="R_ADMIN", role_desc="管理员")
        await Role.get(role_code="R_ADMIN")


        role_admin_menus = ["home", "about", "function_toggle-auth", "manage_log", "manage_user"]
        for route_name in role_admin_menus:
            menu_obj: Menu = await Menu.get(route_name=route_name)
            await role_admin.menus.add(menu_obj)

        button_code2 = await Button.get(button_code="B_CODE2")
        await role_admin.buttons.add(button_code2)
        await role_super.buttons.add(button_code2)


        role_user = await Role.create(role_name="普通用户", role_code="R_USER", role_desc="普通用户")
        await Role.get(role_code="R_USER")  # 确保已创建
        
        role_user_menus = ["home", "about", "function_toggle-auth", "manage_log",]
        for route_name in role_user_menus:
            menu_obj: Menu = await Menu.get(route_name=route_name)
            await role_user.menus.add(menu_obj)

        button_code3 = await Button.get(button_code="B_CODE3")
        await role_user.buttons.add(button_code3)
        await role_admin.buttons.add(button_code3)
        await role_super.buttons.add(button_code3)

    user = await user_controller.model.exists()
    if not user:
        role_super: Role | None = await role_controller.get_by_code("R_SUPER")

        user_super: User = await user_controller.create(
            UserCreate(
                userName="Soybean",
                userEmail="admin@admin.com",
                password="123456",
            )
        )
        await user_super.roles.add(role_super)

        user_super: User = await user_controller.create(
            UserCreate(
                userName="Super",
                userEmail="admin1@admin.com",
                password="123456",
            )
        )
        await user_super.roles.add(role_super)

        role_admin: Role | None = await role_controller.get_by_code("R_ADMIN")
        if not role_admin:
            raise ValueError("角色 R_ADMIN 不存在，请确认角色初始化成功")

        user_admin = await user_controller.create(
            UserCreate(
                userName="Admin",
                userEmail="admin2@admin.com",
                password="123456",
            )
        )
        await user_admin.roles.add(role_admin)

        role_user: Role | None = await role_controller.get_by_code("R_USER")
        if not role_user:
            raise ValueError("角色 R_USER 不存在，请确认角色初始化成功")

        user_user = await user_controller.create(
            UserCreate(
                userName="User",
                userEmail="user@user.com",
                password="123456",
            )
        )
        await user_user.roles.add(role_user)



