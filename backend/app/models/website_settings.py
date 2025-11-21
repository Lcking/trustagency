"""
网站设置模型 - 存储网站级别的配置信息
"""
from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime
from app.database import Base


class WebsiteSettings(Base):
    """网站设置模型"""
    __tablename__ = "website_settings"

    id = Column(Integer, primary_key=True, index=True)
    
    # SEO 设置
    site_title = Column(String(255), default="股票杠杆平台排行榜单")
    site_description = Column(Text, default="专业的股票杠杆交易平台排行榜单，提供平台对比、风险指标、开户指南等全方位信息。")
    site_keywords = Column(String(500), default="股票杠杆,保证金交易,平台排行,杠杆平台")
    
    # 网站信息
    site_name = Column(String(255), default="TrustAgency")
    site_author = Column(String(255), default="TrustAgency团队")
    site_favicon = Column(String(500), nullable=True)
    site_logo = Column(String(500), nullable=True)
    
    # 分析代码
    google_analytics = Column(Text, nullable=True, comment="Google Analytics 追踪代码")
    baidu_analytics = Column(Text, nullable=True, comment="百度统计代码")
    custom_scripts = Column(Text, nullable=True, comment="自定义脚本（放在</head>前）")
    
    # 页脚设置
    icp_number = Column(String(50), nullable=True, comment="ICP 备案号")
    company_name = Column(String(255), nullable=True, comment="公司名称")
    company_address = Column(String(500), nullable=True, comment="公司地址")
    contact_phone = Column(String(20), nullable=True, comment="联系电话")
    contact_email = Column(String(100), nullable=True, comment="联系邮箱")
    
    # 友情链接
    footer_links = Column(Text, nullable=True, comment="页脚友情链接 JSON 格式")
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f"<WebsiteSettings(id={self.id}, site_name={self.site_name})>"
