import time
from contextlib import asynccontextmanager

from loguru import logger
from fastapi import FastAPI,APIRouter

from app.api.v1 import health_check,route,article,auth
from app.api.v1.system_manage import logs,menus,roles,users
from app.settings.config import APP_SETTINGS

from app.core.init_app import (
    init_menus,
    init_users,
    make_middlewares,
    modify_db,
    register_db,
    register_exceptions,
)

from app.sqlmodel.admin import Log
from app.sqlmodel.base import LogType, LogDetailType
# from app.core.dependency import DependPermission
from app.core.dependency import DependAuth

router = APIRouter()

router.include_router(router=health_check.router, tags=["Healthy Check"], prefix="/health-check")
router.include_router(router=route.router, tags=["route"], prefix="/route")
router.include_router(router=auth.router, tags=["auth"], prefix="/auth")
router.include_router(router=logs.router, tags=["日志管理"], prefix="/system-manage", dependencies=[DependAuth])
router.include_router(router=users.router, tags=["用户管理"], prefix="/system-manage", dependencies=[DependAuth])
router.include_router(router=menus.router, tags=["菜单管理"], prefix="/system-manage", dependencies=[DependAuth])
router.include_router(router=roles.router, tags=["角色管理"], prefix="/system-manage", dependencies=[DependAuth])
router.include_router(router=article.router, tags=["文章管理"], dependencies=[DependAuth])


def create_app() -> FastAPI:
    application = FastAPI(
        title=APP_SETTINGS.APP_TITLE,
        description=APP_SETTINGS.APP_DESCRIPTION,
        version=APP_SETTINGS.VERSION,
        openapi_url="/openapi.json",
        middleware=make_middlewares(),
        lifespan=lifespan
    )
    register_db(application)
    register_exceptions(application)
    application.include_router(router, prefix="/api/v1")

    return application


@asynccontextmanager
async def lifespan(
application: FastAPI):
    start_time = time.time()
    try:
        await modify_db()
        await init_menus()
        await init_users()
        await Log.create(log_type=LogType.SystemLog, log_detail_type=LogDetailType.SystemStart)

        yield
    finally:
        end_time = time.time()
        runtime = end_time - start_time
        logger.info(f"App {application.title} runtime: {runtime} seconds")  # noqa
        await Log.create(log_type=LogType.SystemLog, log_detail_type=LogDetailType.SystemStop)


app = create_app()



if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=9999, reload=False)
