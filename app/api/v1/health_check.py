from fastapi import APIRouter

# 创建一个APIRouter实例
router = APIRouter()

@router.get("/health")
async def health_check():

    return {"status": "healthy"}
    