#!/usr/bin/env bash
# Stand-in for the full suite: the firing tests only need the launch, not the load.
echo "compiling 48 modules on $(nproc 2>/dev/null || echo "$NUMBER_OF_PROCESSORS") cores"
sleep 2
echo "1204 passed, 0 failed"
