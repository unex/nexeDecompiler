import argparse

from pathlib import Path

from .core import NexeDecompiler


parser = argparse.ArgumentParser()
parser.add_argument("source", help="source file path", type=str)
parser.add_argument(
    "--dest", help="destination directory, default is cwd", type=str, default=None
)


def path_sub(path: str) -> str:
    return path.replace("\\", "/").replace("../", "")


def cli():
    args = parser.parse_args()

    source = Path(args.source)

    if args.dest:
        dest = Path(args.dest).resolve()
    else:
        dest = Path.cwd().joinpath(f"{source.name}_decompiled")

    if not source.exists():
        print(f'"{source}" does not exist')
        return

    if not source.is_file():
        print(f"Source must be a file")
        return

    with source.open("rb") as fp:
        decomp = NexeDecompiler.from_file(fp).decompile()

        dest.mkdir(parents=True, exist_ok=True)

        print(f"Writing {len(decomp.files)} files to {dest}")

        for path, data in decomp.files.items():
            path = path_sub(path)

            filepath = dest.joinpath(path)
            filepath.parent.mkdir(parents=True, exist_ok=True)
            filepath.write_bytes(data)

        entrypoint = dest.joinpath(path_sub(decomp.entrypoint))

        print(f"Entrypoint located at {entrypoint}")
