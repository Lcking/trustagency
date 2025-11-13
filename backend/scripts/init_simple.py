#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
简化版初始化脚本 - 添加数据库列和初始化数据
"""
import sys
import os

# 添加后端目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import json
from pathlib import Path
from datetime import datetime

try:
    from sqlalchemy import text, inspect
    from app.database import SessionLocal, engine
    from app.models import Platform
except ImportError as e:
    print(f"导入错误: {e}")
    print(f"Python路径: {sys.path}")
    sys.exit(1)


def main():
    print("=" * 50)
    print("平台详情数据初始化")
    print("=" * 50)
    
    # 连接数据库
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        print("✓ 数据库连接成功")
    except Exception as e:
        print(f"✗ 数据库连接失败: {e}")
        return False
    
    # 检查并添加列
    print("\n检查数据库列...")
    inspector = inspect(engine)
    columns = {col['name'] for col in inspector.get_columns('platform')}
    
    new_columns = {
        'why_choose', 'account_types', 'fee_table', 'trading_tools',
        'opening_steps', 'safety_info', 'learning_resources',
        'overview_intro', 'top_badges'
    }
    
    missing = new_columns - columns
    if missing:
        print(f"需要添加 {len(missing)} 列: {missing}")
        for col_name in missing:
            try:
                db.execute(text(f"ALTER TABLE platform ADD COLUMN {col_name} TEXT"))
                print(f"  ✓ {col_name}")
            except Exception as e:
                if "already exists" not in str(e) and "duplicate" not in str(e).lower():
                    print(f"  ✗ {col_name}: {e}")
        db.commit()
    else:
        print("✓ 所有列都已存在")
    
    # 更新平台数据
    print("\n初始化平台数据...")
    
    platforms_data = {
        'alpha-leverage': {
            'why_choose': json.dumps([
                {'icon': '📈', 'title': '最高杠杆比率', 'description': '提供高达1:500的杠杆比率'},
                {'icon': '💰', 'title': '最低交易费用', 'description': '行业内最低的佣金费率（0.15%起）'},
                {'icon': '🛠️', 'title': '高级交易工具', 'description': '专业级的图表分析和风险管理工具'},
                {'icon': '🌙', 'title': '24/7专业支持', 'description': '全天候多语言客户支持团队'}
            ], ensure_ascii=False),
            'account_types': json.dumps([
                {'name': '基础账户', 'leverage': '1:100', 'min_deposit': '$5,000', 'fee': '0.20%'},
                {'name': 'VIP账户', 'leverage': '1:500', 'min_deposit': '$50,000', 'fee': '0.10%'}
            ], ensure_ascii=False),
            'fee_table': json.dumps([
                {'type': '交易手续费', 'basic': '0.20%', 'vip': '0.10%'},
                {'type': '借款利息', 'basic': '6-8%', 'vip': '4-6%'},
                {'type': '提现费用', 'basic': '免费', 'vip': '免费'},
                {'type': '账户维护费', 'basic': '免费', 'vip': '免费'},
                {'type': 'API接口费', 'basic': '$99/月', 'vip': '包含'}
            ], ensure_ascii=False),
            'trading_tools': json.dumps([
                {'title': '高级图表工具', 'description': '支持30多种技术指标'},
                {'title': '风险管理工具', 'description': '止损、止盈等高级功能'},
                {'title': '实时数据', 'description': '市场深度实时推送'},
                {'title': 'API接口', 'description': '支持自动化交易'}
            ], ensure_ascii=False),
            'overview_intro': 'AlphaLeverage是一个专为专业交易者设计的高杠杆交易平台'
        },
        'beta-margin': {
            'why_choose': json.dumps([
                {'icon': '🏢', 'title': '可靠的基础设施', 'description': '99.99%正常运行时间'},
                {'icon': '⚖️', 'title': '公平的费率结构', 'description': '透明的费用体系'},
                {'icon': '🛡️', 'title': '风险管理工具', 'description': '内置风险管理工具'},
                {'icon': '📱', 'title': '跨平台支持', 'description': '桌面、网页、移动无缝同步'}
            ], ensure_ascii=False),
            'account_types': json.dumps([
                {'name': '基础账户', 'leverage': '1:30', 'min_deposit': '$2,000', 'fee': '0.15%'},
                {'name': '专业账户', 'leverage': '1:50', 'min_deposit': '$10,000', 'fee': '0.12%'}
            ], ensure_ascii=False),
            'fee_table': json.dumps([
                {'type': '交易手续费', 'basic': '0.15%', 'pro': '0.12%'},
                {'type': '借款利息', 'basic': '5-7%', 'pro': '4-5%'},
                {'type': '提现费用', 'basic': '免费', 'pro': '免费'},
                {'type': '账户维护费', 'basic': '免费', 'pro': '免费'},
                {'type': 'VPS费用', 'basic': '$19.99/月', 'pro': '包含'}
            ], ensure_ascii=False),
            'trading_tools': json.dumps([
                {'title': '高级图表分析', 'description': '100+指标支持'},
                {'title': '风险管理工具', 'description': '动态止损'},
                {'title': '实时推送', 'description': '价格和新闻推送'},
                {'title': '移动应用', 'description': 'iOS和Android应用'}
            ], ensure_ascii=False),
            'overview_intro': 'BetaMargin是一个平衡专业性和易用性的交易平台'
        },
        'gamma-trader': {
            'why_choose': json.dumps([
                {'icon': '📚', 'title': '教育优先', 'description': '提供全面的学习资源'},
                {'icon': '🔒', 'title': '安全优先', 'description': '低杠杆设置和风险控制'},
                {'icon': '💵', 'title': '低成本起步', 'description': '最低入金$500'},
                {'icon': '☁️', 'title': '简化界面', 'description': '直观易用的交易界面'}
            ], ensure_ascii=False),
            'account_types': json.dumps([
                {'name': '入门账户', 'leverage': '1:20', 'min_deposit': '$500', 'fee': '0.10%'},
                {'name': '标准账户', 'leverage': '1:50', 'min_deposit': '$5,000', 'fee': '0.08%'}
            ], ensure_ascii=False),
            'fee_table': json.dumps([
                {'type': '交易手续费', 'starter': '0.10%', 'standard': '0.08%'},
                {'type': '借款利息', 'starter': '4-5%', 'standard': '3-4%'},
                {'type': '提现费用', 'starter': '免费', 'standard': '免费'},
                {'type': '教学资源', 'starter': '完全免费', 'standard': '完全免费'},
                {'type': 'VPS', 'starter': '$0', 'standard': '$0'}
            ], ensure_ascii=False),
            'trading_tools': json.dumps([
                {'title': '教育资源库', 'description': '100+小时视频教程'},
                {'title': '简化交易界面', 'description': '一键下单'},
                {'title': '新手保护工具', 'description': '自动止损'},
                {'title': '社区支持', 'description': '交易者社区'}
            ], ensure_ascii=False),
            'overview_intro': 'GammaTrader是专为初学者设计的教育导向型交易平台'
        }
    }
    
    for slug, data in platforms_data.items():
        try:
            platform = db.query(Platform).filter(Platform.slug == slug).first()
            if not platform:
                print(f"  ⚠ 平台不存在: {slug}")
                continue
            
            for field, value in data.items():
                setattr(platform, field, value)
            
            platform.updated_at = datetime.utcnow()
            db.commit()
            print(f"  ✓ {platform.name}")
        except Exception as e:
            print(f"  ✗ {slug}: {e}")
            db.rollback()
    
    db.close()
    print("\n✓ 初始化完成！")
    return True


if __name__ == '__main__':
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
