from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.database import engine, Base
import os

# 导入模型以确保它们被注册
from app.models.user import UserInfo
from app.models.project import ProjectInfo
from app.models.api_test import APIInfo
from app.models.ui_test import UIInfo
from app.models.business_flow import BusinessFlow
from app.models.test_reports import TestReports


# 创建数据库表
try:
    Base.metadata.create_all(bind=engine)
    print("✓ 数据库表创建成功")
except Exception as e:
    print(f"✗ 数据库表创建失败: {e}")

app = FastAPI(
    title="Testing Platform API",
    description="A comprehensive testing platform with API, UI, and performance testing capabilities",
    version="1.0.0"
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载静态文件
os.makedirs("static/avatars", exist_ok=True)
os.makedirs("reports", exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/reports", StaticFiles(directory="reports"), name="reports")


# 导入并注册路由
try:
    from app.api.users import router as users_router
    app.include_router(users_router, prefix="/api/v1", tags=["users"])
    print("✓ Users routes loaded successfully")
except Exception as e:
    print(f"✗ Error loading users routes: {e}")

try:
    from app.api.projects import router as projects_router
    app.include_router(projects_router, prefix="/api/v1", tags=["projects"])
    print("✓ Projects routes loaded successfully")
except Exception as e:
    print(f"✗ Error loading projects routes: {e}")

try:
    from app.api.api_tests import router as api_tests_router
    app.include_router(api_tests_router, prefix="/api/v1", tags=["api-test-cases"])
    print("✓ API Tests routes loaded successfully")
except Exception as e:
    print(f"✗ Error loading API tests routes: {e}")

try:
    from app.api.ui_tests import router as ui_tests_router
    app.include_router(ui_tests_router, prefix="/api/v1", tags=["ui-tests"])
    print("✓ UI Tests routes loaded successfully")
except Exception as e:
    print(f"✗ Error loading UI tests routes: {e}")

try:
    from app.api.performance import router as performance_router
    app.include_router(performance_router, prefix="/api/v1", tags=["performance"])
    print("✓ Performance routes loaded successfully")
except Exception as e:
    print(f"✗ Error loading performance routes: {e}")

@app.get("/")
def read_root():
    return {"message": "Testing Platform API is running"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)