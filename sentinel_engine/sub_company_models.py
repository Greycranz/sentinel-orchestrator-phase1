"""
Sentinel Engine Phase 3 - Sub-Company Factory Models
Database models for autonomous sub-company creation and management
"""
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, Float, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import json

try:
    from .models import Base
except ImportError:
    from sqlalchemy.ext.declarative import declarative_base
    Base = declarative_base()

class SubCompany(Base):
    __tablename__ = "sub_companies"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    slug = Column(String, unique=True, index=True)  # URL-safe name
    description = Column(Text)
    industry = Column(String, index=True)
    status = Column(String, default="planning", index=True)  # planning, building, testing, live, paused
    
    # Business details
    mission = Column(Text)
    target_market = Column(Text)
    value_proposition = Column(Text)
    business_model = Column(Text)
    
    # Technical details
    repository_url = Column(String)
    main_product = Column(String)
    tech_stack = Column(JSON)
    api_endpoints = Column(JSON)
    
    # Financial tracking
    revenue_target = Column(Float, default=0.0)
    current_revenue = Column(Float, default=0.0)
    monthly_costs = Column(Float, default=0.0)
    profit_margin = Column(Float, default=0.0)
    
    # Operational
    agents_deployed = Column(JSON)  # List of agent types
    last_activity = Column(DateTime, default=datetime.utcnow)
    health_score = Column(Float, default=100.0)
    
    # Relationships
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    
    # Foreign keys
    parent_company_id = Column(Integer, default=1)  # Sentinel Engine = 1

class SubCompanyAgent(Base):
    __tablename__ = "sub_company_agents"
    
    id = Column(Integer, primary_key=True, index=True)
    sub_company_id = Column(Integer, ForeignKey("sub_companies.id"))
    agent_type = Column(String, index=True)  # builder, marketing, legal, finance, etc.
    name = Column(String)
    status = Column(String, default="active")
    capabilities = Column(JSON)
    configuration = Column(JSON)
    
    # Performance tracking
    jobs_completed = Column(Integer, default=0)
    success_rate = Column(Float, default=100.0)
    last_active = Column(DateTime, default=datetime.utcnow)
    
    created_at = Column(DateTime, default=datetime.utcnow)

class SubCompanyProduct(Base):
    __tablename__ = "sub_company_products"
    
    id = Column(Integer, primary_key=True, index=True)
    sub_company_id = Column(Integer, ForeignKey("sub_companies.id"))
    name = Column(String)
    description = Column(Text)
    product_type = Column(String)  # software, service, content, etc.
    status = Column(String, default="development")  # development, testing, live, deprecated
    
    # Product details
    features = Column(JSON)
    pricing_model = Column(String)
    target_customers = Column(Text)
    competitive_advantages = Column(JSON)
    
    # Metrics
    users_count = Column(Integer, default=0)
    revenue = Column(Float, default=0.0)
    growth_rate = Column(Float, default=0.0)
    customer_satisfaction = Column(Float, default=0.0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)

class AiSourcingRequest(Base):
    __tablename__ = "ai_sourcing_requests"
    
    id = Column(Integer, primary_key=True, index=True)
    sub_company_id = Column(Integer, ForeignKey("sub_companies.id"))
    customer_email = Column(String)
    customer_name = Column(String)
    
    # Request details
    feature_request = Column(Text)
    use_case = Column(Text)
    priority = Column(String, default="medium")  # low, medium, high, critical
    complexity = Column(String)  # simple, moderate, complex, enterprise
    
    # Legal and safety
    safety_approved = Column(Boolean, default=False)
    legal_approved = Column(Boolean, default=False)
    ip_ownership_agreed = Column(Boolean, default=False)
    
    # Development tracking
    status = Column(String, default="submitted")  # submitted, approved, developing, testing, completed, rejected
    estimated_hours = Column(Integer)
    actual_hours = Column(Integer)
    developer_assigned = Column(String)
    
    # Business value
    customer_value = Column(Float, default=0.0)
    business_value = Column(Float, default=0.0)
    revenue_potential = Column(Float, default=0.0)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)

class CompanyTemplate(Base):
    __tablename__ = "company_templates"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True)
    description = Column(Text)
    industry = Column(String)
    
    # Template configuration
    agent_types = Column(JSON)  # List of required agent types
    tech_stack = Column(JSON)  # Default technology stack
    business_model = Column(String)
    initial_features = Column(JSON)
    
    # Setup automation
    repository_template = Column(String)  # Git repo template URL
    deployment_config = Column(JSON)
    environment_variables = Column(JSON)
    
    # Success metrics
    target_revenue = Column(Float)
    target_timeline = Column(Integer)  # Days to launch
    success_criteria = Column(JSON)
    
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class CrossCompanyMessage(Base):
    __tablename__ = "cross_company_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    from_company_id = Column(Integer, ForeignKey("sub_companies.id"))
    to_company_id = Column(Integer, ForeignKey("sub_companies.id"))
    
    message_type = Column(String)  # request, response, notification, collaboration
    subject = Column(String)
    content = Column(Text)
    data_payload = Column(JSON)
    
    # Status tracking
    status = Column(String, default="sent")  # sent, delivered, read, processed, archived
    priority = Column(String, default="normal")  # low, normal, high, urgent
    
    sent_at = Column(DateTime, default=datetime.utcnow)
    read_at = Column(DateTime)
    processed_at = Column(DateTime)
