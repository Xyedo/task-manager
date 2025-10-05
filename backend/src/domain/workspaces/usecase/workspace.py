import datetime

from src.domain.workspaces.entity.update_group import (
    UpdateGroupRequest,
    UpdateGroupResponse,
)
from src.domain.workspaces.entity.create_task import CreateTaskResponse
from src.domain.workspaces.entity.create import WorkspaceRequest, WorkspaceResponse
from src.common.token import TokenPayload
from src.domain.workspaces.entity.pagination import (
    WorkspacePagination,
    WorkspacePaginationResponse,
)
from src.infrastructure.database.repository import Repository
from src.domain.workspaces.entity.task import (
    CreateTask,
    DeleteTask,
    GetTaskById,
    UpdateTask,
)
from src.domain.workspaces.entity.exception import (
    GroupNotFound,
    TaskNotFound,
    WorkspaceNotFound,
)
from migrations.schema import Account, Group, Workspaces, Task
from src.domain.workspaces.entity.list_group import (
    GroupByWorkspaceRequest,
    GroupByWorkspaceResponse,
    GroupResponse,
    TaskResponse,
)


class WorkspaceUsecase:
    __repository: Repository

    def __init__(self):
        self.__repository = Repository()

    def list_workspaces(
        self, auth: TokenPayload, pagination: WorkspacePagination
    ) -> WorkspacePaginationResponse:
        print("here on list workspace")
        with self.__repository.session() as session:
            workspaces = (
                session.query(Workspaces)
                .where(
                    Workspaces.tenant_id == auth.tenant_id,
                    Workspaces.workspace_id
                    > (pagination.lastId if pagination.lastId else 0),
                )
                .order_by(Workspaces.workspace_id)
                .limit(pagination.limit if pagination.limit else 10)
                .all()
            )

            return WorkspacePaginationResponse(
                workspaces=[
                    WorkspaceResponse(
                        workspaceId=workspace.workspace_id,
                        name=workspace.name,
                        createdAt=workspace.created_at,
                        updatedAt=workspace.updated_at,
                        createdBy=workspace.created_by,
                        updatedBy=workspace.updated_by,
                    )
                    for workspace in workspaces
                ]
            )

    def create_workspace(
        self, auth: TokenPayload, workspace: WorkspaceRequest
    ) -> WorkspaceResponse:

        with self.__repository.session() as session:
            new_workspace = Workspaces(
                name=workspace.name, tenant_id=auth.tenant_id, created_by=auth.id
            )
            session.add(new_workspace)
            session.flush()

            default_groups = ["To Do", "In Progress", "In Review", "Done"]
            for group_name in default_groups:
                group = Group(
                    tenant_id=auth.tenant_id,
                    name=group_name,
                    workspace_id=new_workspace.workspace_id,
                    created_by=auth.id,
                )
                session.add(group)

            return WorkspaceResponse(
                workspaceId=new_workspace.workspace_id,
                name=new_workspace.name,
                createdAt=new_workspace.created_at,
                updatedAt=new_workspace.updated_at,
                createdBy=new_workspace.created_by,
                updatedBy=new_workspace.updated_by,
            )

    def workspace_detail(
        self, auth: TokenPayload, payload: GroupByWorkspaceRequest
    ) -> GroupByWorkspaceResponse:

        with self.__repository.session() as session:
            workspace = (
                session.query(Workspaces)
                .where(
                    Workspaces.name == payload.name,
                    Workspaces.tenant_id == auth.tenant_id,
                )
                .first()
            )

            if not workspace:
                raise WorkspaceNotFound()

            groups = (
                session.query(Group)
                .where(Group.workspace_id == workspace.workspace_id)
                .join(Task, Task.group_id == Group.group_id, isouter=True)
                .join(
                    Account,
                    Task.assigned_to_user_id == Account.account_id,
                    isouter=True,
                )
                .order_by(Group.group_id)
                .all()
            )

            return GroupByWorkspaceResponse(
                workspaceId=groups[0].workspace_id,
                groups=[
                    GroupResponse(
                        groupId=group.group_id,
                        name=group.name,
                        tasks=[
                            TaskResponse(
                                taskId=task.task_id,
                                title=task.title,
                                description=task.description,
                                dueDate=task.due_date,
                                assignedToUserId=task.assigned_to_user_id,
                                assignedTo=(
                                    task.assigned_to_user.full_name
                                    if task.assigned_to_user_id
                                    else None
                                ),
                                createdAt=task.created_at,
                                updatedAt=task.updated_at,
                                createdBy=task.created_by,
                                updatedBy=task.updated_by,
                            )
                            for task in group.tasks
                        ],
                        createdAt=group.created_at,
                        updatedAt=group.updated_at,
                        createdBy=group.created_by,
                        updatedBy=group.updated_by,
                    )
                    for group in groups
                ],
            )

    def update_group(
        self, auth: TokenPayload, payload: UpdateGroupRequest
    ) -> UpdateGroupResponse:
        with self.__repository.session() as session:
            workspace = (
                session.query(Workspaces)
                .where(
                    Workspaces.workspace_id == payload.workspaceId,
                )
                .first()
            )

            if not workspace or workspace.tenant_id != auth.tenant_id:
                raise WorkspaceNotFound()

            existing_group = (
                session.query(Group).where(Group.group_id == payload.groupId).first()
            )
            if (
                not existing_group
                or existing_group.workspace_id != workspace.workspace_id
            ):
                raise GroupNotFound()

            existing_group.name = payload.name
            existing_group.updated_by = auth.id
            existing_group.updated_at = datetime.datetime.now(datetime.timezone.utc)
            session.add(existing_group)
            session.flush()

            return UpdateGroupResponse(
                groupId=existing_group.group_id,
                name=existing_group.name,
                createdAt=existing_group.created_at,
                updatedAt=existing_group.updated_at,
                createdBy=existing_group.created_by,
                updatedBy=existing_group.updated_by,
            )

    def create_task(self, auth: TokenPayload, task: CreateTask) -> CreateTaskResponse:

        with self.__repository.session() as session:
            workspace = (
                session.query(Workspaces)
                .where(
                    Workspaces.workspace_id == task.workspaceId,
                )
                .first()
            )

            if not workspace or workspace.tenant_id != auth.tenant_id:
                raise WorkspaceNotFound()

            group = session.query(Group).where(Group.group_id == task.groupId).first()
            if not group or group.workspace_id != workspace.workspace_id:
                raise GroupNotFound()

            new_task = Task(
                group_id=group.group_id,
                tenant_id=auth.tenant_id,
                title=task.title,
                description=task.description,
                due_date=task.dueDate,
                assigned_to_user_id=task.assignedToUserId,
                created_by=auth.id,
            )
            session.add(new_task)
            session.flush()

            session.query(Task).where(Task.task_id == new_task.task_id).join(
                Account, Task.assigned_to_user_id == Account.account_id, isouter=True
            )

            return CreateTaskResponse(
                taskId=new_task.task_id,
                assignedToUserId=new_task.assigned_to_user_id,
                assignedTo=(
                    new_task.assigned_to_user.full_name
                    if new_task.assigned_to_user_id
                    else None
                ),
                title=new_task.title,
                description=new_task.description,
                dueDate=new_task.due_date,
                createdAt=new_task.created_at,
                updatedAt=new_task.updated_at,
                createdBy=new_task.created_by,
                updatedBy=new_task.updated_by,
            )

    def update_task(self, auth: TokenPayload, payload: UpdateTask) -> Task:

        update_data = payload.model_dump(exclude_unset=True)
        print(update_data)
        with self.__repository.session() as session:
            workspace = (
                session.query(Workspaces)
                .where(Workspaces.workspace_id == payload.workspaceId)
                .first()
            )
            if not workspace or workspace.tenant_id != auth.tenant_id:
                raise WorkspaceNotFound()

            existing_task = (
                session.query(Task).where(Task.task_id == payload.taskId).first()
            )

            if (
                not existing_task
                or existing_task.tenant_id != auth.tenant_id
                or existing_task.group_id != payload.groupId
            ):
                raise TaskNotFound()

            for field, value in update_data.items():
                if field == "assignedToUserId":
                    existing_task.assigned_to_user_id = value
                    continue

                if field == "dueDate":
                    existing_task.due_date = value
                    continue

                if field == "title":
                    existing_task.title = value
                    continue

                if field == "toGroupId":
                    existing_task.group_id = value
                    continue

            existing_task.updated_by = auth.id
            existing_task.updated_at = datetime.datetime.now(datetime.timezone.utc)

            session.flush()

            return existing_task

    def get_task(self, auth: TokenPayload, payload: GetTaskById) -> Task:

        with self.__repository.session() as session:
            existing_task = (
                session.query(Task).where(Task.task_id == payload.taskId).first()
            )
            if not existing_task or existing_task.tenant_id != auth.tenant_id:
                raise TaskNotFound()

            return existing_task

    def delete_task(self, auth: TokenPayload, payload: DeleteTask) -> None:

        with self.__repository.session() as session:
            existing_task = (
                session.query(Task).where(Task.task_id == payload.taskId).first()
            )
            if not existing_task or existing_task.tenant_id != auth.tenant_id:
                raise TaskNotFound()

            session.delete(existing_task)
            session.flush()
