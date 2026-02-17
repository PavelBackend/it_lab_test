

class DomainException(Exception):
    """Base domain exception."""
    pass


class TaskNotFoundException(DomainException):
    """Task not found exception."""
    def __init__(self, task_id: str):
        self.task_id = task_id
        super().__init__(f"Task with id {task_id} not found")


class CategoryNotFoundException(DomainException):
    """Category not found exception."""
    def __init__(self, category_id: str):
        self.category_id = category_id
        super().__init__(f"Category with id {category_id} not found")


class InvalidTaskDataException(DomainException):
    """Invalid task data exception."""
    pass


class UnauthorizedAccessException(DomainException):
    """Unauthorized access to resource exception."""
    pass
