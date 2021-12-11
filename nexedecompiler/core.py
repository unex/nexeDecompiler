from .compilers import Nexe, Pkg


class NexeDecompiler:
    COMPILERS = [Nexe, Pkg]

    def __init__(self, data: bytes) -> None:
        self.__data = data

    @classmethod
    def from_file(cls, fp):
        fp.seek(0)
        return cls(fp.read())

    def decompile(self):
        for compiler in self.COMPILERS:
            if compiler.check(self.__data):
                c = compiler(self.__data)
                c.decompile()
                return c
