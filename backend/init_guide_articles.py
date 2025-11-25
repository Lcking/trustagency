#!/usr/bin/env python3
"""
初始化指南文章到数据库
将guides页面涉及的内容导入到数据库中
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal, engine
from app.models.article import Article
from app.models.section import Section
from app.models.category import Category
from slugify import slugify

def get_or_create_category(db, section_id: int, name: str, description: str = None):
    """获取或创建分类"""
    category = db.query(Category).filter(
        Category.section_id == section_id,
        Category.name == name
    ).first()
    
    if not category:
        category = Category(
            name=name,
            description=description or name,
            section_id=section_id,
            is_active=True
        )
        db.add(category)
        db.commit()
        db.refresh(category)
        print(f"  ✅ 创建分类: {name}")
    
    return category

def create_article(db, title: str, content: str, summary: str, section_id: int, category_id: int, slug: str = None):
    """创建文章（如果不存在）"""
    if not slug:
        slug = slugify(title, allow_unicode=True)
    
    # 检查是否已存在
    existing = db.query(Article).filter(Article.slug == slug).first()
    if existing:
        print(f"  ⏭️  文章已存在: {title}")
        return existing
    
    article = Article(
        title=title,
        slug=slug,
        content=content,
        summary=summary,
        section_id=section_id,
        category_id=category_id,
        is_published=True,
        is_featured=True,
        author_id=1,
        seo_title=title,
        meta_description=summary,
        meta_keywords=f"指南,教程,{title}"
    )
    db.add(article)
    db.commit()
    db.refresh(article)
    print(f"  ✅ 创建文章: {title}")
    return article

def init_guide_articles():
    """初始化指南文章"""
    db = SessionLocal()
    
    try:
        # 获取指南栏目
        guide_section = db.query(Section).filter(Section.slug == "guide").first()
        if not guide_section:
            print("❌ 未找到指南栏目")
            return
        
        section_id = guide_section.id
        print(f"📖 指南栏目ID: {section_id}")
        
        # 定义分类和文章
        guide_data = {
            "新手入门": [
                {
                    "title": "杠杆交易快速入门指南",
                    "slug": "quick-start",
                    "summary": "5分钟快速了解杠杆交易的基础知识和入门步骤",
                    "content": """<h2>杠杆交易快速入门指南</h2>
<p>欢迎来到杠杆交易的世界！本指南将帮助您在5分钟内了解杠杆交易的基础知识。</p>

<h3>第一步：了解杠杆</h3>
<p>杠杆是一种允许您用较少资金控制较大交易规模的工具。例如，10倍杠杆意味着您只需1000元就能进行10000元的交易。</p>

<h3>第二步：认识风险</h3>
<p>杠杆会放大收益，同时也会放大损失。这意味着：</p>
<ul>
<li>价格上涨10%，您的收益可能是100%（10倍杠杆）</li>
<li>价格下跌10%，您的损失也可能是100%</li>
</ul>
<p><strong>重要：</strong>永远不要投入您承受不起损失的资金！</p>

<h3>第三步：选择平台</h3>
<p>选择一个安全、可靠、费用合理的交易平台。关键考虑因素：</p>
<ul>
<li>监管合规性</li>
<li>费用结构</li>
<li>杠杆选项</li>
<li>用户评价</li>
</ul>

<h3>第四步：开设账户</h3>
<ol>
<li>在选定平台注册</li>
<li>完成身份验证（KYC）</li>
<li>充值入金</li>
<li>熟悉平台操作</li>
</ol>

<h3>第五步：开始交易</h3>
<p>建议从小额开始，使用模拟账户练习，逐步积累经验后再增加投入。</p>

<div class="alert alert-warning">
<strong>新手建议：</strong>从低杠杆（2-3倍）开始，随着经验增加再考虑提高杠杆比例。
</div>"""
                },
                {
                    "title": "初学者常见问题解答",
                    "slug": "beginner-faq",
                    "summary": "解答新手交易者最常遇到的问题和困惑",
                    "content": """<h2>初学者常见问题解答</h2>

<h3>Q1: 杠杆交易适合新手吗？</h3>
<p>杠杆交易风险较高，新手应该先充分学习基础知识，使用模拟账户练习，从低杠杆开始。</p>

<h3>Q2: 最少需要多少资金开始？</h3>
<p>不同平台要求不同，通常最低入金在100-1000元之间。建议从最低要求开始，不要投入过多。</p>

<h3>Q3: 什么是保证金？</h3>
<p>保证金是您需要存入的最低资金，用于开设和维持杠杆头寸。当账户余额低于维持保证金时，可能触发强制平仓。</p>

<h3>Q4: 如何选择杠杆比例？</h3>
<p>新手建议从2-5倍开始。杠杆越高，风险越大。随着经验增加，可以逐步调整。</p>

<h3>Q5: 什么是止损？</h3>
<p>止损是一种自动卖出指令，当价格跌到设定水平时执行，用于限制损失。每次交易都应该设置止损。</p>

<h3>Q6: 模拟账户有什么用？</h3>
<p>模拟账户使用虚拟资金，让您在零风险环境下学习和练习交易技巧。强烈建议新手先在模拟账户上练习。</p>

<h3>Q7: 如何避免爆仓？</h3>
<ul>
<li>使用较低杠杆</li>
<li>设置止损</li>
<li>不要满仓操作</li>
<li>定期监控账户</li>
</ul>"""
                }
            ],
            "账户管理": [
                {
                    "title": "账户开设完整指南",
                    "slug": "open-account",
                    "summary": "分步骤详解如何在交易平台开设账户",
                    "content": """<h2>账户开设完整指南</h2>

<h3>第1步：选择合适的平台</h3>
<p>在开户前，请确保您已经充分比较了各个平台：</p>
<ul>
<li><strong>杠杆比例</strong>：选择适合您风险承受能力的最大杠杆</li>
<li><strong>费用结构</strong>：比较交易手续费、借款利息和其他费用</li>
<li><strong>最低入金</strong>：确保金额在您的预算范围内</li>
<li><strong>教育资源</strong>：特别是对初学者来说很重要</li>
<li><strong>安全性</strong>：检查监管状态和安全措施</li>
</ul>

<h3>第2步：注册账户</h3>
<ol>
<li>访问平台官方网站</li>
<li>点击"注册"或"开设账户"按钮</li>
<li>填写基本信息（姓名、邮箱、电话）</li>
<li>创建强密码（大小写字母、数字、符号混合）</li>
<li>同意条款和条件</li>
<li>点击确认邮件中的验证链接</li>
</ol>

<h3>第3步：身份验证（KYC）</h3>
<p><strong>所需文件：</strong></p>
<ul>
<li>有效身份证明（护照或身份证）</li>
<li>地址证明（水电费账单或银行对账单）</li>
<li>工作或财务来源证明（某些平台要求）</li>
</ul>
<p>验证通常需要1-3个工作日。</p>

<h3>第4步：充值入金</h3>
<p><strong>常见充值方式：</strong></p>
<ul>
<li>银行转账：安全但较慢（1-3天）</li>
<li>信用卡/借记卡：快速但可能有费用</li>
<li>电子钱包：部分平台支持</li>
</ul>

<h3>第5步：设置并开始</h3>
<ol>
<li>登录账户</li>
<li>启用两步验证(2FA)</li>
<li>完成个人资料</li>
<li>熟悉交易界面</li>
<li>设置风险参数</li>
</ol>"""
                },
                {
                    "title": "首次入金完整指南",
                    "slug": "first-deposit",
                    "summary": "详解首次充值入金的流程、方式和注意事项",
                    "content": """<h2>首次入金完整指南</h2>

<h3>入金前的准备</h3>
<ul>
<li>确认账户已通过身份验证</li>
<li>了解平台支持的入金方式</li>
<li>确定您愿意投入的金额</li>
<li>准备好支付方式（银行卡、电子钱包等）</li>
</ul>

<h3>常见入金方式</h3>

<h4>1. 银行转账</h4>
<ul>
<li><strong>优点</strong>：安全、通常无手续费</li>
<li><strong>缺点</strong>：到账较慢（1-3个工作日）</li>
<li><strong>适合</strong>：大额入金</li>
</ul>

<h4>2. 信用卡/借记卡</h4>
<ul>
<li><strong>优点</strong>：即时到账</li>
<li><strong>缺点</strong>：可能收取1-3%手续费</li>
<li><strong>适合</strong>：小额快速入金</li>
</ul>

<h4>3. 电子钱包</h4>
<ul>
<li><strong>优点</strong>：快速、方便</li>
<li><strong>缺点</strong>：不是所有平台都支持</li>
<li><strong>常见</strong>：PayPal、Skrill、支付宝等</li>
</ul>

<h3>入金步骤</h3>
<ol>
<li>登录您的交易账户</li>
<li>进入"入金"或"充值"页面</li>
<li>选择入金方式</li>
<li>输入入金金额</li>
<li>确认交易详情</li>
<li>完成支付</li>
<li>等待资金到账</li>
</ol>

<h3>重要提醒</h3>
<div class="alert alert-warning">
<ul>
<li>从小额开始，不要一次投入过多</li>
<li>只使用您承受得起损失的资金</li>
<li>在真实交易前先使用模拟账户练习</li>
<li>注意入金手续费和汇率</li>
</ul>
</div>"""
                },
                {
                    "title": "提现流程详解",
                    "slug": "withdrawal-guide",
                    "summary": "了解如何安全、快速地从交易账户提取资金",
                    "content": """<h2>提现流程详解</h2>

<h3>提现前须知</h3>
<ul>
<li>确认账户已完成身份验证</li>
<li>了解平台的最低提现金额</li>
<li>检查是否有未结算的交易</li>
<li>注意提现手续费</li>
</ul>

<h3>提现步骤</h3>
<ol>
<li><strong>登录账户</strong>：进入您的交易账户</li>
<li><strong>进入提现页面</strong>：通常在"资金管理"或"钱包"中</li>
<li><strong>选择提现方式</strong>：银行转账、电子钱包等</li>
<li><strong>输入提现金额</strong>：确保不低于最低要求</li>
<li><strong>填写收款信息</strong>：银行账户或钱包地址</li>
<li><strong>确认并提交</strong>：仔细核对所有信息</li>
<li><strong>等待处理</strong>：通常1-5个工作日</li>
</ol>

<h3>提现方式对比</h3>
<table>
<tr><th>方式</th><th>到账时间</th><th>手续费</th></tr>
<tr><td>银行转账</td><td>1-5工作日</td><td>通常免费或较低</td></tr>
<tr><td>电子钱包</td><td>即时-24小时</td><td>可能有手续费</td></tr>
<tr><td>信用卡</td><td>3-5工作日</td><td>可能有手续费</td></tr>
</table>

<h3>常见问题</h3>
<p><strong>Q: 为什么提现被延迟？</strong></p>
<p>可能原因：身份验证未完成、账户有异常、银行处理延迟等。</p>

<p><strong>Q: 提现有限额吗？</strong></p>
<p>大多数平台有每日/每周提现限额，具体请查看平台规定。</p>"""
                },
                {
                    "title": "查看账户余额和交易记录",
                    "slug": "account-balance",
                    "summary": "学习如何查看账户余额、持仓和历史交易记录",
                    "content": """<h2>查看账户余额和交易记录</h2>

<h3>账户概览</h3>
<p>登录后，您通常可以在主页面看到以下关键信息：</p>
<ul>
<li><strong>总资产</strong>：您账户的总价值</li>
<li><strong>可用余额</strong>：可以用于新交易的资金</li>
<li><strong>已用保证金</strong>：当前持仓占用的保证金</li>
<li><strong>浮动盈亏</strong>：未平仓头寸的当前盈亏</li>
</ul>

<h3>查看持仓</h3>
<p>在"持仓"或"头寸"页面，您可以看到：</p>
<ul>
<li>当前持有的所有头寸</li>
<li>每个头寸的买入价格</li>
<li>当前市场价格</li>
<li>未实现盈亏</li>
<li>使用的杠杆比例</li>
</ul>

<h3>交易历史</h3>
<p>在"历史"或"交易记录"页面，您可以查看：</p>
<ul>
<li>已完成的所有交易</li>
<li>交易日期和时间</li>
<li>买入/卖出价格</li>
<li>实现盈亏</li>
<li>手续费详情</li>
</ul>

<h3>报表导出</h3>
<p>大多数平台支持导出交易记录，用于：</p>
<ul>
<li>个人记账</li>
<li>税务申报</li>
<li>交易分析</li>
</ul>"""
                }
            ],
            "风险管理": [
                {
                    "title": "风险管理完全指南",
                    "slug": "risk-management",
                    "summary": "全面了解杠杆交易中的风险管理策略和技巧",
                    "content": """<h2>风险管理完全指南</h2>

<div class="alert alert-danger">
<strong>最重要的规则：</strong>永远不要使用您承受不起失去的资金进行交易！
</div>

<h3>风险管理的五大支柱</h3>

<h4>1. 设置止损</h4>
<p>止损是限制损失的最重要工具。每次交易都必须设置止损。</p>
<ul>
<li>根据技术分析确定止损位置</li>
<li>不要设置得太紧（容易被震出）</li>
<li>不要设置得太宽（损失过大）</li>
</ul>

<h4>2. 控制杠杆</h4>
<p>杠杆越高，风险越大。建议：</p>
<ul>
<li>新手：2-5倍杠杆</li>
<li>有经验：5-10倍杠杆</li>
<li>专业交易者：10倍以上</li>
</ul>

<h4>3. 仓位管理</h4>
<p>计算合适的仓位大小：</p>
<ul>
<li>单笔交易风险不超过总资金的1-2%</li>
<li>总风险敞口不超过总资金的10-20%</li>
</ul>

<h4>4. 多元化</h4>
<p>不要把所有资金投入单一交易或资产。分散投资可以降低整体风险。</p>

<h4>5. 监控保证金</h4>
<p>定期检查保证金水平，确保账户有足够缓冲，避免被强制平仓。</p>

<h3>风险管理清单</h3>
<ul>
<li>☐ 每次交易前确定止损位</li>
<li>☐ 计算好仓位大小</li>
<li>☐ 确认风险收益比至少2:1</li>
<li>☐ 检查账户保证金水平</li>
<li>☐ 不要情绪化交易</li>
</ul>"""
                },
                {
                    "title": "止损设置方法详解",
                    "slug": "stop-loss-guide",
                    "summary": "学习如何正确设置止损来保护您的投资",
                    "content": """<h2>止损设置方法详解</h2>

<h3>什么是止损？</h3>
<p>止损是一种预设的卖出指令，当价格跌到设定水平时自动执行，用于限制亏损。</p>

<h3>止损类型</h3>

<h4>1. 固定止损</h4>
<p>在固定价格水平设置止损。</p>
<p><strong>例如</strong>：以100元买入，设置止损在95元（5%亏损）。</p>

<h4>2. 追踪止损</h4>
<p>止损价格随市场价格上涨而自动上移。</p>
<p><strong>例如</strong>：设置5%追踪止损，价格从100涨到120时，止损自动上移到114。</p>

<h4>3. 技术止损</h4>
<p>基于技术分析设置止损，如支撑位下方。</p>

<h3>设置止损的原则</h3>
<ol>
<li><strong>在入场前确定</strong>：先想好止损位再开仓</li>
<li><strong>给予适当空间</strong>：避免被正常波动触发</li>
<li><strong>考虑风险收益比</strong>：止损金额应小于潜在收益</li>
<li><strong>不要随意移动</strong>：除非是向有利方向移动</li>
</ol>

<h3>常见错误</h3>
<ul>
<li>❌ 不设止损</li>
<li>❌ 止损设置太紧</li>
<li>❌ 亏损时取消止损</li>
<li>❌ 情绪化调整止损</li>
</ul>

<h3>止损计算示例</h3>
<p>账户资金：10000元<br>
愿意承担风险：1%（100元）<br>
买入价格：50元<br>
止损距离：2元<br>
<strong>仓位大小 = 100 / 2 = 50股</strong></p>"""
                }
            ],
            "交易策略": [
                {
                    "title": "日内交易策略指南",
                    "slug": "day-trading",
                    "summary": "学习日内交易的技巧、策略和风险管理",
                    "content": """<h2>日内交易策略指南</h2>

<h3>什么是日内交易？</h3>
<p>日内交易是指在同一交易日内完成买入和卖出，不持仓过夜。目标是利用日内价格波动获利。</p>

<h3>日内交易的特点</h3>
<ul>
<li>高频率：每天多次交易</li>
<li>短周期：持仓时间从几分钟到几小时</li>
<li>高风险/高收益：快速获利或亏损</li>
<li>需要全程关注：必须监控市场</li>
</ul>

<h3>日内交易策略</h3>

<h4>1. 突破交易</h4>
<p>当价格突破重要支撑或阻力位时入场。</p>

<h4>2. 回调交易</h4>
<p>在趋势中等待回调，在回调结束时入场。</p>

<h4>3. 区间交易</h4>
<p>在价格区间内低买高卖。</p>

<h3>日内交易技巧</h3>
<ul>
<li>选择流动性高的品种</li>
<li>关注开盘和收盘时段</li>
<li>严格执行止损</li>
<li>控制交易次数</li>
<li>保持冷静，不要追涨杀跌</li>
</ul>

<h3>日内交易不适合谁？</h3>
<ul>
<li>没有足够时间监控市场</li>
<li>无法承受高压力</li>
<li>资金量较小</li>
<li>新手交易者</li>
</ul>"""
                },
                {
                    "title": "摇摆交易策略指南",
                    "slug": "swing-trading",
                    "summary": "学习摇摆交易的方法，捕捉中期趋势",
                    "content": """<h2>摇摆交易策略指南</h2>

<h3>什么是摇摆交易？</h3>
<p>摇摆交易是一种中期交易策略，持仓时间从几天到几周，目标是捕捉价格的"摇摆"波动。</p>

<h3>摇摆交易的优势</h3>
<ul>
<li>不需要全天监控市场</li>
<li>交易频率适中</li>
<li>有时间分析和决策</li>
<li>适合上班族</li>
<li>交易成本相对较低</li>
</ul>

<h3>摇摆交易策略</h3>

<h4>1. 趋势跟踪</h4>
<p>识别中期趋势，顺势交易。上升趋势中做多，下降趋势中做空。</p>

<h4>2. 支撑阻力交易</h4>
<p>在支撑位买入，在阻力位卖出。</p>

<h4>3. 均线交叉</h4>
<p>使用移动平均线（如5日和20日均线）的交叉作为买卖信号。</p>

<h3>摇摆交易技巧</h3>
<ol>
<li>使用日线图和4小时图分析</li>
<li>关注成交量确认</li>
<li>设置合理的止损和获利目标</li>
<li>耐心等待最佳入场点</li>
<li>不要被短期波动影响</li>
</ol>

<h3>推荐给新手的理由</h3>
<p>摇摆交易平衡了交易频率和风险，给予足够的时间思考和分析，是新手的理想起点。</p>"""
                },
                {
                    "title": "趋势交易策略指南",
                    "slug": "trend-trading",
                    "summary": "学习如何识别和跟随长期趋势进行交易",
                    "content": """<h2>趋势交易策略指南</h2>

<h3>什么是趋势交易？</h3>
<p>趋势交易是跟随市场的长期方向进行交易，持仓时间可能从数周到数月。</p>

<h3>趋势的类型</h3>
<ul>
<li><strong>上升趋势</strong>：高点和低点不断抬高</li>
<li><strong>下降趋势</strong>：高点和低点不断降低</li>
<li><strong>横盘整理</strong>：价格在区间内波动</li>
</ul>

<h3>识别趋势的方法</h3>

<h4>1. 趋势线</h4>
<p>连接两个或更多的低点（上升趋势）或高点（下降趋势）。</p>

<h4>2. 移动平均线</h4>
<p>价格在均线上方为上升趋势，下方为下降趋势。</p>

<h4>3. 技术指标</h4>
<p>ADX（平均趋向指数）可以判断趋势强度。</p>

<h3>趋势交易规则</h3>
<ol>
<li><strong>顺势而为</strong>：只在趋势方向交易</li>
<li><strong>等待回调</strong>：在回调时入场，而非追高</li>
<li><strong>让利润奔跑</strong>：不要过早平仓</li>
<li><strong>严格止损</strong>：趋势反转时及时离场</li>
</ol>

<h3>趋势交易的优缺点</h3>
<p><strong>优点</strong>：</p>
<ul>
<li>潜在利润大</li>
<li>交易频率低</li>
<li>不需要频繁盯盘</li>
</ul>
<p><strong>缺点</strong>：</p>
<ul>
<li>需要耐心</li>
<li>可能错过短期机会</li>
<li>趋势反转时可能回吐利润</li>
</ul>"""
                },
                {
                    "title": "高级交易技巧",
                    "slug": "advanced-trading",
                    "summary": "进阶交易技巧和策略，适合有经验的交易者",
                    "content": """<h2>高级交易技巧</h2>

<h3>1. 金字塔加仓</h3>
<p>当交易方向正确时，分批加仓以扩大利润。</p>
<ul>
<li>只在盈利时加仓</li>
<li>每次加仓量递减</li>
<li>调整止损保护利润</li>
</ul>

<h3>2. 对冲策略</h3>
<p>同时持有相反方向的头寸来降低风险。</p>
<ul>
<li>跨品种对冲</li>
<li>跨市场对冲</li>
<li>期权保护</li>
</ul>

<h3>3. 多时间框架分析</h3>
<p>结合不同时间周期的图表进行分析：</p>
<ul>
<li>长周期确定趋势方向</li>
<li>中周期寻找交易机会</li>
<li>短周期精确入场点</li>
</ul>

<h3>4. 量价分析</h3>
<p>结合成交量分析价格走势：</p>
<ul>
<li>放量突破更可靠</li>
<li>缩量回调是健康调整</li>
<li>量价背离可能预示反转</li>
</ul>

<h3>5. 情绪管理</h3>
<p>控制交易情绪是成功的关键：</p>
<ul>
<li>制定交易计划并严格执行</li>
<li>不要报复性交易</li>
<li>接受亏损是交易的一部分</li>
<li>保持交易日志</li>
</ul>

<h3>6. 风险收益优化</h3>
<p>追求最优的风险收益比：</p>
<ul>
<li>寻找至少2:1的风险收益比</li>
<li>提高胜率或提高盈亏比</li>
<li>定期复盘优化策略</li>
</ul>"""
                }
            ],
            "平台操作": [
                {
                    "title": "平台界面导航指南",
                    "slug": "platform-navigation",
                    "summary": "熟悉交易平台的主要功能和界面布局",
                    "content": """<h2>平台界面导航指南</h2>

<h3>主要界面区域</h3>

<h4>1. 行情区</h4>
<p>显示实时价格、涨跌幅、成交量等市场数据。</p>

<h4>2. 图表区</h4>
<p>K线图、技术指标、画线工具等。</p>

<h4>3. 交易区</h4>
<p>下单界面，包括买入/卖出、数量、价格、杠杆等设置。</p>

<h4>4. 持仓区</h4>
<p>显示当前持有的头寸、盈亏、保证金等。</p>

<h4>5. 账户区</h4>
<p>账户余额、可用资金、历史记录等。</p>

<h3>常用功能</h3>
<ul>
<li><strong>市价单</strong>：以当前市场价格立即成交</li>
<li><strong>限价单</strong>：设定价格，达到后自动成交</li>
<li><strong>止损单</strong>：设定止损价格</li>
<li><strong>止盈单</strong>：设定获利了结价格</li>
</ul>

<h3>快捷操作</h3>
<ul>
<li>一键平仓</li>
<li>快速调整杠杆</li>
<li>图表周期切换</li>
<li>指标添加/删除</li>
</ul>

<h3>移动端特点</h3>
<p>移动端通常提供简化界面，适合监控和简单操作。复杂分析建议使用电脑端。</p>"""
                },
                {
                    "title": "下单交易操作教程",
                    "slug": "order-tutorial",
                    "summary": "详解如何在交易平台上进行买入和卖出操作",
                    "content": """<h2>下单交易操作教程</h2>

<h3>下单前的准备</h3>
<ol>
<li>分析市场，确定交易方向</li>
<li>计算仓位大小</li>
<li>确定入场价格</li>
<li>设置止损和止盈价格</li>
</ol>

<h3>下单步骤</h3>

<h4>步骤1：选择交易品种</h4>
<p>在行情列表中找到您要交易的品种。</p>

<h4>步骤2：打开交易面板</h4>
<p>点击"买入"或"卖出"按钮。</p>

<h4>步骤3：设置交易参数</h4>
<ul>
<li><strong>方向</strong>：买入（做多）或卖出（做空）</li>
<li><strong>数量</strong>：交易的数量或金额</li>
<li><strong>杠杆</strong>：选择杠杆倍数</li>
<li><strong>订单类型</strong>：市价单或限价单</li>
</ul>

<h4>步骤4：设置止损止盈</h4>
<ul>
<li>止损价格：亏损时自动平仓</li>
<li>止盈价格：盈利时自动平仓</li>
</ul>

<h4>步骤5：确认并提交</h4>
<p>检查所有参数无误后，点击确认提交订单。</p>

<h3>订单类型说明</h3>
<table>
<tr><th>类型</th><th>特点</th><th>适用场景</th></tr>
<tr><td>市价单</td><td>立即成交</td><td>急需入场</td></tr>
<tr><td>限价单</td><td>指定价格</td><td>等待更好价格</td></tr>
<tr><td>止损单</td><td>触发执行</td><td>风险控制</td></tr>
</table>"""
                },
                {
                    "title": "移动端使用指南",
                    "slug": "mobile-guide",
                    "summary": "学习如何在手机上高效使用交易平台",
                    "content": """<h2>移动端使用指南</h2>

<h3>移动端的优势</h3>
<ul>
<li>随时随地监控市场</li>
<li>及时收到价格提醒</li>
<li>快速执行紧急操作</li>
<li>方便的推送通知</li>
</ul>

<h3>移动端的局限</h3>
<ul>
<li>屏幕较小，图表分析不便</li>
<li>复杂操作不如电脑方便</li>
<li>网络依赖性高</li>
</ul>

<h3>推荐使用场景</h3>
<ul>
<li>监控持仓和盈亏</li>
<li>接收价格提醒</li>
<li>紧急平仓或调整止损</li>
<li>查看账户状态</li>
</ul>

<h3>移动端安全建议</h3>
<ol>
<li>启用生物识别登录（指纹/面部）</li>
<li>开启两步验证</li>
<li>不要在公共WiFi下交易</li>
<li>定期更新APP版本</li>
<li>设置登录通知</li>
</ol>

<h3>推荐设置</h3>
<ul>
<li>开启价格提醒</li>
<li>设置保证金警告通知</li>
<li>启用交易确认提醒</li>
<li>配置快捷操作按钮</li>
</ul>"""
                }
            ]
        }
        
        # 创建文章
        created_count = 0
        for category_name, articles in guide_data.items():
            print(f"\n📁 处理分类: {category_name}")
            
            # 获取或创建分类
            category = get_or_create_category(db, section_id, category_name)
            
            # 创建文章
            for article_data in articles:
                article = create_article(
                    db,
                    title=article_data["title"],
                    content=article_data["content"],
                    summary=article_data["summary"],
                    section_id=section_id,
                    category_id=category.id,
                    slug=article_data.get("slug")
                )
                if article:
                    created_count += 1
        
        print(f"\n✅ 完成！共处理 {created_count} 篇指南文章")
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("🚀 开始初始化指南文章...")
    init_guide_articles()

