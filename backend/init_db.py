#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
简单初始化脚本 - 只添加缺失的列，避免触发 init_db() 的查询问题
"""
import sqlite3
import json
from datetime import datetime

DB_PATH = '/Users/ck/Desktop/Project/trustagency/backend/trustagency.db'

def main():
    """直接使用 sqlite3 添加列和更新数据"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        print("检查并添加缺失的列...\n")
        
        # 要添加的列
        columns_to_add = [
            'why_choose',
            'account_types', 
            'fee_table',
            'trading_tools',
            'opening_steps',
            'safety_info',
            'learning_resources',
            'overview_intro',
            'top_badges',
            'trading_conditions',
            'fee_advantages',
            'security_measures',
            'customer_support',
            'platform_badges'
        ]
        
        # 获取现有列
        cursor.execute("PRAGMA table_info(platforms)")
        existing_cols = {row[1] for row in cursor.fetchall()}
        print(f"数据库现有 {len(existing_cols)} 列")
        
        # 添加缺失的列
        for col in columns_to_add:
            if col not in existing_cols:
                try:
                    cursor.execute(f"ALTER TABLE platforms ADD COLUMN {col} TEXT")
                    print(f"  ✓ 添加列: {col}")
                except sqlite3.OperationalError as e:
                    if "already exists" in str(e):
                        print(f"  ℹ {col} 已存在")
                    else:
                        raise
            else:
                print(f"  ✓ {col} 已存在")
        
        conn.commit()
        print("\n✓ 所有列已准备就绪\n")
        
        # 更新平台数据
        print("初始化平台数据...\n")
        
        platforms_data = {
            'alphaleverage': {
                'overview_intro': 'AlphaLeverage 是一个专为专业交易者设计的高杠杆交易平台',
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
                'top_badges': json.dumps(['推荐平台', '专业级交易', '最高杠杆'], ensure_ascii=False),
                'trading_conditions': json.dumps([
                    {'label': '最大杠杆', 'value': '1:500'},
                    {'label': '最低入金', 'value': '$5,000'},
                    {'label': '最小交易量', 'value': '0.01手'},
                    {'label': '交易品种', 'value': '外汇、贵金属、原油、加密'}
                ], ensure_ascii=False),
                'fee_advantages': json.dumps([
                    {'item': '交易手续费', 'value': '从0.10%起'},
                    {'item': '借款利息', 'value': '年利率4-8%'},
                    {'item': '入金优惠', 'value': '新客户入金100%返还'},
                    {'item': '月度返现', 'value': '活跃交易者可获得返现'}
                ], ensure_ascii=False),
                'security_measures': json.dumps([
                    '资金隔离存管（全额保护）',
                    '银行级SSL加密传输',
                    '二次验证登录保护',
                    '24小时风险监控',
                    '合规监管认证'
                ], ensure_ascii=False),
                'customer_support': json.dumps([
                    {'channel': '在线客服', 'hours': '24/7'},
                    {'channel': '电子邮件', 'hours': '24小时回复'},
                    {'channel': '电话支持', 'hours': '工作日9-18点'},
                    {'channel': '社区论坛', 'hours': '实时交流'}
                ], ensure_ascii=False),
                'platform_badges': json.dumps(['推荐平台', '专业级交易', '最高杠杆'], ensure_ascii=False)
            },
            'betamargin': {
                'overview_intro': 'BetaMargin 是一个平衡专业性和易用性的交易平台',
                'why_choose': json.dumps([
                    {'icon': '🏢', 'title': '可靠的基础设施', 'description': '99.99%正常运行时间'},
                    {'icon': '⚖️', 'title': '公平的费率结构', 'description': '透明的费用体系，没有隐藏费用'},
                    {'icon': '🛡️', 'title': '风险管理工具', 'description': '内置风险管理工具帮助控制交易风险'},
                    {'icon': '📱', 'title': '跨平台支持', 'description': '桌面、网页、移动三平台无缝同步'}
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
                    {'title': '高级图表分析', 'description': 'TradingView集成，100+指标支持'},
                    {'title': '风险管理工具', 'description': '动态止损、追踪止盈等'},
                    {'title': '实时推送', 'description': '价格、新闻、经济日历实时通知'},
                    {'title': '移动应用', 'description': 'iOS和Android应用程序'}
                ], ensure_ascii=False),
                'top_badges': json.dumps(['成熟稳定', '平衡型平台', '新手友好'], ensure_ascii=False),
                'trading_conditions': json.dumps([
                    {'label': '最大杠杆', 'value': '1:50'},
                    {'label': '最低入金', 'value': '$2,000'},
                    {'label': '最小交易量', 'value': '0.01手'},
                    {'label': '交易品种', 'value': '外汇、指数、商品、加密'}
                ], ensure_ascii=False),
                'fee_advantages': json.dumps([
                    {'item': '交易手续费', 'value': '从0.12%起'},
                    {'item': '借款利息', 'value': '年利率4-7%'},
                    {'item': '推荐奖励', 'value': '最高50%分利'},
                    {'item': '稳定的点差', 'value': '无滑点保证'}
                ], ensure_ascii=False),
                'security_measures': json.dumps([
                    '投资者保护基金覆盖',
                    'ISO 27001信息安全认证',
                    '分离账户管理',
                    '实时交易监控',
                    '定期独立审计'
                ], ensure_ascii=False),
                'customer_support': json.dumps([
                    {'channel': '在线客服', 'hours': '24/7'},
                    {'channel': '电话支持', 'hours': '24/5'},
                    {'channel': '邮件支持', 'hours': '12小时回复'},
                    {'channel': '社区论坛', 'hours': '24/7开放'}
                ], ensure_ascii=False),
                'platform_badges': json.dumps(['成熟稳定', '平衡型平台', '新手友好'], ensure_ascii=False)
            },
            'gammatrader': {
                'overview_intro': 'GammaTrader 是专为初学者设计的教育导向型交易平台',
                'why_choose': json.dumps([
                    {'icon': '📚', 'title': '教育优先', 'description': '提供全面的学习资源，从基础到进阶的完整课程'},
                    {'icon': '🔒', 'title': '安全优先', 'description': '低杠杆设置和风险控制工具，最大化保护新手资金'},
                    {'icon': '💵', 'title': '低成本起步', 'description': '最低入金$500，行业内最低费率0.10%'},
                    {'icon': '☁️', 'title': '简化界面', 'description': '直观易用的交易界面，快速上手'}
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
                    {'title': '教育资源库', 'description': '100+小时视频教程和交易指南'},
                    {'title': '简化交易界面', 'description': '一键下单，自动风险计算'},
                    {'title': '新手保护工具', 'description': '自动止损、风险提示等'},
                    {'title': '社区支持', 'description': '交易者社区，分享经验和策略'}
                ], ensure_ascii=False),
                'top_badges': json.dumps(['新手友好', '教育平台', '低成本'], ensure_ascii=False),
                'trading_conditions': json.dumps([
                    {'label': '最大杠杆', 'value': '1:20'},
                    {'label': '最低入金', 'value': '$500'},
                    {'label': '最小交易量', 'value': '0.01手'},
                    {'label': '交易品种', 'value': '主流外汇和商品'}
                ], ensure_ascii=False),
                'fee_advantages': json.dumps([
                    {'item': '交易手续费', 'value': '最低0.08%'},
                    {'item': '借款利息', 'value': '年利率3-5%'},
                    {'item': '新手奖励', 'value': '$20新手礼金'},
                    {'item': '教育资源', 'value': '终身免费'}
                ], ensure_ascii=False),
                'security_measures': json.dumps([
                    '客户资金100%分离存管',
                    '国际金融监管认证',
                    '冷钱包存储加密资产',
                    '定期风险评估',
                    '透明的运营报告'
                ], ensure_ascii=False),
                'customer_support': json.dumps([
                    {'channel': '实时在线客服', 'hours': '24/7'},
                    {'channel': '教育支持', 'hours': '24/7'},
                    {'channel': '电话热线', 'hours': '工作日8-22点'},
                    {'channel': '社交媒体', 'hours': '实时回复'}
                ], ensure_ascii=False),
                'platform_badges': json.dumps(['新手友好', '教育平台', '低成本'], ensure_ascii=False)
            }
        }
        
        for slug, fields in platforms_data.items():
            # 先查询平台 ID
            cursor.execute("SELECT id, name FROM platforms WHERE slug = ?", (slug,))
            result = cursor.fetchone()
            
            if not result:
                print(f"  ⚠ 平台未找到: {slug}")
                continue
            
            platform_id, platform_name = result
            
            # 更新字段
            update_sql = "UPDATE platforms SET "
            update_vals = []
            field_names = []
            
            for field_name, field_value in fields.items():
                field_names.append(f"{field_name} = ?")
                update_vals.append(field_value)
            
            update_sql += ", ".join(field_names)
            update_sql += f", updated_at = ? WHERE id = ?"
            
            update_vals.append(datetime.utcnow().isoformat())
            update_vals.append(platform_id)
            
            cursor.execute(update_sql, update_vals)
            print(f"  ✓ 更新: {platform_name}")
        
        conn.commit()
        conn.close()
        
        print("\n✅ 初始化完成！")
        print("\n后续步骤:")
        print("1. 启动后端: cd backend && python -m uvicorn app.main:app --reload")
        print("2. 测试 API: curl http://localhost:8001/api/admin/platforms/1/edit")
        return True
        
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    import sys
    success = main()
    sys.exit(0 if success else 1)
