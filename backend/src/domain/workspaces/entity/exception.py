

class WorkspaceNotFound(Exception):
    def __init__(self, message="Workspace not found"):
        self.message = message
        super().__init__(self.message)


class GroupNotFound(Exception):
    def __init__(self, message="Group not found"):
        self.message = message
        super().__init__(self.message)

class TaskNotFound(Exception):
    def __init__(self, message="Task not found"):
        self.message = message
        super().__init__(self.message)