class User:
    def __init__(self, id: int, name: str) -> None:
        super().__init__()
        self.id = id
        self.name = name

    def get_id(self) -> int:
        return self.id

    def get_name(self) -> str:
        return self.name

    def set_name(self, name: str) -> None:
        self.name = name
