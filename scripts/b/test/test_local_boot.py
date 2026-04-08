import os
import sys
import unittest
from pathlib import Path
from unittest import mock

SCRIPT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SCRIPT_DIR))

import b
import pip_install_voxeloo


class LauncherAliasTests(unittest.TestCase):
    def test_dev_alias_uses_gaia_service_name(self):
        expanded = b.expand_targets(["dev"])
        self.assertIn("gaia", expanded)
        self.assertNotIn("gaia_v2", expanded)

    def test_legacy_gaia_v2_alias_maps_to_gaia(self):
        self.assertEqual(b.expand_targets(["gaia_v2"]), ["gaia"])

    def test_local_alias_matches_supported_local_services(self):
        self.assertEqual(
            set(b.expand_targets(["local"])),
            {"logic", "chat", "map", "gaia", "web", "trigger", "task"},
        )


class PythonExecutableTests(unittest.TestCase):
    def test_prefers_explicit_python_override(self):
        with mock.patch.dict(os.environ, {"PYTHON": "/tmp/custom-python"}):
            self.assertEqual(
                pip_install_voxeloo.python_executable(), "/tmp/custom-python"
            )

    def test_defaults_to_current_interpreter(self):
        with mock.patch.dict(os.environ, {}, clear=True):
            self.assertEqual(
                pip_install_voxeloo.python_executable(), sys.executable
            )


if __name__ == "__main__":
    unittest.main()
