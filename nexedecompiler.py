import re
import sys
import json
import struct

from enum import Enum
from pathlib import PurePath, Path

def slice(str, i):
    return str[:i], str[i:]

# nexe https://github.com/nexe/nexe

NEXE_SENTINEL = b'<nexe~~sentinel>'

def unpack_nexe(file):
    code_size, bundle_size = map(int, struct.unpack('<dd', file[-16:]))

    start = len(file) - code_size - bundle_size - len(NEXE_SENTINEL) - 16 # code, bundle, sentinel, lengths

    node, rest = slice(file, start)
    code, rest = slice(rest, code_size)
    bundle, rest = slice(rest, bundle_size)

    resources = re.search(rb"process\.__nexe = (.*);\n", code).group(1)
    resources = json.loads(resources)["resources"]

    return node, code, bundle, resources

def decompile_nexe(data: bytes):
    node, code, bundle, resources = unpack_nexe(data)

    files = {path: bundle[pos: pos + length] for path, (pos, length) in resources.items()} # unreadable one-liner, fuck you future me!

    return files

# pkg https://github.com/vercel/pkg

def unpack_pkg(data: bytes):
    payload_pos_m = re.search(rb"var PAYLOAD_POSITION = '(\d*).*'", data)
    payload_len_m = re.search(rb"var PAYLOAD_SIZE = '(\d*).*'", data)
    prelude_pos_m = re.search(rb"var PRELUDE_POSITION = '(\d*).*'", data)
    prelude_len_m = re.search(rb"var PRELUDE_SIZE = '(\d*).*'", data)

    payload_pos = int(payload_pos_m.group(1))
    payload_len = int(payload_len_m.group(1))
    prelude_pos = int(prelude_pos_m.group(1))
    prelude_len = int(prelude_len_m.group(1))

    payload = data[payload_pos: payload_pos + payload_len]
    prelude = data[prelude_pos: prelude_pos + prelude_len]

    prelude_data = re.search(rb"\/\/# sourceMappingURL=common\.js\.map\n\},\n(?P<virtfs>\{.*\})\n,\n(?P<entrypoint>.*)\n,\n(?P<symlinks>\{.*\})\n,\n(?P<_dict>\{.*\})\n,\n(?P<docompress>\d*)\n\);", prelude)

    virtfs, entrypoint, symlinks, _dict, docompress = (v.decode() for k, v in prelude_data.groupdict().items())

    virtfs = json.loads(virtfs)
    symlinks = json.loads(symlinks)
    _dict = json.loads(_dict)

    return payload, virtfs, entrypoint, symlinks, _dict, docompress

def decompile_pkg(data: bytes):
    payload, virtfs, entrypoint, symlinks, _dict, docompress = unpack_pkg(data)

    class StripeType(Enum):
        BLOB = '0' # v8 bytecode
        CONTENT = '1' # raw js
        LINKS = '2'
        STAT = '3'

    # TODO implement decompression
    class CompressType(Enum):
        NONE = '0'
        GZIP = '1'
        BROTLI = '2'

    files = {}

    for path, slices in virtfs.items():
        for typ, (pos, length) in slices.items():
            path = path.replace('C:\\snapshot\\', '')

            data = payload[pos:pos+length]

            if typ == StripeType.BLOB.value:
                path = path.replace('.js', '.jsc')
                files[path] = data

            elif typ == StripeType.CONTENT.value:
                files[path] = data

    return files

def decompile(fs):
    data = fs.read()

    # perhaps we make this dynamic in case some goofy goober
    # decides to add erroneous padding to the end of their file?
    if data[-32:-16] == NEXE_SENTINEL:
        return decompile_nexe(data)

    # pkg uses this to bootstrap node, so it should exist in all pkg binaries...
    elif re.search(rb'pkg/prelude/bootstrap.js', data):
        return decompile_pkg(data)

    else:
        raise TypeError("Could not decompile")


if __name__ == "__main__":
    source_path = Path(sys.argv[1])

    with open(source_path, 'rb') as fs:
        files = decompile(fs)

        basepath = Path(f'{source_path.name}_decompiled')

        for path, data in files.items():
            path = path.replace("..\\", "") \
                       .replace("../", "") \
                       .replace("\\", "/")
            path = PurePath(path)

            fullpath = basepath.joinpath(path)
            fullpath.parent.mkdir(parents=True, exist_ok=True)
            fullpath.write_bytes(data)

            print(f'Wrote "{fullpath}"')
