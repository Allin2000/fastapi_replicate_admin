from datetime import datetime, timedelta, timezone

from fastapi import APIRouter
from fastapi import Form,HTTPException
from fastapi.responses import JSONResponse

from app.core.utils import insert_log
from app.services.user import user_controller
from app.core.ctx import CTX_USER_ID
from app.core.dependency import DependAuth, check_token
from app.sqlmodel.admin import User, Role, Button, StatusType
from app.sqlmodel.base import LogDetailType, LogType
from app.schemas.base import Fail, Success
from app.schemas.login import CredentialsSchema, JWTOut, JWTPayload
from app.settings.config import APP_SETTINGS
from app.core.security import create_access_token
from app.core.utils import model_to_dict

router = APIRouter()


@router.post("/login", summary="登录")
async def login(credentials: CredentialsSchema):
    user_obj: User | None = await user_controller.authenticate(credentials)  # 账号验证, 失败则触发异常返回请求错误
    if user_obj is None:
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    await user_controller.update_last_login(user_obj.id)
    payload = JWTPayload(
        data={"userId": user_obj.id, "userName": user_obj.user_name, "tokenType": "accessToken"},
        iat=datetime.now(timezone.utc),
        exp=datetime.now(timezone.utc)
    )
    access_token_payload = payload.model_copy(deep=True)
    access_token_payload.exp += timedelta(minutes=APP_SETTINGS.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_token_payload = payload.model_copy(deep=True)
    refresh_token_payload.data["tokenType"] = "refreshToken"
    refresh_token_payload.exp += timedelta(minutes=APP_SETTINGS.JWT_REFRESH_TOKEN_EXPIRE_MINUTES)
    data = JWTOut(
        access_token=create_access_token(data=access_token_payload),
        refresh_token=create_access_token(data=refresh_token_payload),
    )
    await insert_log(log_type=LogType.UserLog, log_detail_type=LogDetailType.UserLoginSuccess, by_user_id=user_obj.id)
    return Success(data=data.model_dump(by_alias=True))



@router.post("/token", summary="OAuth2 登录（Swagger UI 专用）")
async def auth_token(username: str = Form(...), password: str = Form(...)):
    try:
        credentials = CredentialsSchema(userName=username, password=password)
        user_obj: User | None = await user_controller.authenticate(credentials)

        if user_obj is None:
            raise HTTPException(status_code=401, detail="用户名或密码错误")

        await user_controller.update_last_login(user_obj.id)

        payload = JWTPayload(
            data={
                "userId": user_obj.id,
                "userName": user_obj.user_name,
                "tokenType": "accessToken"
            },
            iat=datetime.now(timezone.utc),
            exp=datetime.now(timezone.utc)
        )

        access_token_payload = payload.model_copy(deep=True)
        access_token_payload.exp += timedelta(
            minutes=APP_SETTINGS.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
        )


        
        # refresh_token_payload = payload.model_copy(deep=True)
        # refresh_token_payload.data["tokenType"] = "refreshToken"
        # refresh_token_payload.exp += timedelta(
        #     minutes=APP_SETTINGS.JWT_REFRESH_TOKEN_EXPIRE_MINUTES
        # )

        # jwt_out = JWTOut(
        #     access_token=create_access_token(data=access_token_payload),
        #     refresh_token=create_access_token(data=refresh_token_payload),
        # )

       # 注意：Swagger UI 只需要 access_token
        access_token = create_access_token(data=access_token_payload)

        await insert_log(
            log_type=LogType.UserLog,
            log_detail_type=LogDetailType.UserLoginSuccess,
            by_user_id=user_obj.id,
        )

        return  JSONResponse(
        content={
            "access_token": access_token,
            "token_type": "bearer"
        }
    )
    except Exception as e:
        # 打印日志方便调试
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))



@router.post("/refreshToken", summary="刷新认证")
async def refresh_token(jwt_token: JWTOut):
    if not jwt_token.refresh_token:
        return Fail(code="4000", msg="The refreshToken is not valid.")
    status, code, data = check_token(jwt_token.refresh_token)
    if not status:
        return Fail(code=code, msg=data)
    user_id = data["data"]["userId"]
    user_obj = await user_controller.get(user_id)

    if data["data"]["tokenType"] != "refreshToken":
        return Fail(code="4000", msg="The token is not an refresh token.")

    if user_obj.status == StatusType.disable:
        await insert_log(log_type=LogType.UserLog, log_detail_type=LogDetailType.UserLoginForbid, by_user_id=user_id)
        return Fail(code="4030", msg="This user has been disabled.")

    await user_controller.update_last_login(user_id)
    payload = JWTPayload(
        data={"userId": user_obj.id, "userName": user_obj.user_name, "tokenType": "accessToken"},
        iat=datetime.now(timezone.utc),
        exp=datetime.now(timezone.utc)
    )
    access_token_payload = payload.model_copy()
    access_token_payload.exp += timedelta(minutes=APP_SETTINGS.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_token_payload = payload.model_copy()
    refresh_token_payload.data["tokenType"] = "refreshToken"
    refresh_token_payload.exp += timedelta(minutes=APP_SETTINGS.JWT_REFRESH_TOKEN_EXPIRE_MINUTES)
    data = JWTOut(
        access_token=create_access_token(data=access_token_payload),
        refresh_token=create_access_token(data=refresh_token_payload),
    )
    await insert_log(log_type=LogType.UserLog, log_detail_type=LogDetailType.UserAuthRefreshTokenSuccess, by_user_id=user_obj.id)
    return Success(data=data.model_dump(by_alias=True))


@router.get("/getUserInfo", summary="查看用户信息", dependencies=[DependAuth])
async def get_user_info():
    user_id = CTX_USER_ID.get()
    user_obj: User = await user_controller.get(id=user_id)
    if user_obj is None:
        return Fail(code="4000", msg="用户不存在。")
    # data = await user_obj.to_dict(exclude_fields=["password"])
    data = await model_to_dict(user_obj,exclude_fields=["password"])

    user_roles: list[Role] = await user_obj.roles
    user_role_codes = [user_role.role_code for user_role in user_roles]

    user_role_button_codes = [b.button_code for b in await Button.all()] if "R_SUPER" in user_role_codes else [b.button_code for user_role in user_roles for b in await user_role.buttons]

    user_role_button_codes = list(set(user_role_button_codes))

    data.update({
        "user_id": user_id,
        "roles": user_role_codes,
        "buttons": user_role_button_codes
    })
    await insert_log(log_type=LogType.UserLog, log_detail_type=LogDetailType.UserLoginGetUserInfo, by_user_id=user_obj.id)
    return Success(data=data)


@router.get("/error", summary="自定义后端错误")  # todo 使用限流器, 每秒最多一次
async def check_error(code: str, msg: str):
    if code == "9999":
        return Success(code="4030", msg="accessToken已过期")

    return Fail(code=code, msg=f"未知错误, code: {code} msg: {msg}")




