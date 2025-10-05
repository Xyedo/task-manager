class UserNotFound(Exception):
    def __init__(self, message="User not found"):
        self.message = message
        super().__init__(self.message)


class InvalidCredentials(Exception):
    def __init__(self, message="Invalid credentials"):
        self.message = message
        super().__init__(self.message)


class RefreshTokenNotFound(Exception):
    def __init__(self, message="Invalid refresh token"):
        self.message = message
        super().__init__(self.message)
