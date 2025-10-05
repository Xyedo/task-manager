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

        account = Account(
            username="user",
            full_name="Demo User",
            email="user@example.com",
            hashed_password=hasher.hash("password"),
            tenant_id=tenant.tenant_id,
        )
        session.add(account)
        session.flush()

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
