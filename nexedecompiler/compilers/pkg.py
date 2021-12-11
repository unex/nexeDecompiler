import re
import json

from enum import Enum

from .abstract_compiler import AbstractCompiler


class StripeType(Enum):
    BLOB = "0"  # v8 bytecode
    CONTENT = "1"  # raw js
    LINKS = "2"
    STAT = "3"


# TODO implement decompression
class CompressionType(Enum):
    NONE = "0"
    GZIP = "1"
    BROTLI = "2"


# pkg https://github.com/vercel/pkg
class Pkg(AbstractCompiler):
    @staticmethod
    def check(data):
        # pkg uses this to bootstrap node, so it should exist in all pkg binaries...
        return re.search(rb"pkg/prelude/bootstrap.js", data)

    def decompile(self):
        payload_pos_m = re.search(rb"var PAYLOAD_POSITION = '(\d*).*'", self.__data)
        payload_len_m = re.search(rb"var PAYLOAD_SIZE = '(\d*).*'", self.__data)
        prelude_pos_m = re.search(rb"var PRELUDE_POSITION = '(\d*).*'", self.__data)
        prelude_len_m = re.search(rb"var PRELUDE_SIZE = '(\d*).*'", self.__data)

        payload_pos = int(payload_pos_m.group(1))
        payload_len = int(payload_len_m.group(1))
        prelude_pos = int(prelude_pos_m.group(1))
        prelude_len = int(prelude_len_m.group(1))

        payload = self.__data[payload_pos : payload_pos + payload_len]
        prelude = self.__data[prelude_pos : prelude_pos + prelude_len]

        prelude_data = re.search(
            rb"\/\/# sourceMappingURL=common\.js\.map\n\},\n(?P<virtfs>\{.*\})\n,\n(?P<entrypoint>.*)\n,\n(?P<symlinks>\{.*\})\n,\n(?P<_dict>\{.*\})\n,\n(?P<docompress>\d*)\n\);",
            prelude,
        )

        virtfs, entrypoint, symlinks, _dict, docompress = (
            v.decode() for k, v in prelude_data.groupdict().items()
        )

        self.virtfs = json.loads(virtfs)
        self.entrypoint = entrypoint
        self.symlinks = json.loads(symlinks)
        self.dict = json.loads(_dict)
        self.docompress = docompress

        self.files = {}

        for path, slices in virtfs.items():
            for typ, (pos, length) in slices.items():
                path = path.replace("C:\\snapshot\\", "")

                data = payload[pos : pos + length]

                if typ == StripeType.BLOB.value:
                    path = path.replace(".js", ".jsc")
                    self.files[path] = data

                elif typ == StripeType.CONTENT.value:
                    self.files[path] = data
