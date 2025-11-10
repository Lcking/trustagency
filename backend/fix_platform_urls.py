#!/usr/bin/env python3
"""
检查并更新平台数据中的website_url字段
"""
import sys
sys.path.insert(0, '.')

from app.database import SessionLocal
from app.models.platform import Platform

db = SessionLocal()

try:
    platforms = db.query(Platform).all()
    print("=" * 60)
    print("数据库中的平台数据:")
    print("=" * 60)
    
    for p in platforms:
        print(f"ID: {p.id}, 名称: {p.name}")
        print(f"  website_url: {p.website_url}")
        print()
    
    # 如果有平台的website_url为null，修复它
    print("=" * 60)
    print("更新平台数据...")
    print("=" * 60)
    
    platform_urls = {
        "AlphaLeverage": "https://alphaleverage.com",
        "BetaMargin": "https://betamargin.com",
        "GammaTrader": "https://gammatrader.com",
    }
    
    updated = 0
    for name, url in platform_urls.items():
        p = db.query(Platform).filter(Platform.name == name).first()
        if p:
            if not p.website_url or p.website_url != url:
                print(f"更新 {name}: {p.website_url} -> {url}")
                p.website_url = url
                updated += 1
            else:
                print(f"✅ {name}: 已有正确的URL")
    
    if updated > 0:
        db.commit()
        print(f"\n✅ 已更新 {updated} 个平台的website_url")
    else:
        print("\n✅ 所有平台都已有正确的URL")
    
    # 再次检查
    print("\n" + "=" * 60)
    print("更新后的平台数据:")
    print("=" * 60)
    
    db.refresh()  # 刷新会话
    platforms = db.query(Platform).all()
    for p in platforms:
        print(f"✅ {p.name}: {p.website_url}")

except Exception as e:
    print(f"❌ 错误: {e}")
    import traceback
    traceback.print_exc()

finally:
    db.close()
    print("\n✅ 完成")
