#!/usr/bin/env python3
import json
import os
import sys


def read_text(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read().strip()
    except OSError:
        return ""


def find_prefix_value(root, dirpath, suffix, dockerfile_path):
    candidates = [
        f"{dockerfile_path}.prefix",
        os.path.join(dirpath, f"{suffix}.prefix"),
        os.path.join(dirpath, f"prefix.{suffix}"),
        os.path.join(dirpath, f"prefix-{suffix}"),
        os.path.join(dirpath, "prefix"),
        os.path.join(dirpath, "PREFIX"),
        os.path.join(dirpath, ".prefix"),
    ]
    for path in candidates:
        if os.path.isfile(path):
            value = read_text(path)
            if value:
                return value

    root_candidates = [
        os.path.join(root, "prefix"),
        os.path.join(root, "PREFIX"),
        os.path.join(root, ".prefix"),
    ]
    for path in root_candidates:
        if os.path.isfile(path):
            value = read_text(path)
            if value:
                return value

    return ""


def infer_suffix(root, dirpath, filename):
    if filename == "Dockerfile":
        rel = os.path.relpath(dirpath, root)
        if rel == ".":
            return "default"
        return os.path.basename(dirpath)
    if filename.startswith("Dockerfile."):
        return filename[len("Dockerfile.") :]
    if filename.startswith("Dockerfile-"):
        return filename[len("Dockerfile-") :]
    tail = filename.replace("Dockerfile", "").lstrip(".-")
    return tail or "default"


def discover_root_only(root):
    dockerfiles = []
    for filename in os.listdir(root):
        path = os.path.join(root, filename)
        if not os.path.isfile(path):
            continue
        if filename == "Dockerfile" or filename.startswith("Dockerfile."):
            dockerfiles.append(path)
        elif filename.startswith("Dockerfile-"):
            dockerfiles.append(path)
    return dockerfiles


def discover_all(root):
    dockerfiles = []
    for dirpath, dirnames, filenames in os.walk(root):
        if ".git" in dirnames:
            dirnames.remove(".git")
        for filename in filenames:
            if filename == "Dockerfile" or filename.startswith("Dockerfile."):
                dockerfiles.append(os.path.join(dirpath, filename))
            elif filename.startswith("Dockerfile-"):
                dockerfiles.append(os.path.join(dirpath, filename))
    return dockerfiles


def main():
    if len(sys.argv) < 2:
        print("Usage: discover_targets.py <repo_root>", file=sys.stderr)
        return 1

    root = sys.argv[1].rstrip("/")
    if not os.path.isdir(root):
        print(f"Repo root not found: {root}", file=sys.stderr)
        return 1

    default_prefix = os.environ.get("IMAGE_PREFIX_DEFAULT", "moltbot").strip()
    scan_mode = os.environ.get("DOCKERFILE_SCAN", "root").strip().lower()
    if scan_mode == "all":
        dockerfiles = discover_all(root)
    else:
        dockerfiles = discover_root_only(root)

    targets = []
    for dockerfile in sorted(dockerfiles):
        dirpath = os.path.dirname(dockerfile)
        filename = os.path.basename(dockerfile)
        suffix = infer_suffix(root, dirpath, filename)
        prefix_value = find_prefix_value(root, dirpath, suffix, dockerfile) or default_prefix

        if suffix == "default":
            image = prefix_value
        else:
            if prefix_value.endswith("-"):
                image = f"{prefix_value}{suffix}"
            else:
                image = f"{prefix_value}-{suffix}"

        targets.append(
            {
                "name": suffix,
                "context": root,
                "dockerfile": dockerfile,
                "image": image,
            }
        )

    if not targets:
        print("No Dockerfile targets found.", file=sys.stderr)
        return 1

    print(json.dumps({"include": targets}, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
