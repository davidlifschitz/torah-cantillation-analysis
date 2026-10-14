# Local notebook-execution environment block

Date: 2026-10-14. This is a managed-runtime limitation, not a failure in the project notebook code.

## Reproduction

From the repository root:

```bash
uv run python scripts/notebooks.py --snapshot primary-20261013 --execute
```

The Jupyter kernel terminates before replying to `kernel_info` with `Operation not permitted (src/ip_resolver.cpp:542)`. The managed runtime also denies binding the small ZeroMQ probes `tcp://127.0.0.1:*` and `ipc:///tmp/...` with `Operation not permitted`.

## Impact and evidence

Local re-execution is blocked in this runtime. The repository's 11 committed notebooks each have executed code-cell counts and outputs, and the prior hosted [Research Pipeline run](https://github.com/davidlifschitz/torah-cantillation-analysis/actions/runs/38435753641) completed successfully. Restoring and reproducing the approved source snapshot, running the extended analysis, Ruff, compileall and pytest all succeeded locally.

No notebook or networking code change is indicated by this host-level restriction. If notebook code changes, re-execute the collection in a runner that supports local socket binding. See [issue #5](https://github.com/davidlifschitz/torah-cantillation-analysis/issues/5).
