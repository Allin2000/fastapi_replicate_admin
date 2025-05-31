from tortoise import BaseDBAsyncClient


async def upgrade(db: BaseDBAsyncClient) -> str:
    return """
        CREATE TABLE IF NOT EXISTS "api_logs" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "ip_address" VARCHAR(60) NOT NULL,
    "user_agent" VARCHAR(800) NOT NULL,
    "request_url" VARCHAR(255) NOT NULL,
    "request_params" JSONB,
    "request_data" JSONB,
    "response_data" JSONB,
    "response_code" VARCHAR(6),
    "create_time" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "process_time" DOUBLE PRECISION
);
COMMENT ON COLUMN "api_logs"."id" IS 'API日志ID';
COMMENT ON COLUMN "api_logs"."ip_address" IS 'IP地址';
COMMENT ON COLUMN "api_logs"."user_agent" IS 'User-Agent';
COMMENT ON COLUMN "api_logs"."request_url" IS '请求URL';
COMMENT ON COLUMN "api_logs"."request_params" IS '请求参数';
COMMENT ON COLUMN "api_logs"."request_data" IS '请求数据';
COMMENT ON COLUMN "api_logs"."response_data" IS '响应数据';
COMMENT ON COLUMN "api_logs"."response_code" IS '响应业务码';
COMMENT ON COLUMN "api_logs"."create_time" IS '创建时间';
COMMENT ON COLUMN "api_logs"."process_time" IS '请求处理时间';
CREATE TABLE IF NOT EXISTS "buttons" (
    "create_time" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "update_time" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "id" SERIAL NOT NULL PRIMARY KEY,
    "button_code" VARCHAR(200) NOT NULL,
    "button_desc" VARCHAR(200) NOT NULL,
    "status" VARCHAR(1) NOT NULL DEFAULT '1'
);
COMMENT ON COLUMN "buttons"."id" IS '菜单ID';
COMMENT ON COLUMN "buttons"."button_code" IS '按钮编码';
COMMENT ON COLUMN "buttons"."button_desc" IS '按钮描述';
COMMENT ON COLUMN "buttons"."status" IS '状态';
CREATE TABLE IF NOT EXISTS "menus" (
    "create_time" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "update_time" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "id" SERIAL NOT NULL PRIMARY KEY,
    "menu_name" VARCHAR(100) NOT NULL,
    "menu_type" VARCHAR(1) NOT NULL,
    "route_name" VARCHAR(100) NOT NULL,
    "route_path" VARCHAR(200) NOT NULL,
    "path_param" VARCHAR(200),
    "route_param" JSONB,
    "order" INT NOT NULL DEFAULT 0,
    "component" VARCHAR(100),
    "parent_id" INT NOT NULL DEFAULT 0,
    "i18n_key" VARCHAR(100) NOT NULL,
    "icon" VARCHAR(100),
    "icon_type" VARCHAR(1),
    "href" VARCHAR(200),
    "multi_tab" BOOL NOT NULL DEFAULT False,
    "keep_alive" BOOL NOT NULL DEFAULT False,
    "hide_in_menu" BOOL NOT NULL DEFAULT False,
    "active_menu" VARCHAR(100),
    "fixed_index_in_tab" INT,
    "status" VARCHAR(1) NOT NULL DEFAULT '1',
    "redirect" VARCHAR(200),
    "props" BOOL NOT NULL DEFAULT False,
    "constant" BOOL NOT NULL DEFAULT False
);
COMMENT ON COLUMN "menus"."id" IS '菜单ID';
COMMENT ON COLUMN "menus"."menu_name" IS '菜单名称';
COMMENT ON COLUMN "menus"."menu_type" IS '菜单类型';
COMMENT ON COLUMN "menus"."route_name" IS '路由名称';
COMMENT ON COLUMN "menus"."route_path" IS '路由路径';
COMMENT ON COLUMN "menus"."path_param" IS '路径参数';
COMMENT ON COLUMN "menus"."route_param" IS '路由参数, List[dict]';
COMMENT ON COLUMN "menus"."order" IS '菜单顺序';
COMMENT ON COLUMN "menus"."component" IS '路由组件';
COMMENT ON COLUMN "menus"."parent_id" IS '父菜单ID';
COMMENT ON COLUMN "menus"."i18n_key" IS '用于国际化的展示文本，优先级高于title';
COMMENT ON COLUMN "menus"."icon" IS '图标名称';
COMMENT ON COLUMN "menus"."icon_type" IS '图标类型';
COMMENT ON COLUMN "menus"."href" IS '外链';
COMMENT ON COLUMN "menus"."multi_tab" IS '是否支持多页签';
COMMENT ON COLUMN "menus"."keep_alive" IS '是否缓存';
COMMENT ON COLUMN "menus"."hide_in_menu" IS '是否在菜单隐藏';
COMMENT ON COLUMN "menus"."active_menu" IS '隐藏的路由需要激活的菜单';
COMMENT ON COLUMN "menus"."fixed_index_in_tab" IS '固定在页签的序号';
COMMENT ON COLUMN "menus"."status" IS '状态';
COMMENT ON COLUMN "menus"."redirect" IS '重定向路径';
COMMENT ON COLUMN "menus"."props" IS '是否为首路由';
COMMENT ON COLUMN "menus"."constant" IS '是否为公共路由';
CREATE TABLE IF NOT EXISTS "roles" (
    "create_time" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "update_time" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "id" SERIAL NOT NULL PRIMARY KEY,
    "role_name" VARCHAR(20) NOT NULL UNIQUE,
    "role_code" VARCHAR(20) NOT NULL UNIQUE,
    "role_desc" VARCHAR(500),
    "role_home" VARCHAR(100) NOT NULL DEFAULT 'home',
    "status" VARCHAR(1) NOT NULL DEFAULT '1'
);
COMMENT ON COLUMN "roles"."id" IS '角色ID';
COMMENT ON COLUMN "roles"."role_name" IS '角色名称';
COMMENT ON COLUMN "roles"."role_code" IS '角色编码';
COMMENT ON COLUMN "roles"."role_desc" IS '角色描述';
COMMENT ON COLUMN "roles"."role_home" IS '角色首页';
COMMENT ON COLUMN "roles"."status" IS '状态';
CREATE TABLE IF NOT EXISTS "users" (
    "create_time" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "update_time" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "id" SERIAL NOT NULL PRIMARY KEY,
    "user_name" VARCHAR(20) NOT NULL UNIQUE,
    "password" VARCHAR(128) NOT NULL,
    "nick_name" VARCHAR(30),
    "user_gender" VARCHAR(1) NOT NULL DEFAULT '3',
    "user_email" VARCHAR(255) NOT NULL UNIQUE,
    "user_phone" VARCHAR(20),
    "last_login" TIMESTAMPTZ,
    "status" VARCHAR(1) NOT NULL DEFAULT '1'
);
COMMENT ON COLUMN "users"."id" IS '用户ID';
COMMENT ON COLUMN "users"."user_name" IS '用户名称';
COMMENT ON COLUMN "users"."password" IS '密码';
COMMENT ON COLUMN "users"."nick_name" IS '昵称';
COMMENT ON COLUMN "users"."user_gender" IS '性别';
COMMENT ON COLUMN "users"."user_email" IS '邮箱';
COMMENT ON COLUMN "users"."user_phone" IS '电话';
COMMENT ON COLUMN "users"."last_login" IS '最后登录时间';
COMMENT ON COLUMN "users"."status" IS '状态';
CREATE TABLE IF NOT EXISTS "logs" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "log_type" VARCHAR(1) NOT NULL,
    "log_detail_type" VARCHAR(4),
    "create_time" TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
    "by_user_id" INT REFERENCES "users" ("id") ON DELETE NO ACTION
);
COMMENT ON COLUMN "logs"."id" IS '日志ID';
COMMENT ON COLUMN "logs"."log_type" IS '日志类型';
COMMENT ON COLUMN "logs"."log_detail_type" IS '日志详情类型';
COMMENT ON COLUMN "logs"."create_time" IS '创建时间';
COMMENT ON COLUMN "logs"."by_user_id" IS '操作人';
CREATE TABLE IF NOT EXISTS "aerich" (
    "id" SERIAL NOT NULL PRIMARY KEY,
    "version" VARCHAR(255) NOT NULL,
    "app" VARCHAR(100) NOT NULL,
    "content" JSONB NOT NULL
);
CREATE TABLE IF NOT EXISTS "menus_buttons" (
    "menus_id" INT NOT NULL REFERENCES "menus" ("id") ON DELETE CASCADE,
    "button_id" INT NOT NULL REFERENCES "buttons" ("id") ON DELETE CASCADE
);
CREATE UNIQUE INDEX IF NOT EXISTS "uidx_menus_butto_menus_i_a9336b" ON "menus_buttons" ("menus_id", "button_id");
CREATE TABLE IF NOT EXISTS "roles_menus" (
    "roles_id" INT NOT NULL REFERENCES "roles" ("id") ON DELETE CASCADE,
    "menu_id" INT NOT NULL REFERENCES "menus" ("id") ON DELETE CASCADE
);
CREATE UNIQUE INDEX IF NOT EXISTS "uidx_roles_menus_roles_i_3d4119" ON "roles_menus" ("roles_id", "menu_id");
CREATE TABLE IF NOT EXISTS "roles_buttons" (
    "roles_id" INT NOT NULL REFERENCES "roles" ("id") ON DELETE CASCADE,
    "button_id" INT NOT NULL REFERENCES "buttons" ("id") ON DELETE CASCADE
);
CREATE UNIQUE INDEX IF NOT EXISTS "uidx_roles_butto_roles_i_f9441d" ON "roles_buttons" ("roles_id", "button_id");
CREATE TABLE IF NOT EXISTS "users_roles" (
    "users_id" INT NOT NULL REFERENCES "users" ("id") ON DELETE CASCADE,
    "role_id" INT NOT NULL REFERENCES "roles" ("id") ON DELETE CASCADE
);
CREATE UNIQUE INDEX IF NOT EXISTS "uidx_users_roles_users_i_baf5e4" ON "users_roles" ("users_id", "role_id");"""


async def downgrade(db: BaseDBAsyncClient) -> str:
    return """
        """
