#!/usr/bin/env python3
"""
测试 Schema 验证和 ORM 查询
"""
import sys
from pathlib import Path

backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from app.models import Platform
from app.schemas.platform import PlatformResponse, PlatformListResponse

# 创建数据库连接
db_url = f"sqlite:///{backend_dir}/trustagency.db"
engine = create_engine(db_url)

print("=" * 60)
print("🧪 ORM 和 Schema 验证测试")
print("=" * 60)

with Session(engine) as db:
    # 查询平台
    print("\n1️⃣  查询第一个平台...")
    platform = db.query(Platform).first()
    
    if not platform:
        print("   ❌ 没有找到平台")
        sys.exit(1)
    
    print(f"   ✅ 找到平台: {platform.name}")
    print(f"      ID: {platform.id}")
    print(f"      Type: {platform.platform_type}")
    
    # 尝试验证 Schema
    print("\n2️⃣  验证 PlatformResponse Schema...")
    try:
        platform_response = PlatformResponse.model_validate(platform)
        print("   ✅ Schema 验证成功!")
        print(f"      JSON: {platform_response.model_dump_json()[:100]}...")
    except Exception as e:
        print(f"   ❌ Schema 验证失败: {e}")
        import traceback
        traceback.print_exc()
    
    # 查询所有平台
    print("\n3️⃣  查询所有平台...")
    platforms = db.query(Platform).all()
    print(f"   ✅ 找到 {len(platforms)} 个平台")
    
    # 尝试创建 ListResponse
    print("\n4️⃣  创建 PlatformListResponse...")
    try:
        platform_responses = [PlatformResponse.model_validate(p) for p in platforms]
        list_response = PlatformListResponse(
            data=platform_responses,
            total=len(platforms),
            skip=0,
            limit=10
        )
        print("   ✅ ListResponse 创建成功!")
        json_str = list_response.model_dump_json()
        print(f"      JSON 长度: {len(json_str)} 字节")
        print(f"      前 200 个字符: {json_str[:200]}...")
    except Exception as e:
        print(f"   ❌ ListResponse 创建失败: {e}")
        import traceback
        traceback.print_exc()

print("\n" + "=" * 60)
print("✅ 测试完成")
print("=" * 60)
