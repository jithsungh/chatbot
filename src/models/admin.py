import uuid
import enum
from sqlalchemy import Column, Boolean, TIMESTAMP, Text, Enum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from .base import Base

class AdminRole(enum.Enum):
    super_admin = "super_admin"
    admin = "admin"
    read_only = "read_only"

class Admin(Base):
    __tablename__ = "admins"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(Text, nullable=False)
    email = Column(Text, nullable=False, unique=True)
    password = Column(Text, nullable=False)
    enabled = Column(Boolean, default=False)
    verified = Column(Boolean, default=False)
    role = Column(Enum(AdminRole), default=AdminRole.admin)
    verification_token = Column(Text, nullable=True)
    last_login = Column(TIMESTAMP(timezone=True), nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    
    @classmethod
    def create(cls, session, name, email, password, enabled=False, verification_token=None):
        """Create a new admin"""
        new_admin = cls(
            name=name,
            email=email,
            password=password,
            enabled=enabled,
            verification_token=verification_token
        )
        session.add(new_admin)
        session.commit()
        return new_admin
    
    @classmethod
    def get_count(cls, session):
        """ return total count of records"""
        return session.query(cls).count()
    
    @classmethod
    def get_name_by_id(cls, session, admin_id):
        """Get admin name by ID"""
        admin = session.query(cls).filter_by(id=admin_id).first()
        return admin.name if admin else None
    
    @classmethod
    def get_by_id(cls, session, admin_id):
        """Get admin by ID"""
        return session.query(cls).filter_by(id=admin_id).first()
    
    @classmethod
    def get_by_email(cls, session, email):
        """Get admin by email"""
        return session.query(cls).filter_by(email=email).first()
    
    @classmethod
    def get_all(cls, session):
        """Get all admins"""
        return session.query(cls).all()
    
    @classmethod
    def get_enabled_admins(cls, session):
        """Get all enabled admins"""
        return session.query(cls).filter_by(enabled=True).all()
    
    @classmethod
    def update_last_login(cls, session, admin_id):
        """Update last login timestamp"""
        admin = session.query(cls).filter_by(id=admin_id).first()
        if admin:
            admin.last_login = func.now()
            session.commit()
            return admin
        return None
    
    @classmethod
    def enable_admin(cls, session, admin_id):
        """Enable an admin account"""
        admin = session.query(cls).filter_by(id=admin_id).first()
        if admin:
            admin.enabled = True
            session.commit()
            return admin
        return None
    
    @classmethod
    def disable_admin(cls, session, admin_id):
        """Disable an admin account"""
        admin = session.query(cls).filter_by(id=admin_id).first()
        if admin:
            admin.enabled = False
            session.commit()
            return admin
        return None
    
    @classmethod
    def delete_by_id(cls, session, admin_id):
        """Delete admin by ID"""
        admin = session.query(cls).filter_by(id=admin_id).first()
        if admin:
            session.delete(admin)
            session.commit()
            return True
        return False
    
    @classmethod
    def update_password(cls, session, admin_id, new_password):
        """Update admin password"""
        admin = session.query(cls).filter_by(id=admin_id).first()
        if admin:
            admin.password = new_password
            session.commit()
            return admin
        return None

    def to_dict(self):
        """Convert admin object to dictionary (excluding password)"""
        return {
            "id": str(self.id),
            "name": self.name,
            "email": self.email,
            "role": self.role.value,  # Include role information
            "enabled": self.enabled,
            "verified": self.verified,  # Include verification status
            "last_login": self.last_login.isoformat() if self.last_login else None,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

    def __repr__(self):
        return f"<Admin(id='{self.id}', name='{self.name}', email='{self.email}', enabled={self.enabled})>"