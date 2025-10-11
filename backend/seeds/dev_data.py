import dotenv
import sqlalchemy as sa
from sqlalchemy.orm import Session
from migrations.schema import Task, Tenant, Account, Workspaces, Group

import os
from faker import Faker
from argon2 import PasswordHasher


def main():
    dotenv.load_dotenv()

    engine = sa.create_engine(os.environ.get("DATABASE_URL"))
    hasher = PasswordHasher()

    with Session(engine) as session:
        fake = Faker()
        tenant = Tenant(name=fake.company())
        session.add(tenant)

        session.flush()

        for _ in range(100):
            pw = fake.password()
            hashed_pw = hasher.hash(pw)
            account = Account(
                username=fake.user_name(),
                email=fake.email(),
                full_name=fake.name(),
                hashed_password=hashed_pw,
                tenant_id=tenant.tenant_id,
            )
            session.add(account)

        # Create demo user for testing
        user_account = Account(
            username="user",
            full_name="Demo User",
            email="user@example.com",
            hashed_password=hasher.hash("password"),
            tenant_id=tenant.tenant_id,
        )
        session.add(user_account)
        
        # Create admin user for load testing
        admin_account = Account(
            username="admin",
            full_name="Admin User",
            email="admin@example.com",
            hashed_password=hasher.hash("adminpassword"),
            tenant_id=tenant.tenant_id,
        )
        session.add(admin_account)
        
        # Create additional test users for load testing
        test_users_data = [
            ("testuser", "testpassword", "Test User", "testuser@example.com"),
            ("loadtest1", "password123", "Load Test User 1", "loadtest1@example.com"),
            ("loadtest2", "password123", "Load Test User 2", "loadtest2@example.com"),
            ("loadtest3", "password123", "Load Test User 3", "loadtest3@example.com"),
        ]
        
        for username, password, full_name, email in test_users_data:
            test_account = Account(
                username=username,
                full_name=full_name,
                email=email,
                hashed_password=hasher.hash(password),
                tenant_id=tenant.tenant_id,
            )
            session.add(test_account)
        
        session.flush()
        
        # Use the regular user for workspace creation
        account = user_account

        workspace = Workspaces(
            name="My Kanban Project",
            tenant_id=tenant.tenant_id,
            created_by=account.account_id,
        )
        session.add(workspace)
        session.flush()

        for group_name in ["To Do", "In Progress", "In Review", "Done"]:
            group = Group(
                name=group_name,
                workspace_id=workspace.workspace_id,
                created_by=account.account_id,
                tenant_id=tenant.tenant_id,
            )
            session.add(group)
            if group_name == "To Do":
                session.flush()
                task = Task(
                    title=f"Task 2",
                    description=f"This is the description for task 2.",
                    group=group,
                    created_by=account.account_id,
                    tenant_id=tenant.tenant_id,
                    due_date=fake.date_between(start_date="now", end_date="+30d"),
                )
                session.add(task)

            if group_name == "In Progress":
                session.flush()
                task = Task(
                    title=f"Task 1",
                    description=f"This is the description for task 1.",
                    group=group,
                    created_by=account.account_id,
                    tenant_id=tenant.tenant_id,
                    due_date=fake.date_between(start_date="now", end_date="+30d"),
                )
                session.add(task)

        session.commit()
    print("Development data seeded successfully.")


if __name__ == "__main__":
    main()
