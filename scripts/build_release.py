#!/usr/bin/env python3
"""Build tenet release assets (stdlib only, no network).

Produces in --out (default: dist/):
  tenet-plugin-<version>.zip  plugin directory contents, loadable with `claude --plugin-dir <zip>`
  tenet-<version>.zip         every git-tracked file under a tenet-<version>/ prefix (installers included)
  checksums.txt               SHA-256 of each zip

Zips are deterministic: sorted entries, fixed timestamps and permissions, so the same tree gives the
same checksums locally and in CI.

Usage:
  python scripts/build_release.py [--out DIR] [--tag tenet--v<version>]
  python scripts/build_release.py --print-version | --print-prerelease
"""
import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import zipfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLUGIN_REL = "plugins/tenet"
TAG_PREFIX = "tenet--v"
FIXED_DATE = (1980, 1, 1, 0, 0, 0)


def plugin_version(root=ROOT):
    with open(os.path.join(root, PLUGIN_REL, ".claude-plugin", "plugin.json"), encoding="utf-8") as handle:
        return json.load(handle)["version"]


def is_prerelease(version):
    """Semver pre-release: anything after a '-' in the core version (build metadata after '+' ignored)."""
    return "-" in version.split("+", 1)[0]


def tracked_files(root=ROOT):
    out = subprocess.run(["git", "ls-files", "-z"], cwd=root, capture_output=True, check=True).stdout.decode("utf-8")
    return sorted(f for f in out.split("\0") if f and os.path.isfile(os.path.join(root, f)))


def write_zip(path, entries):
    """entries: list of (archive_name, source_path); written in sorted order with fixed metadata."""
    with zipfile.ZipFile(path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        for name, source in sorted(entries):
            info = zipfile.ZipInfo(name, date_time=FIXED_DATE)
            info.compress_type = zipfile.ZIP_DEFLATED
            executable = source.endswith(".sh")
            info.external_attr = ((0o100755 if executable else 0o100644) & 0xFFFF) << 16
            with open(source, "rb") as handle:
                data = handle.read()
            if not source.endswith((".png", ".zip", ".jpg", ".gif")):
                data = data.replace(b"\r\n", b"\n")  # match git's normalized content on every OS
            archive.writestr(info, data)


def sha256(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build(out_dir, root=ROOT, tag=None):
    version = plugin_version(root)
    if tag is not None and tag != TAG_PREFIX + version:
        raise SystemExit("error: tag %s does not match plugin.json version %s (expected %s%s)" % (tag, version, TAG_PREFIX, version))
    notes = os.path.join(root, "docs", "releases", "v%s.md" % version)
    if not os.path.isfile(notes):
        raise SystemExit("error: missing release notes %s" % os.path.relpath(notes, root))
    files = tracked_files(root)
    plugin_entries = [(f[len(PLUGIN_REL) + 1:], os.path.join(root, f)) for f in files if f.startswith(PLUGIN_REL + "/")]
    if not any(name == ".claude-plugin/plugin.json" for name, _ in plugin_entries):
        raise SystemExit("error: plugin manifest is not tracked by git")
    full_entries = [("tenet-%s/%s" % (version, f), os.path.join(root, f)) for f in files]
    os.makedirs(out_dir, exist_ok=True)
    assets = ["tenet-plugin-%s.zip" % version, "tenet-%s.zip" % version]
    write_zip(os.path.join(out_dir, assets[0]), plugin_entries)
    write_zip(os.path.join(out_dir, assets[1]), full_entries)
    with open(os.path.join(out_dir, "checksums.txt"), "w", encoding="utf-8", newline="\n") as handle:
        for name in assets:
            handle.write("%s  %s\n" % (sha256(os.path.join(out_dir, name)), name))
    return version, assets


def main(argv=None):
    parser = argparse.ArgumentParser(description="Build tenet release assets.")
    parser.add_argument("--out", default=os.path.join(ROOT, "dist"))
    parser.add_argument("--tag", help="release tag to check against plugin.json (tenet--v<version>)")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--print-version", action="store_true")
    group.add_argument("--print-prerelease", action="store_true", help="print true/false for the current version")
    args = parser.parse_args(argv)
    if args.print_version:
        print(plugin_version())
        return 0
    if args.print_prerelease:
        print("true" if is_prerelease(plugin_version()) else "false")
        return 0
    if args.tag is not None and not re.match(r"^%s\d" % re.escape(TAG_PREFIX), args.tag):
        raise SystemExit("error: tag must look like %s<version>" % TAG_PREFIX)
    version, assets = build(args.out, tag=args.tag)
    print("built tenet %s (%s):" % (version, "pre-release" if is_prerelease(version) else "release"))
    for name in assets + ["checksums.txt"]:
        print("  " + os.path.join(args.out, name))
    return 0


if __name__ == "__main__":
    sys.exit(main())
