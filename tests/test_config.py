from dataclasses import FrozenInstanceError
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import config as config_module


class TestConfig(unittest.TestCase):
    """Unit tests for the Config dataclass, factory loading, immutability, and validation."""

    def setUp(self) -> None:
        """Create temporary files and a baseline valid environment mapping for each test."""
        self.tmp_dir = tempfile.TemporaryDirectory()
        self.base = Path(self.tmp_dir.name)
        self.secrets_path = self.base / "secrets.txt"
        self.history_path = self.base / "history.json"
        self.secrets_path.write_text("snail\napple\n", encoding="utf-8")

        self.valid_env = {
            "SECRETS_FILE": str(self.secrets_path),
            "WORD_LENGTH": "5",
            "WORD_COUNT": "2",
            "MAX_GUESSES": "6",
            "HISTORY_FILE": str(self.history_path),
        }

    def tearDown(self) -> None:
        """Clean up temporary files and directories created during setUp."""
        self.tmp_dir.cleanup()

    def test_module_config_exists_and_is_config_instance(self):
        """Verify that config_module exposes a module-level Config instance."""
        self.assertTrue(hasattr(config_module, "config"))
        self.assertIsInstance(config_module.config, config_module.Config)

    def test_from_env_with_real_values(self):
        """Verify Config.from_env() parses paths and integers accurately from environment variables."""
        with patch.dict(os.environ, self.valid_env, clear=False):
            cfg = config_module.Config.from_env()

        self.assertIsInstance(cfg, config_module.Config)
        self.assertEqual(cfg.secrets_file, self.secrets_path)
        self.assertEqual(cfg.history_file, self.history_path)
        self.assertEqual(cfg.word_length, 5)
        self.assertEqual(cfg.word_count, 2)
        self.assertEqual(cfg.max_guesses, 6)

    def test_config_is_frozen(self):
        """Verify attributes on a Config instance cannot be mutated after creation."""
        with patch.dict(os.environ, self.valid_env, clear=False):
            cfg = config_module.Config.from_env()

        with self.assertRaises((FrozenInstanceError, AttributeError)):
            cfg.word_length = 7  # type: ignore[misc]

    def test_invalid_integer_raises_runtime_error_on_load_config(self):
        """Verify load_config() wraps non-numeric integer environment values in a RuntimeError."""
        bad_env = {**self.valid_env, "WORD_LENGTH": "not_a_number"}
        with patch.dict(os.environ, bad_env, clear=False):
            with self.assertRaises(RuntimeError) as ctx:
                config_module.load_config()

        self.assertIn("WORD_LENGTH", str(ctx.exception))

    def test_non_positive_int_rejected_by_validator(self):
        """Verify values less than or equal to zero are rejected during config validation."""
        bad_env = {**self.valid_env, "MAX_GUESSES": "0"}
        with patch.dict(os.environ, bad_env, clear=False):
            with self.assertRaises(RuntimeError):
                config_module.load_config()

    def test_missing_env_var_rejected(self):
        """Verify missing required environment variables raise RuntimeError with the variable name."""
        env_without_secret = {
            k: v for k, v in self.valid_env.items() if k != "SECRETS_FILE"
        }
        # clear=True isolates os.environ for this test so a real .env/shell var doesn't leak in
        with patch.dict(os.environ, env_without_secret, clear=True):
            with self.assertRaises(RuntimeError) as ctx:
                config_module.load_config()

        self.assertIn("SECRETS_FILE", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()