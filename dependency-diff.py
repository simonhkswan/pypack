#! /usr/bin/env python
import argparse
import pathlib
import subprocess
from typing import List, Union


def subprocess_command(cmd: List[str]):
    out: Union[str, bytes] = subprocess.check_output(cmd)

    if not isinstance(out, str):
        out = out.decode("utf-8")
    return out.strip()


def deps_to_dicts(deps):
    pairs = [dep.strip().split("==") for n, dep in enumerate(deps.split("\n"))]
    pairs = [p for p in pairs if len(p) == 2]
    version_dict = {name: ver for name, ver in pairs}
    line_no = {name: n for n, (name, ver) in enumerate(pairs)}
    return version_dict, line_no


def gh_action_warning(file, title, message, line, endline, col, endcol):
    print(
        f"::warning file={file},line={line},endLine={endline},col={col},"
        f"endColumn={endcol},title={title}::{message}"
    )


if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Update the version of the file given.")
    parser.add_argument(
        "file_path",
        metavar="file",
        type=pathlib.Path,
        help="The path to the requirements.txt file.",
    )
    args = parser.parse_args()
    file_path = args.file_path

    new_deps = subprocess_command(["cat", f"{file_path.as_posix()}"])
    old_deps = subprocess_command(["git", "show", f"HEAD:{file_path.as_posix()}"])

    new_vers, new_lines = deps_to_dicts(new_deps)
    old_vers, old_lines = deps_to_dicts(old_deps)

    removed = []
    added = []
    updated = []
    for pkg in old_vers:
        if pkg not in new_vers:
            removed.append(pkg)
        elif old_vers[pkg] != new_vers[pkg]:
            print(pkg, old_vers[pkg], repr(old_vers[pkg]), new_vers[pkg], repr(new_vers[pkg]))
            updated.append(pkg)
    for pkg in new_vers:
        if pkg not in old_vers:
            added.append(pkg)

    print(old_deps)
    print(repr(old_deps))
    print(old_vers, old_lines)
    print("---")
    print(new_deps)
    print(repr(new_deps))
    print(old_vers, old_lines)
    print("---")
    print(removed)
    print(added)
    print(updated)
    for pkg in updated:
        file = file_path.as_posix()
        title = "Update Requirement"
        message = f"Dependency `{pkg}` should be updated from {old_vers[pkg]} to {new_vers[pkg]}."
        line = old_lines[pkg] + 1
        endline = line
        col = len(pkg) + 3
        endcol = col + len(old_vers[pkg])
        gh_action_warning(
            file=file,
            title=title,
            message=message,
            line=line,
            endline=endline,
            col=col,
            endcol=endcol,
        )
    for pkg in removed:
        file = file_path.as_posix()
        title = "Remove Requirement"
        message = f"Dependency `{pkg}` should be removed from requirements."
        line = old_lines[pkg] + 1
        endline = line
        col = 1
        endcol = len(pkg) + 3 + len(old_vers[pkg])
        gh_action_warning(
            file=file,
            title=title,
            message=message,
            line=line,
            endline=endline,
            col=col,
            endcol=endcol,
        )

    for pkg in removed:
        file = file_path.as_posix()
        title = "Add Requirement"
        message = f"Dependency `{pkg}=={new_vers[pkg]}` should be added to requirements."
        line = 1
        endline = line
        col = 1
        endcol = 1
        gh_action_warning(
            file=file,
            title=title,
            message=message,
            line=line,
            endline=endline,
            col=col,
            endcol=endcol,
        )
