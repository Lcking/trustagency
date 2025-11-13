#!/usr/bin/env python3
"""
平台详情页面数据模板和初始化脚本
根据前端现有的两个页面结构，生成结构化的后端数据
"""
import json
from typing import Dict, List, Any

# ===== AlphaLeverage 平台详情数据 =====
ALPHA_LEVERAGE_DETAILS = {
    "platform_type": "专业",
    "platform_badges": ["推荐平台", "高杠杆", "极速执行"],
    
    "why_choose": json.dumps([
        {
            "icon": "🚀",
            "title": "极速执行",
            "description": "毫秒级订单执行速度，不错过任何交易机会。"
        },
        {
            "icon": "💰",
            "title": "低成本交易",
            "description": "行业最低的手续费，最大化你的交易收益。"
        },
        {
            "icon": "🔓",
            "title": "高杠杆比例",
            "description": "最高500倍杠杆，充分利用资本进行大额交易。"
        },
        {
            "icon": "📊",
            "title": "丰富货币对",
            "description": "支持150+交易对，涵盖主流和新兴市场。"
        }
    ]),
    
    "trading_conditions": json.dumps([
        {"label": "最大杠杆", "value": "1:500"},
        {"label": "最低入金", "value": "$1,000"},
        {"label": "最小交易量", "value": "0.01手"},
        {"label": "交易时间", "value": "24/5"}
    ]),
    
    "fee_advantages": json.dumps([
        {"label": "交易手续费", "value": "0.5点"},
        {"label": "隔夜利息", "value": "年 2-4%"},
        {"label": "取款费", "value": "免费"},
        {"label": "账户维护费", "value": "$0"}
    ]),
    
    "account_types": json.dumps([
        {
            "name": "标准账户",
            "suitable_for": "活跃交易者",
            "leverage": "1:100 - 1:300",
            "min_deposit": "$1,000",
            "commission": "0.5点",
            "features": [
                "杠杆比例: 1:100 - 1:300",
                "最低入金: $1,000",
                "手续费: 0.5点",
                "24/5 客户支持",
                "高级分析工具"
            ],
            "cta_text": "立即开户",
            "cta_link": "https://alphaleverage.com/open-account"
        },
        {
            "name": "VIP账户",
            "suitable_for": "专业交易者",
            "leverage": "1:300 - 1:500",
            "min_deposit": "$10,000",
            "commission": "0.3点",
            "features": [
                "杠杆比例: 1:300 - 1:500",
                "最低入金: $10,000",
                "手续费: 0.3点",
                "优先客户支持",
                "个人账户经理",
                "定制交易工具"
            ],
            "cta_text": "升级到VIP",
            "cta_link": "https://alphaleverage.com/vip"
        }
    ]),
    
    "trading_tools": json.dumps([
        {
            "title": "MetaTrader 5终端",
            "description": "业界领先的交易平台，支持自动交易和高级分析。"
        },
        {
            "title": "高级图表分析",
            "description": "50+ 技术指标，自定义时间框架，绘图工具完整。"
        },
        {
            "title": "风险管理工具",
            "description": "止损、获利订单、保证金监控、自动清算保护。"
        },
        {
            "title": "经济日历",
            "description": "实时经济数据、市场新闻提示、宏观经济分析。"
        },
        {
            "title": "移动应用",
            "description": "iOS 和 Android 原生应用，随时随地交易。"
        }
    ]),
    
    "opening_steps": json.dumps([
        {
            "step_number": 1,
            "title": "创建账户",
            "description": "填写邮箱、设置密码，2分钟完成注册。",
            "icon_color": "primary"
        },
        {
            "step_number": 2,
            "title": "验证身份",
            "description": "上传身份证件照片进行KYC认证。",
            "icon_color": "info"
        },
        {
            "step_number": 3,
            "title": "入金交易",
            "description": "支持多种支付方式，最低$1,000即可开始交易。",
            "icon_color": "success"
        }
    ]),
    
    "security_measures": json.dumps([
        {"text": "✓ 资金独立托管 - 客户资金与公司资金分离"},
        {"text": "✓ 加密数据传输 - 256位SSL加密连接"},
        {"text": "✓ 定期安全审计 - 第三方安全认证"},
        {"text": "✓ 保证金保护 - 负数保护政策"},
        {"text": "✓ 风险警告系统 - 实时保证金监控"}
    ]),
    
    "customer_support": json.dumps([
        {"type": "24/5 在线支持", "description": "通过在线客服、邮件和电话获得即时帮助。"},
        {"type": "中文支持", "description": "专业的中文客服团队，语言无障碍。"},
        {"type": "新手教程", "description": "详细的视频教程和交易指南。"},
        {"type": "VIP服务", "description": "VIP账户用户享受个人账户经理服务。"}
    ]),
    
    "learning_resources": json.dumps([
        {
            "title": "新手交易指南",
            "description": "从零开始学习杠杆交易基础知识",
            "link": "/guides/beginner"
        },
        {
            "title": "高级交易策略",
            "description": "学习专业交易者的策略和技巧",
            "link": "/guides/strategy"
        },
        {
            "title": "风险管理课程",
            "description": "掌握风险管理，保护你的交易资本",
            "link": "/guides/risk-management"
        },
        {
            "title": "市场分析工坊",
            "description": "每周直播分析和交易机会讨论",
            "link": "/workshops"
        }
    ])
}

# ===== BetaMargin 平台详情数据 =====
BETA_MARGIN_DETAILS = {
    "platform_type": "平衡",
    "platform_badges": ["推荐平台", "平衡杠杆", "专业工具"],
    
    "why_choose": None,  # Beta Margin页面没有"为什么选择"部分，用交易条件和费用优势代替
    
    "trading_conditions": json.dumps([
        {"label": "最大杠杆", "value": "1:50"},
        {"label": "最低入金", "value": "$2,000"},
        {"label": "最小交易量", "value": "1股"},
        {"label": "交易时间", "value": "24/5"}
    ]),
    
    "fee_advantages": json.dumps([
        {"label": "交易手续费", "value": "0.10-0.20%"},
        {"label": "借款利息", "value": "年 4-6%"},
        {"label": "取款费", "value": "免费"},
        {"label": "账户维护费", "value": "$0"}
    ]),
    
    "account_types": json.dumps([
        {
            "name": "基础账户",
            "suitable_for": "进阶初学者和活跃交易者",
            "leverage": "1:10 - 1:30",
            "min_deposit": "$2,000",
            "commission": "0.15%",
            "features": [
                "杠杆比例：1:10 - 1:30",
                "最低入金：$2,000",
                "交易手续费：0.15%",
                "24/5 客户支持"
            ],
            "cta_text": "立即开户",
            "cta_link": "/guides/open-account/"
        },
        {
            "name": "专业账户",
            "suitable_for": "经验丰富的专业交易者",
            "leverage": "1:30 - 1:50",
            "min_deposit": "$10,000",
            "commission": "0.10%",
            "features": [
                "杠杆比例：1:30 - 1:50",
                "最低入金：$10,000",
                "交易手续费：0.10%",
                "优先客户支持",
                "高级分析工具"
            ],
            "cta_text": "升级到专业",
            "cta_link": "/guides/upgrade"
        }
    ]),
    
    "trading_tools": json.dumps([
        {
            "title": "高级图表工具",
            "description": "支持 50+ 技术指标，自定义时间框架，绘图工具集。"
        },
        {
            "title": "风险管理工具",
            "description": "止损订单、获利订单、保证金追加警告、自动清算保护。"
        },
        {
            "title": "实时数据",
            "description": "实时股票报价、市场深度、新闻提示、经济日历。"
        },
        {
            "title": "移动应用",
            "description": "iOS 和 Android 原生应用，随时随地交易。"
        }
    ]),
    
    "opening_steps": json.dumps([
        {
            "step_number": 1,
            "title": "注册账户",
            "description": "填写基本信息，创建账户。",
            "icon_color": "primary"
        },
        {
            "step_number": 2,
            "title": "验证身份",
            "description": "上传身份证明文件。",
            "icon_color": "info"
        },
        {
            "step_number": 3,
            "title": "入金交易",
            "description": "$2,000 起即可开始。",
            "icon_color": "success"
        }
    ]),
    
    "security_measures": json.dumps([
        {"text": "✓ 自律监管机制"},
        {"text": "✓ 资金独立管理"},
        {"text": "✓ 加密数据传输"},
        {"text": "✓ 定期安全审计"},
        {"text": "✓ 保证金保护政策"}
    ]),
    
    "customer_support": json.dumps([
        {"type": "24/5 客户支持", "description": "通过多种渠道获得即时帮助。"},
        {"type": "优先支持", "description": "VIP账户用户享受优先支持。"},
        {"type": "新手教程", "description": "丰富的交易教程和网络研讨会。"}
    ]),
    
    "learning_resources": json.dumps([
        {
            "title": "平台学习中心",
            "description": "全面的交易教育资源库",
            "link": "/wiki/learning-center"
        },
        {
            "title": "保证金追加指南",
            "description": "了解保证金追加机制和风险",
            "link": "/wiki/margin-call/"
        }
    ])
}

# ===== GammaTrader 平台详情数据 =====
GAMMA_TRADER_DETAILS = {
    "platform_type": "新手友好",
    "platform_badges": ["新手友好", "教育优先", "低成本"],
    
    "why_choose": json.dumps([
        {
            "icon": "📚",
            "title": "教育优先",
            "description": "40+ 小时的教育课程、实时交易研讨会、新手指南和最佳实践。"
        },
        {
            "icon": "🛡️",
            "title": "安全优先",
            "description": "低杠杆限制、强制风险设置、保证金监控和明确的风险警告。"
        },
        {
            "icon": "💰",
            "title": "低成本起步",
            "description": "仅需 $500 起开户，0.08% 交易费，免提现费。"
        },
        {
            "icon": "🎯",
            "title": "简化界面",
            "description": "直观的交易面板、一键风险设置、新手模式和实时学习提示。"
        }
    ]),
    
    "trading_conditions": json.dumps([
        {"label": "最大杠杆", "value": "1:75 (可调整)"},
        {"label": "最低入金", "value": "$500"},
        {"label": "最小交易量", "value": "0.1手"},
        {"label": "交易时间", "value": "24/5"}
    ]),
    
    "fee_advantages": json.dumps([
        {"label": "交易手续费", "value": "0.08%"},
        {"label": "借款利息", "value": "年 2-3%"},
        {"label": "取款费", "value": "免费"},
        {"label": "账户维护费", "value": "$0"}
    ]),
    
    "account_types": json.dumps([
        {
            "name": "初学者账户",
            "suitable_for": "新手和保守投资者",
            "leverage": "1:10 - 1:30",
            "min_deposit": "$500",
            "commission": "0.08%",
            "features": [
                "杠杆比例：1:10 - 1:30",
                "最低入金：$500",
                "交易手续费：0.08%",
                "新手指导",
                "实时学习提示",
                "模拟账户免费试用"
            ],
            "cta_text": "免费开始",
            "cta_link": "/guides/beginner-start"
        },
        {
            "name": "进阶账户",
            "suitable_for": "有经验的初级交易者",
            "leverage": "1:30 - 1:75",
            "min_deposit": "$2,000",
            "commission": "0.06%",
            "features": [
                "杠杆比例：1:30 - 1:75",
                "最低入金：$2,000",
                "交易手续费：0.06%",
                "高级分析工具",
                "优先客户支持"
            ],
            "cta_text": "升级账户",
            "cta_link": "/guides/upgrade"
        }
    ]),
    
    "trading_tools": json.dumps([
        {
            "title": "简化交易面板",
            "description": "直观的界面设计，一键执行交易，适合初学者。"
        },
        {
            "title": "风险管理工具",
            "description": "自动风险设置、保证金监控、清晰的风险警告。"
        },
        {
            "title": "教育集成",
            "description": "交易时实时学习提示、内置教程、视频指南。"
        },
        {
            "title": "模拟交易",
            "description": "免费模拟账户，无风险练习交易。"
        }
    ]),
    
    "opening_steps": json.dumps([
        {
            "step_number": 1,
            "title": "创建账户",
            "description": "只需填写基本信息，1分钟即可完成。",
            "icon_color": "primary"
        },
        {
            "step_number": 2,
            "title": "学习基础",
            "description": "完成新手教程，了解交易基础知识。",
            "icon_color": "info"
        },
        {
            "step_number": 3,
            "title": "开始交易",
            "description": "仅需$500起即可开始真实交易。",
            "icon_color": "success"
        }
    ]),
    
    "security_measures": json.dumps([
        {"text": "✓ 初学者友好的风险控制"},
        {"text": "✓ 强制止损设置"},
        {"text": "✓ 加密数据传输"},
        {"text": "✓ 完整的教育资源支持"},
        {"text": "✓ 资金安全保障"}
    ]),
    
    "customer_support": json.dumps([
        {"type": "24/5 客户支持", "description": "专业团队随时准备帮助初学者。"},
        {"type": "新手热线", "description": "新手专线电话支持，快速解答问题。"},
        {"type": "在线社区", "description": "与其他交易者交流经验和策略。"}
    ]),
    
    "learning_resources": json.dumps([
        {
            "title": "新手完整指南",
            "description": "从零开始，逐步掌握杠杆交易",
            "link": "/guides/complete-beginner"
        },
        {
            "title": "交易策略课程",
            "description": "40+ 小时教育课程",
            "link": "/guides/strategy-course"
        },
        {
            "title": "实时交易研讨会",
            "description": "每周直播研讨会和专家分析",
            "link": "/workshops"
        }
    ])
}

# 数据映射
PLATFORM_DETAILS_MAP = {
    "alphaleverage": (7, ALPHA_LEVERAGE_DETAILS),
    "betamargin": (8, BETA_MARGIN_DETAILS),
    "gammatrader": (3, GAMMA_TRADER_DETAILS),
}

if __name__ == "__main__":
    # 打印示例数据
    print("="*70)
    print("平台详情数据模板示例")
    print("="*70)
    
    for slug, (pid, details) in PLATFORM_DETAILS_MAP.items():
        print(f"\n平台: {slug} (ID: {pid})")
        print(f"  类型: {details.get('platform_type')}")
        print(f"  徽章: {details.get('platform_badges')}")
        print(f"  账户类型数: {len(json.loads(details['account_types']))}")
        print(f"  开户步骤: {len(json.loads(details['opening_steps']))}")
