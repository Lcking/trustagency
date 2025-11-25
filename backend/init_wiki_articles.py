#!/usr/bin/env python3
"""
初始化Wiki百科文章到数据库
将wiki页面静态展示的16篇文章导入到数据库中
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
        meta_keywords=f"百科,{title}"
    )
    db.add(article)
    db.commit()
    db.refresh(article)
    print(f"  ✅ 创建文章: {title}")
    return article

def init_wiki_articles():
    """初始化Wiki文章"""
    db = SessionLocal()
    
    try:
        # 获取百科栏目
        wiki_section = db.query(Section).filter(Section.slug == "wiki").first()
        if not wiki_section:
            print("❌ 未找到百科栏目")
            return
        
        section_id = wiki_section.id
        print(f"📚 百科栏目ID: {section_id}")
        
        # 定义分类和文章
        wiki_data = {
            "基础概念": [
                {
                    "title": "什么是杠杆交易？",
                    "slug": "what-is-leverage",
                    "summary": "了解杠杆交易的基本概念、运作原理和适用场景",
                    "content": """<h2>什么是杠杆交易？</h2>
<p>杠杆交易是一种允许投资者使用借入资金来放大其交易规模的金融操作方式。通过杠杆，投资者可以用较少的自有资金控制更大价值的资产。</p>

<h3>杠杆交易的基本原理</h3>
<p>假设您有1万元本金，使用10倍杠杆，您可以控制价值10万元的资产。如果资产价格上涨10%，您的收益将是1万元（100%回报率），而不是使用自有资金时的1000元（10%回报率）。</p>

<h3>杠杆的双刃剑效应</h3>
<p>杠杆既能放大收益，也能放大亏损。在上述例子中，如果资产价格下跌10%，您将损失全部本金。因此，合理使用杠杆和风险管理至关重要。</p>

<h3>常见杠杆比例</h3>
<ul>
<li><strong>2-5倍</strong>：保守型，适合新手</li>
<li><strong>5-10倍</strong>：中等风险，适合有经验的交易者</li>
<li><strong>10倍以上</strong>：高风险，仅适合专业交易者</li>
</ul>

<h3>总结</h3>
<p>杠杆交易是一把双刃剑，正确使用可以提高资金效率，但也伴随着更高的风险。建议新手从低杠杆开始，逐步积累经验。</p>"""
                },
                {
                    "title": "什么是保证金追加？",
                    "slug": "margin-call",
                    "summary": "理解保证金追加的含义、触发条件和应对策略",
                    "content": """<h2>什么是保证金追加（Margin Call）？</h2>
<p>保证金追加是指当您的账户权益下降到维持保证金水平以下时，券商要求您补充资金的通知。</p>

<h3>保证金追加的触发条件</h3>
<p>当您的账户净值低于维持保证金要求时，就会触发保证金追加。通常，维持保证金是初始保证金的50%-80%。</p>

<h3>收到保证金追加通知后该怎么办？</h3>
<ol>
<li><strong>追加保证金</strong>：向账户存入更多资金</li>
<li><strong>平仓部分头寸</strong>：减少持仓以降低保证金要求</li>
<li><strong>不采取行动</strong>：券商可能会强制平仓您的部分或全部头寸</li>
</ol>

<h3>如何避免保证金追加？</h3>
<ul>
<li>使用较低的杠杆比例</li>
<li>设置止损订单</li>
<li>定期监控账户状况</li>
<li>保持充足的账户余额</li>
</ul>"""
                },
                {
                    "title": "杠杆比例的含义",
                    "slug": "leverage-ratio",
                    "summary": "深入理解杠杆比例的计算方法和实际应用",
                    "content": """<h2>杠杆比例的含义</h2>
<p>杠杆比例表示您可以用多少倍的资金进行交易。例如，10:1的杠杆意味着每1元本金可以控制10元的资产。</p>

<h3>杠杆比例的计算</h3>
<p><strong>公式</strong>：杠杆比例 = 总持仓价值 / 自有资金</p>
<p>例如：您有1000元本金，持有价值5000元的股票，则杠杆比例为5:1。</p>

<h3>不同杠杆比例的风险等级</h3>
<table>
<tr><th>杠杆比例</th><th>风险等级</th><th>适合人群</th></tr>
<tr><td>2:1 - 3:1</td><td>低</td><td>保守投资者、新手</td></tr>
<tr><td>5:1 - 10:1</td><td>中</td><td>有经验的交易者</td></tr>
<tr><td>20:1以上</td><td>高</td><td>专业交易者</td></tr>
</table>

<h3>选择合适杠杆的建议</h3>
<p>选择杠杆时应考虑：您的风险承受能力、交易经验、市场波动性和资金管理策略。</p>"""
                },
                {
                    "title": "做多和做空交易",
                    "slug": "long-short",
                    "summary": "了解做多和做空的区别及实际操作方法",
                    "content": """<h2>做多和做空交易</h2>
<p>做多和做空是两种基本的交易方向，分别适用于看涨和看跌市场。</p>

<h3>什么是做多？</h3>
<p>做多是指买入资产，期望其价格上涨后卖出获利。这是最常见的交易方式。</p>
<p><strong>示例</strong>：以100元买入股票，当价格涨到120元时卖出，获利20元。</p>

<h3>什么是做空？</h3>
<p>做空是指借入资产并立即卖出，期望价格下跌后以更低价格买回归还，从差价中获利。</p>
<p><strong>示例</strong>：借入股票并以100元卖出，当价格跌到80元时买回归还，获利20元。</p>

<h3>做多 vs 做空对比</h3>
<table>
<tr><th>特点</th><th>做多</th><th>做空</th></tr>
<tr><td>盈利条件</td><td>价格上涨</td><td>价格下跌</td></tr>
<tr><td>最大亏损</td><td>投入本金</td><td>理论上无限</td></tr>
<tr><td>复杂度</td><td>简单</td><td>较复杂</td></tr>
</table>"""
                }
            ],
            "风险管理": [
                {
                    "title": "关键风险指标",
                    "slug": "risk-metrics",
                    "summary": "学习如何监测和理解杠杆交易中的关键风险指标",
                    "content": """<h2>关键风险指标</h2>
<p>了解和监控风险指标是成功交易的关键。以下是最重要的风险指标。</p>

<h3>1. 保证金水平</h3>
<p>保证金水平 = (账户净值 / 已用保证金) × 100%</p>
<p>当保证金水平低于100%时，需要警惕保证金追加风险。</p>

<h3>2. 风险敞口</h3>
<p>风险敞口是指您的投资组合面临的潜在损失金额。应始终控制在可承受范围内。</p>

<h3>3. 最大回撤</h3>
<p>最大回撤是指从账户最高点到最低点的最大跌幅，用于衡量交易策略的风险。</p>

<h3>4. 夏普比率</h3>
<p>夏普比率 = (投资组合收益 - 无风险收益) / 投资组合标准差</p>
<p>夏普比率越高，说明风险调整后的收益越好。</p>"""
                },
                {
                    "title": "仓位管理",
                    "slug": "position-sizing",
                    "summary": "如何选择合适的仓位大小来控制风险",
                    "content": """<h2>仓位管理</h2>
<p>仓位管理是风险控制的核心，决定了每次交易投入多少资金。</p>

<h3>仓位管理的基本原则</h3>
<ul>
<li><strong>单笔交易风险</strong>：通常不超过总资金的1-2%</li>
<li><strong>总风险敞口</strong>：所有持仓的总风险不超过总资金的10-20%</li>
<li><strong>分散投资</strong>：不要把所有资金集中在单一交易上</li>
</ul>

<h3>仓位计算公式</h3>
<p><strong>仓位大小 = 风险金额 / 每单位风险</strong></p>
<p>例如：账户10000元，愿意承担1%风险（100元），止损距离为2元，则仓位 = 100/2 = 50股。</p>

<h3>仓位管理策略</h3>
<ol>
<li><strong>固定金额法</strong>：每次交易固定金额</li>
<li><strong>固定比例法</strong>：每次交易固定比例的账户资金</li>
<li><strong>凯利公式</strong>：根据胜率和盈亏比计算最优仓位</li>
</ol>"""
                },
                {
                    "title": "止损和获利订单",
                    "slug": "stop-loss-takeprofit",
                    "summary": "学习如何设置止损和获利订单来保护利润和限制损失",
                    "content": """<h2>止损和获利订单</h2>
<p>止损和获利订单是自动化风险管理的重要工具。</p>

<h3>什么是止损订单？</h3>
<p>止损订单是预设的卖出指令，当价格跌到设定水平时自动执行，用于限制亏损。</p>

<h3>什么是获利订单？</h3>
<p>获利订单是预设的卖出指令，当价格涨到设定水平时自动执行，用于锁定利润。</p>

<h3>设置止损的方法</h3>
<ul>
<li><strong>固定金额止损</strong>：基于愿意承受的最大损失</li>
<li><strong>技术止损</strong>：基于支撑位、移动平均线等技术指标</li>
<li><strong>百分比止损</strong>：基于入场价格的固定百分比</li>
<li><strong>追踪止损</strong>：随价格上涨自动上移的止损</li>
</ul>

<h3>止损设置技巧</h3>
<p>止损不应设置得太紧（容易被正常波动触发）或太宽（损失过大）。建议根据市场波动性和您的风险承受能力来设置。</p>"""
                },
                {
                    "title": "投资组合多元化",
                    "slug": "diversification",
                    "summary": "通过多元化分散风险的策略和方法",
                    "content": """<h2>投资组合多元化</h2>
<p>多元化是降低投资风险的重要策略，通过分散投资来减少单一资产的影响。</p>

<h3>多元化的好处</h3>
<ul>
<li>降低单一资产风险</li>
<li>平滑投资组合波动</li>
<li>提高风险调整后收益</li>
</ul>

<h3>多元化的维度</h3>
<ol>
<li><strong>资产类别</strong>：股票、债券、商品、房地产等</li>
<li><strong>地区</strong>：国内、国际、新兴市场</li>
<li><strong>行业</strong>：科技、金融、消费、医疗等</li>
<li><strong>时间</strong>：定期定额投资，分散入场时机</li>
</ol>

<h3>多元化的注意事项</h3>
<p>过度多元化可能降低收益，应在风险分散和收益之间找到平衡。相关性低的资产组合效果更好。</p>"""
                },
                {
                    "title": "风险收益比",
                    "slug": "risk-reward-ratio",
                    "summary": "理解风险收益比及其在交易决策中的应用",
                    "content": """<h2>风险收益比</h2>
<p>风险收益比是评估交易机会质量的重要指标。</p>

<h3>什么是风险收益比？</h3>
<p>风险收益比 = 潜在收益 / 潜在损失</p>
<p>例如：如果您的止损是20元，目标获利是60元，则风险收益比为3:1。</p>

<h3>理想的风险收益比</h3>
<p>一般建议风险收益比至少为2:1或更高。这意味着即使只有50%的胜率，您仍然可以盈利。</p>

<h3>风险收益比与胜率的关系</h3>
<table>
<tr><th>风险收益比</th><th>盈亏平衡胜率</th></tr>
<tr><td>1:1</td><td>50%</td></tr>
<tr><td>2:1</td><td>33%</td></tr>
<tr><td>3:1</td><td>25%</td></tr>
</table>

<h3>实际应用</h3>
<p>在进入每笔交易前，先计算风险收益比。只有当比率符合您的标准时才进行交易。</p>"""
                }
            ],
            "市场分析": [
                {
                    "title": "技术分析基础",
                    "slug": "technical-analysis",
                    "summary": "学习技术分析的基本概念和常用工具",
                    "content": """<h2>技术分析基础</h2>
<p>技术分析是通过研究历史价格和成交量数据来预测未来价格走势的方法。</p>

<h3>技术分析的三大假设</h3>
<ol>
<li>市场行为包含一切信息</li>
<li>价格沿趋势移动</li>
<li>历史会重演</li>
</ol>

<h3>常用技术指标</h3>
<ul>
<li><strong>移动平均线（MA）</strong>：识别趋势方向</li>
<li><strong>相对强弱指数（RSI）</strong>：判断超买超卖</li>
<li><strong>MACD</strong>：趋势和动量指标</li>
<li><strong>布林带</strong>：波动性和价格通道</li>
</ul>

<h3>技术分析的优缺点</h3>
<p><strong>优点</strong>：客观、可量化、适用于各种市场</p>
<p><strong>缺点</strong>：滞后性、可能产生假信号、需要经验判断</p>"""
                },
                {
                    "title": "支撑和阻力",
                    "slug": "support-resistance",
                    "summary": "理解支撑位和阻力位的概念及交易应用",
                    "content": """<h2>支撑和阻力</h2>
<p>支撑和阻力是技术分析中最基本也是最重要的概念。</p>

<h3>什么是支撑位？</h3>
<p>支撑位是价格下跌过程中可能停止下跌的价格水平，通常是之前的低点或重要心理价位。</p>

<h3>什么是阻力位？</h3>
<p>阻力位是价格上涨过程中可能停止上涨的价格水平，通常是之前的高点或重要心理价位。</p>

<h3>如何识别支撑和阻力</h3>
<ul>
<li>历史高点和低点</li>
<li>整数价位（如100、1000等）</li>
<li>移动平均线</li>
<li>趋势线</li>
<li>斐波那契回撤位</li>
</ul>

<h3>交易策略</h3>
<p>在支撑位买入，在阻力位卖出；突破支撑可能继续下跌，突破阻力可能继续上涨。</p>"""
                },
                {
                    "title": "K线图形态",
                    "slug": "candlestick-patterns",
                    "summary": "学习常见K线图形态及其信号含义",
                    "content": """<h2>K线图形态</h2>
<p>K线图是最常用的价格图表类型，每根K线显示开盘价、收盘价、最高价和最低价。</p>

<h3>单根K线形态</h3>
<ul>
<li><strong>锤子线</strong>：看涨反转信号，出现在下跌趋势底部</li>
<li><strong>上吊线</strong>：看跌反转信号，出现在上涨趋势顶部</li>
<li><strong>十字星</strong>：表示市场犹豫，可能反转</li>
<li><strong>长影线</strong>：表示价格被拒绝</li>
</ul>

<h3>多根K线形态</h3>
<ul>
<li><strong>吞没形态</strong>：强烈的反转信号</li>
<li><strong>早晨之星/黄昏之星</strong>：三根K线的反转形态</li>
<li><strong>三只乌鸦/三白兵</strong>：连续三根同向K线</li>
</ul>

<h3>使用K线形态的注意事项</h3>
<p>K线形态应结合趋势、支撑阻力和其他指标一起使用，单独使用可能产生假信号。</p>"""
                },
                {
                    "title": "基本面分析",
                    "slug": "fundamental-analysis",
                    "summary": "了解基本面分析的方法和关键指标",
                    "content": """<h2>基本面分析</h2>
<p>基本面分析通过研究公司财务状况、行业前景和宏观经济来评估资产价值。</p>

<h3>基本面分析的关键指标</h3>
<ul>
<li><strong>市盈率（P/E）</strong>：股价与每股收益的比率</li>
<li><strong>市净率（P/B）</strong>：股价与每股净资产的比率</li>
<li><strong>ROE</strong>：净资产收益率，衡量盈利能力</li>
<li><strong>负债率</strong>：评估公司财务风险</li>
</ul>

<h3>宏观经济因素</h3>
<ul>
<li>GDP增长率</li>
<li>通货膨胀率</li>
<li>利率政策</li>
<li>就业数据</li>
</ul>

<h3>基本面 vs 技术分析</h3>
<p>基本面分析关注"买什么"，技术分析关注"何时买"。两者结合使用效果更好。</p>"""
                }
            ],
            "交易平台": [
                {
                    "title": "费用结构详解",
                    "slug": "fee-structure",
                    "summary": "全面了解交易手续费、借款利息和其他隐含成本",
                    "content": """<h2>费用结构详解</h2>
<p>了解各种交易费用对于计算真实收益至关重要。</p>

<h3>常见费用类型</h3>
<ul>
<li><strong>交易手续费</strong>：每次买卖时收取，通常按交易金额的百分比</li>
<li><strong>融资利息</strong>：杠杆交易借入资金的利息成本</li>
<li><strong>隔夜费</strong>：持仓过夜产生的费用</li>
<li><strong>点差</strong>：买入价和卖出价之间的差额</li>
<li><strong>出入金费用</strong>：充值和提现的手续费</li>
</ul>

<h3>费用计算示例</h3>
<p>假设：交易金额10000元，手续费0.1%，融资利息年化8%</p>
<p>手续费 = 10000 × 0.1% × 2（买卖各一次）= 20元</p>
<p>日融资利息 = 10000 × 8% / 365 = 2.19元</p>

<h3>如何降低交易成本</h3>
<ol>
<li>选择低费率平台</li>
<li>减少交易频率</li>
<li>使用限价单而非市价单</li>
<li>关注VIP等级优惠</li>
</ol>"""
                },
                {
                    "title": "如何选择交易平台",
                    "slug": "choosing-platform",
                    "summary": "选择适合自己的交易平台的关键因素和建议",
                    "content": """<h2>如何选择交易平台</h2>
<p>选择合适的交易平台是成功交易的重要基础。</p>

<h3>选择平台的关键因素</h3>
<ol>
<li><strong>监管合规</strong>：选择持有正规牌照、受监管的平台</li>
<li><strong>费用结构</strong>：比较手续费、点差、融资利息等</li>
<li><strong>交易品种</strong>：确保平台提供您需要的交易品种</li>
<li><strong>杠杆选项</strong>：检查可用的杠杆比例</li>
<li><strong>用户体验</strong>：平台界面、交易工具、移动端支持</li>
<li><strong>客户服务</strong>：响应速度、服务质量、中文支持</li>
<li><strong>资金安全</strong>：客户资金隔离、保险保障</li>
</ol>

<h3>评估平台的步骤</h3>
<ol>
<li>查阅监管信息和牌照</li>
<li>阅读用户评价和评测</li>
<li>使用模拟账户体验</li>
<li>小额资金测试出入金</li>
<li>测试客服响应</li>
</ol>

<h3>红旗警告</h3>
<p>警惕：无监管、承诺高回报、出金困难、负面评价多的平台。</p>"""
                },
                {
                    "title": "平台安全性",
                    "slug": "platform-security",
                    "summary": "了解如何评估和确保交易平台的安全性",
                    "content": """<h2>平台安全性</h2>
<p>资金安全是选择交易平台时最重要的考虑因素之一。</p>

<h3>平台安全性评估要点</h3>
<ul>
<li><strong>监管牌照</strong>：FCA、ASIC、CySEC等权威监管</li>
<li><strong>资金隔离</strong>：客户资金与公司运营资金分开存放</li>
<li><strong>投资者保护</strong>：是否有投资者赔偿计划</li>
<li><strong>加密技术</strong>：SSL加密、双因素认证</li>
<li><strong>公司背景</strong>：上市公司、历史记录</li>
</ul>

<h3>账户安全措施</h3>
<ol>
<li>启用双因素认证（2FA）</li>
<li>使用强密码并定期更换</li>
<li>不在公共网络进行交易</li>
<li>定期检查账户活动</li>
<li>警惕钓鱼邮件和网站</li>
</ol>

<h3>遇到问题怎么办</h3>
<p>如果遇到平台问题，首先联系客服；如无法解决，可向监管机构投诉；保留所有交易记录和通讯证据。</p>"""
                }
            ]
        }
        
        # 创建文章
        created_count = 0
        for category_name, articles in wiki_data.items():
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
        
        print(f"\n✅ 完成！共处理 {created_count} 篇文章")
        
    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    print("🚀 开始初始化Wiki百科文章...")
    init_wiki_articles()

