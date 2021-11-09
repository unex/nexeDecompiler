import re
import sys
import json
import struct

from pathlib import PurePath, Path

SENTINEL = b'<nexe~~sentinel>'
RE_RESOURCES = re.compile(r"process\.__nexe = (.*);\n")

def slice(str, i):
    return str[:i], str[i:]

def decompile(fs):
    file = fs.read()

    # perhaps we make this dynamic in case some goofy goober
    # decides to add erroneous padding to the end of their file?
    sentinel_bytes = file[-32:-16]

    if sentinel_bytes != SENTINEL:
        raise TypeError('not a nexe binary') # is there a more fitting exception than this?

    code_size, bundle_size = map(int, struct.unpack('<dd', file[-16:]))

    start = len(file) - code_size - bundle_size - len(SENTINEL) - 16 # code, bundle, sentinel, lengths

    node, rest = slice(file, start)
    code, rest = slice(rest, code_size)
    bundle, rest = slice(rest, bundle_size)

    if _resources := RE_RESOURCES.findall(code.decode()):
        resources = json.loads(_resources[0])["resources"]

    files = {res[0]: bundle[res[1][0]: res[1][0] + res[1][1]] for res in resources.items()} # unreadable one-liner, fuck you future me!

    return files


if __name__ == "__main__":
    source_path = Path(sys.argv[1])

    with open(source_path, 'rb') as fs:
        files = decompile(fs)

        source = Path(source_path.name)

        for path, data in files.items():
            path = path.replace("..\\", "").replace("\\", "/")
            path = PurePath(path)

            fullpath = source.joinpath(path)
            fullpath.parent.mkdir(parents=True, exist_ok=True)

            with open(fullpath, "wb") as of:
                of.write(data)

            print(f'Wrote "{fullpath}"')
