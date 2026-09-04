# tinyparse setup

## Overview

tinyparse started in 2021 as an internal tool for reading the tiny
config format that our build scripts used. Over time it grew a
command-line interface and a small library, and in 2023 it was
published. It is worth noting that the tool has changed a lot since
then, and some older guides on the web describe options that no
longer exist. This guide covers the current release. To install it,
you need Node 20 or later, and you also need to decide where the
settings file will live, which depends on whether you run it per
project or globally, and the settings file format is described at the
end of this document.

## Details

Download the release archive from the releases page and extract it
into a directory on your PATH, then run `tinyparse init` to create the
config, then edit the config to point at your source directory, after
which you can run `tinyparse check` and it will print a summary and
exit with a nonzero code on any error. Supported platforms are:

- Windows 10 and later, x64, package `tinyparse-win-x64.zip`
- macOS 13 and later, arm64, package `tinyparse-darwin-arm64.tar.gz`
- macOS 13 and later, x64, package `tinyparse-darwin-x64.tar.gz`
- Linux, glibc 2.31 and later, x64, package `tinyparse-linux-x64.tar.gz`

The config uses the same tiny format that tinyparse itself parses, so
a syntax error in it is reported the same way as in a source file (see
above). If the settings file is missing, tinyparse looks for one in
the home directory, and if that is also missing it uses defaults,
which are listed below.

## Notes

The defaults are: source directory `.`, output `stdout`, strict mode
off. Strict mode makes unknown keys an error rather than a warning.
This is the option most people want in CI, as mentioned earlier, and
it can also be set with the `--strict` flag, which overrides the
settings file.

If you want to use tinyparse from a script, the exit codes are 0 for
success, 1 for a parse error and 2 for a usage error. The library API
is documented separately.
