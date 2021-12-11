import re
import json
import struct

from .abstract_compiler import AbstractCompiler


def slice(str, i):
    return str[:i], str[i:]


# nexe https://github.com/nexe/nexe
class Nexe(AbstractCompiler):
    NEXE_SENTINEL = b"<nexe~~sentinel>"

    @staticmethod
    def check(data):
        # perhaps we make this dynamic in case some goofy goober
        # decides to add erroneous padding to the end of their file?
        return data[-32:-16] == Nexe.NEXE_SENTINEL

    def decompile(self) -> None:
        self.entrypoint = (
            re.search(
                rb"const entry = path\.resolve\(path\.dirname\(process\.execPath\),\"(\S*.js)\"\)",
                self._data,
            )
            .group(1)
            .decode()
        )

        code_size, bundle_size = map(int, struct.unpack("<dd", self._data[-16:]))

        start = (
            len(self._data) - code_size - bundle_size - len(self.NEXE_SENTINEL) - 16
        )  # code, bundle, sentinel, lengths

        self.node, rest = slice(self._data, start)
        self.code, rest = slice(rest, code_size)
        self.bundle, rest = slice(rest, bundle_size)

        resources = re.search(rb"process\.__nexe = (.*);\n", self.code).group(1)
        self.resources = json.loads(resources)["resources"]

        self.files = {
            path: self.bundle[pos : pos + length]
            for path, (pos, length) in self.resources.items()
        }
