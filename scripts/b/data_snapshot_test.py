import unittest
from unittest.mock import patch

import b
import data_snapshot


class FakeContext:
    def __init__(self):
        self.calls = []

    def invoke(self, command, *args, **kwargs):
        self.calls.append((command.name, kwargs))
        return None


class FakeRedisServer:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False


class DataSnapshotRunTest(unittest.TestCase):
    def _run_command(self, command):
        ctx = FakeContext()
        with patch.object(data_snapshot.subprocess, "run") as subprocess_run:
            with patch.object(
                data_snapshot, "RedisServer", return_value=FakeRedisServer()
            ):
                command.callback.__wrapped__(ctx, False)
        return ctx, subprocess_run

    def test_run_requires_complete_assets(self):
        ctx, subprocess_run = self._run_command(data_snapshot.run)

        subprocess_run.assert_called_once_with(
            ["git", "lfs", "pull"], cwd=data_snapshot.REPO_DIR, check=True
        )
        self.assertIn(
            ("check-for-missing-assets", {"error_on_missing": True}),
            ctx.calls,
        )
        self.assertIn(
            (
                "run",
                {
                    "target": ["web"],
                    "redis": True,
                    "storage": "memory",
                    "assets": "local",
                    "open_admin_access": True,
                    "bikkie_static_prefix": data_snapshot.BIKKIE_STATIC_PREFIX,
                    "galois_static_prefix": data_snapshot.GALOIS_STATIC_PREFIX,
                    "local_gcs": True,
                },
            ),
            ctx.calls,
        )

    def test_run_minimal_command_is_registered(self):
        self.assertIn("run-minimal", b.data_snapshot_commands.commands)

    def test_run_minimal_allows_missing_assets(self):
        ctx, _ = self._run_command(data_snapshot.run_minimal)

        self.assertIn(
            ("check-for-missing-assets", {"error_on_missing": False}),
            ctx.calls,
        )
        self.assertNotIn(
            ("check-for-missing-assets", {"error_on_missing": True}),
            ctx.calls,
        )


if __name__ == "__main__":
    unittest.main()
