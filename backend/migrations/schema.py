from sqlalchemy import Column, ForeignKey, Integer, DateTime, String, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import schema
from sqlalchemy.orm import relationship


Base = declarative_base()


class Authentication(Base):
    __tablename__ = "authentication"

    token = Column(String, primary_key=True, nullable=False)


class Tenant(Base):
    __tablename__ = "tenant"

    tenant_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)


class Account(Base):
    __tablename__ = "account"

    tenant_id = Column(Integer, ForeignKey("tenant.tenant_id"), nullable=False)

    account_id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)


class Workspaces(Base):
    __tablename__ = "workspace"

    tenant_id = Column(Integer, ForeignKey("tenant.tenant_id"), nullable=False)

    workspace_id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False)

    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(Integer, ForeignKey("account.account_id"), nullable=False)
    updated_by = Column(Integer, ForeignKey("account.account_id"), nullable=True)

    groups = relationship("Group", backref="workspace", cascade="all, delete-orphan")

    __table_args__ = (
        schema.UniqueConstraint("tenant_id", "name", name="uq_workspace_tenant_name"),
    )


class Group(Base):
    __tablename__ = "group"

    tenant_id = Column(Integer, ForeignKey("tenant.tenant_id"), nullable=False)

    group_id = Column(Integer, primary_key=True, autoincrement=True)
    workspace_id = Column(Integer, ForeignKey("workspace.workspace_id"), nullable=False)
    name = Column(String, nullable=False)

    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(Integer, ForeignKey("account.account_id"), nullable=False)
    updated_by = Column(Integer, ForeignKey("account.account_id"), nullable=True)

    tasks = relationship("Task", backref="group", cascade="all, delete-orphan")

    __table_args__ = (
        schema.UniqueConstraint("workspace_id", "name", name="uq_group_workspace_name"),
        schema.Index("group_workspace_id_idx", "workspace_id"),
    )


class Task(Base):
    __tablename__ = "task"

    tenant_id = Column(Integer, ForeignKey("tenant.tenant_id"), nullable=False)

    task_id = Column(Integer, primary_key=True, autoincrement=True)
    group_id = Column(Integer, ForeignKey("group.group_id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    due_date = Column(DateTime(timezone=True), nullable=True)
    assigned_to_user_id = Column(
        Integer, ForeignKey("account.account_id"), nullable=True
    )
    assigned_to_user = relationship(
        "Account", foreign_keys=[assigned_to_user_id], backref="task"
    )

    created_at = Column(
        DateTime(timezone=True), server_default=func.now(), nullable=False
    )
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(Integer, ForeignKey("account.account_id"), nullable=False)
    updated_by = Column(Integer, ForeignKey("account.account_id"), nullable=True)

    __table_args__ = (schema.Index("task_group_id_idx", "group_id"),)
