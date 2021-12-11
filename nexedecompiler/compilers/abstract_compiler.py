from typing import Dict


class AbstractCompiler:
    files: Dict[str, bytes]
    entrypoint: str

    def __init__(self, data: bytes) -> None:
        self._data = data

        self.decompile()

    def decompile(self):
        raise NotImplementedError()
