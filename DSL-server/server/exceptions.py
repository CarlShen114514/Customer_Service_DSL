class TypeException(Exception):
    def __init__(self, msg: str, context: list[str]) -> None:
        self.msg = msg
        self.context = context

class GrammarException(Exception):
    def __init__(self, msg: str, context: list[str]) -> None:
        self.msg = msg
        self.context = context

class NetworkException(Exception):
    def __init__(self, msg: str, context: list[str]) -> None:
        self.msg = msg
        self.context = context



