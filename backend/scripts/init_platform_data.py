#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
初始化平台详情数据脚本
执行以下步骤：
1. 检查数据库连接
2. 添加新的数据库列（如果尚未存在）
3. 初始化三个主要平台的详情数据
"""
import json
import sys
from pathlib import Path

# 添加项目根路径到Python路径
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import Column, String, inspect, text
from app.database import SessionLocal, engine
from app.models import Platform
from datetime import datetime


def get_db_session():
    """获取数据库连接"""
    try:
        db = SessionLocal()
        # 测试连接
        db.execute(text("SELECT 1"))
        print("✓ 数据库连接成功")
        return db
    except Exception as e:
        print(f"✗ 数据库连接失败: {e}")
        sys.exit(1)


def check_and_add_columns(db):
    """检查并添加缺失的数据库列"""
    print("\n=== 检查数据库列 ===")
    
    inspector = inspect(engine)
    platform_columns = {col['name'] for col in inspector.get_columns('platform')}
    
    required_columns = {
        'why_choose', 'account_types', 'fee_table', 'trading_tools',
        'opening_steps', 'safety_info', 'learning_resources',
        'overview_intro', 'top_badges'
    }
    
    missing_columns = required_columns - platform_columns
    
    if missing_columns:
        print(f"需要添加 {len(missing_columns)} 个列: {missing_columns}")
        
        for col_name in missing_columns:
            try:
                db.execute(text(f"ALTER TABLE platform ADD COLUMN {col_name} TEXT"))
                print(f"  ✓ 添加列: {col_name}")
            except Exception as e:
                if "already exists" in str(e) or "duplicate" in str(e).lower():
                    print(f"  ℹ 列已存在: {col_name}")
                else:
                    print(f"  ✗ 添加列失败 {col_name}: {e}")
        
        db.commit()
        print("✓ 所有列已添加")
    else:
        print("✓ 所有必需的列都已存在")
    
    return missing_columns


# ===== 平台详情数据模板 =====

ALPHA_LEVERAGE_DATA = {
    "overview_intro": "AlphaLeverage 是一个专为专业交易者设计的高杠杆交易平台。提供业界最高的杠杆比率和最低的交易成本，支持多种交易工具和24/7专业客户支持。",
    
    "why_choose": json.dumps([
        {
            "icon": "📈",
            "title": "最高杠杆比率",
            "description": "提供高达1:500的杠杆比率，让专业交易者获得更大的交易收益机会"
        },
        {
            "icon": "💰",
            "title": "最低交易费用",
            "description": "行业内最低的佣金费率（0.15%起），节省交易成本"
        },
        {
            "icon": "🛠️",
            "title": "高级交易工具",
            "description": "提供专业级的图表分析、风险管理工具和实时数据推送"
        },
        {
            "icon": "🌙",
            "title": "24/7专业支持",
            "description": "全天候多语言客户支持团队，快速解决问题"
        }
    ], ensure_ascii=False),
    
    "account_types": json.dumps([
        {
            "name": "基础账户",
            "leverage": "1:100",
            "min_deposit": "$5,000",
            "fee": "0.20%",
            "description": "适合活跃交易者",
            "features": ["基础分析工具", "标准支持"]
        },
        {
            "name": "VIP账户",
            "leverage": "1:500",
            "min_deposit": "$50,000",
            "fee": "0.10%",
            "description": "为专业交易者提供",
            "features": ["高级分析工具", "优先支持", "个人经理"]
        }
    ], ensure_ascii=False),
    
    "fee_table": json.dumps([
        {"type": "交易手续费", "basic": "0.20%", "vip": "0.10%"},
        {"type": "借款利息", "basic": "6-8%", "vip": "4-6%"},
        {"type": "提现费用", "basic": "免费", "vip": "免费"},
        {"type": "账户维护费", "basic": "免费", "vip": "免费"},
        {"type": "API接口费", "basic": "$99/月", "vip": "包含"}
    ], ensure_ascii=False),
    
    "trading_tools": json.dumps([
        {"title": "高级图表工具", "description": "支持30多种技术指标和K线图形"},
        {"title": "风险管理工具", "description": "止损、止盈、追踪止损等高级功能"},
        {"title": "实时数据", "description": "市场深度、价格走势等实时推送"},
        {"title": "API接口", "description": "强大的API接口支持自动化交易"}
    ], ensure_ascii=False),
    
    "opening_steps": json.dumps([
        {
            "step_number": 1,
            "title": "创建账户",
            "description": "注册账户并进行身份验证(KYC)"
        },
        {
            "step_number": 2,
            "title": "充值资金",
            "description": "选择支付方式进行存款(最低$5,000)"
        },
        {
            "step_number": 3,
            "title": "开始交易",
            "description": "下载交易平台，配置参数后立即开始交易"
        }
    ], ensure_ascii=False),
    
    "safety_info": json.dumps([
        "✓ 获得FCA、ASIC等多国监管",
        "✓ 资金隔离保护(客户资金单独存管)",
        "✓ 256位SSL加密，安全等级AAA",
        "✓ 通过国际ISO 9001认证",
        "✓ 定期安全审计和风险评估"
    ], ensure_ascii=False),
    
    "learning_resources": json.dumps([
        {
            "title": "交易教程库",
            "description": "从基础到进阶的完整视频教程",
            "link": "/resources/tutorials"
        },
        {
            "title": "实时行情分析",
            "description": "专业分析师每日市场评述",
            "link": "/resources/analysis"
        },
        {
            "title": "策略分享",
            "description": "成功交易者的策略模板和代码",
            "link": "/resources/strategies"
        }
    ], ensure_ascii=False),
    
    "top_badges": json.dumps([
        "推荐平台",
        "专业级交易",
        "最高杠杆"
    ], ensure_ascii=False)
}


BETA_MARGIN_DATA = {
    "overview_intro": "BetaMargin 是一个平衡专业性和易用性的交易平台。为中等杠杆交易者提供稳定、可靠的交易基础设施和公平的费用结构。",
    
    "why_choose": json.dumps([
        {
            "icon": "🏢",
            "title": "可靠的基础设施",
            "description": "多个数据中心冗余保障，99.99%正常运行时间"
        },
        {
            "icon": "⚖️",
            "title": "公平的费率结构",
            "description": "透明的费用体系，没有隐藏费用"
        },
        {
            "icon": "🛡️",
            "title": "风险管理工具",
            "description": "内置风险管理工具帮助控制交易风险"
        },
        {
            "icon": "📱",
            "title": "跨平台支持",
            "description": "桌面、网页、移动三平台无缝同步"
        }
    ], ensure_ascii=False),
    
    "account_types": json.dumps([
        {
            "name": "基础账户",
            "leverage": "1:30",
            "min_deposit": "$2,000",
            "fee": "0.15%",
            "description": "适合初学者和活跃交易者",
            "features": ["24/5客户支持", "基础分析工具"]
        },
        {
            "name": "专业账户",
            "leverage": "1:50",
            "min_deposit": "$10,000",
            "fee": "0.12%",
            "description": "为经验丰富的交易者设计",
            "features": ["优先支持", "高级工具", "量化交易接口"]
        }
    ], ensure_ascii=False),
    
    "fee_table": json.dumps([
        {"type": "交易手续费", "basic": "0.15%", "pro": "0.12%"},
        {"type": "借款利息", "basic": "5-7%", "pro": "4-5%"},
        {"type": "提现费用", "basic": "免费", "pro": "免费"},
        {"type": "账户维护费", "basic": "免费", "pro": "免费"},
        {"type": "VPS费用", "basic": "$19.99/月", "pro": "包含"}
    ], ensure_ascii=False),
    
    "trading_tools": json.dumps([
        {"title": "高级图表分析", "description": "TradingView集成，100+指标支持"},
        {"title": "风险管理工具", "description": "动态止损、追踪止盈等"},
        {"title": "实时推送", "description": "价格、新闻、经济日历实时通知"},
        {"title": "移动应用", "description": "iOS和Android应用程序"}
    ], ensure_ascii=False),
    
    "opening_steps": json.dumps([
        {
            "step_number": 1,
            "title": "注册账户",
            "description": "填写基本信息，验证邮箱和电话"
        },
        {
            "step_number": 2,
            "title": "身份认证",
            "description": "完成KYC认证，上传身份证件"
        },
        {
            "step_number": 3,
            "title": "资金入账",
            "description": "通过银行卡、支付宝等方式存款"
        }
    ], ensure_ascii=False),
    
    "safety_info": json.dumps([
        "✓ 受英国FCA和欧盟CySEC双重监管",
        "✓ 客户资金由第三方银行独立管理",
        "✓ 支持高达20万欧元的投资者保护计划",
        "✓ 定期进行第三方审计",
        "✓ 256位加密和双因素认证"
    ], ensure_ascii=False),
    
    "learning_resources": json.dumps([
        {
            "title": "新手指南",
            "description": "外汇交易入门完全手册",
            "link": "/resources/guides"
        },
        {
            "title": "每日市场分析",
            "description": "专业分析师的技术分析和操作建议",
            "link": "/resources/daily-analysis"
        },
        {
            "title": "WebRTC直播间",
            "description": "每周在线讲座和交易讨论",
            "link": "/resources/live"
        }
    ], ensure_ascii=False),
    
    "top_badges": json.dumps([
        "成熟稳定",
        "平衡型平台",
        "新手友好"
    ], ensure_ascii=False)
}


GAMMA_TRADER_DATA = {
    "overview_intro": "GammaTrader 是专为初学者设计的教育导向型交易平台。提供简化的交易界面、完整的教育资源和安全可靠的低成本交易环境。",
    
    "why_choose": json.dumps([
        {
            "icon": "📚",
            "title": "教育优先",
            "description": "提供全面的学习资源，从基础到进阶的完整课程"
        },
        {
            "icon": "🔒",
            "title": "安全优先",
            "description": "低杠杆设置和风险控制工具，最大化保护新手资金"
        },
        {
            "icon": "💵",
            "title": "低成本起步",
            "description": "最低入金$500，行业内最低费率0.10%"
        },
        {
            "icon": "☁️",
            "title": "简化界面",
            "description": "直观易用的交易界面，快速上手"
        }
    ], ensure_ascii=False),
    
    "account_types": json.dumps([
        {
            "name": "入门账户",
            "leverage": "1:20",
            "min_deposit": "$500",
            "fee": "0.10%",
            "description": "完全初学者的最佳选择",
            "features": ["教育资源", "模拟交易", "新手支持"]
        },
        {
            "name": "标准账户",
            "leverage": "1:50",
            "min_deposit": "$5,000",
            "fee": "0.08%",
            "description": "进阶交易者的理想选择",
            "features": ["全面工具", "优先支持", "个性化学习计划"]
        }
    ], ensure_ascii=False),
    
    "fee_table": json.dumps([
        {"type": "交易手续费", "starter": "0.10%", "standard": "0.08%"},
        {"type": "借款利息", "starter": "4-5%", "standard": "3-4%"},
        {"type": "提现费用", "starter": "免费", "standard": "免费"},
        {"type": "教学资源", "starter": "完全免费", "standard": "完全免费"},
        {"type": "VPS", "starter": "$0", "standard": "$0"}
    ], ensure_ascii=False),
    
    "trading_tools": json.dumps([
        {"title": "教育资源库", "description": "100+小时视频教程和交易指南"},
        {"title": "简化交易界面", "description": "一键下单，自动风险计算"},
        {"title": "新手保护工具", "description": "自动止损、风险提示等"},
        {"title": "社区支持", "description": "交易者社区，分享经验和策略"}
    ], ensure_ascii=False),
    
    "opening_steps": json.dumps([
        {
            "step_number": 1,
            "title": "快速注册",
            "description": "仅需邮箱和密码，2分钟完成"
        },
        {
            "step_number": 2,
            "title": "学习基础知识",
            "description": "完成入门课程，了解交易基础"
        },
        {
            "step_number": 3,
            "title": "入金交易",
            "description": "最低入金$500，立即开始交易之旅"
        }
    ], ensure_ascii=False),
    
    "safety_info": json.dumps([
        "✓ 新手保护计划：首笔交易风险补偿",
        "✓ 所有资金存放在持证银行",
        "✓ 强制止损保护，永远不会亏损超过账户本金",
        "✓ 定期安全培训和风险警示",
        "✓ 银行级别的数据加密技术"
    ], ensure_ascii=False),
    
    "learning_resources": json.dumps([
        {
            "title": "交易入门课程",
            "description": "从零开始学习外汇交易基础",
            "link": "/resources/courses/beginner"
        },
        {
            "title": "每周直播讲座",
            "description": "专家讲解市场动态和交易技巧",
            "link": "/resources/webinars"
        },
        {
            "title": "模拟交易练习",
            "description": "使用虚拟资金练习，零风险学习",
            "link": "/resources/demo"
        },
        {
            "title": "常见问题解答",
            "description": "初学者最常问问题的解答库",
            "link": "/resources/faq"
        }
    ], ensure_ascii=False),
    
    "top_badges": json.dumps([
        "新手友好",
        "教育平台",
        "低成本"
    ], ensure_ascii=False)
}


def update_platform_details(db):
    """更新三个平台的详情数据"""
    print("\n=== 初始化平台详情数据 ===")
    
    platforms_to_update = [
        ("alpha-leverage", ALPHA_LEVERAGE_DATA),
        ("beta-margin", BETA_MARGIN_DATA),
        ("gamma-trader", GAMMA_TRADER_DATA),
    ]
    
    for slug, data in platforms_to_update:
        try:
            platform = db.query(Platform).filter(Platform.slug == slug).first()
            if not platform:
                print(f"✗ 找不到平台: {slug}")
                continue
            
            # 更新所有字段
            for field_name, field_value in data.items():
                setattr(platform, field_name, field_value)
            
            platform.updated_at = datetime.utcnow()
            db.commit()
            print(f"✓ 更新平台: {platform.name} ({slug})")
            
        except Exception as e:
            print(f"✗ 更新平台失败 {slug}: {e}")
            db.rollback()


def main():
    """主函数"""
    print("=" * 50)
    print("平台详情数据初始化脚本")
    print("=" * 50)
    
    # 获取数据库连接
    db = get_db_session()
    
    try:
        # 检查并添加数据库列
        check_and_add_columns(db)
        
        # 初始化平台详情数据
        update_platform_details(db)
        
        print("\n" + "=" * 50)
        print("✓ 初始化完成！")
        print("=" * 50)
        
    except Exception as e:
        print(f"\n✗ 出现错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    finally:
        db.close()


if __name__ == "__main__":
    main()
