from pathlib import Path
import sys
import unittest

ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from validators import (
    validate_has_attr,
    validate_isinstance,
    validate_non_empty_path,
    validate_not_none,
    validate_positive_int,
)


class _SampleObj:
    def __init__(self) -> None:
        self.value = 42

    def run(self) -> str:
        return "ok"


class TestValidators(unittest.TestCase):
    """Unit tests for shared validation helpers in validators.py."""

    # --- validate_positive_int ---

    def test_validate_positive_int_returns_valid_int(self) -> None:
        self.assertEqual(validate_positive_int("word_length", 5), 5)
        self.assertEqual(validate_positive_int("max_guesses", 1), 1)

    def test_validate_positive_int_rejects_zero_negative_and_non_ints(self) -> None:
        invalid_values = [0, -1, -100, True, False, 3.5, "5", None, [1]]
        for bad in invalid_values:
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError) as ctx:
                    validate_positive_int("count", bad)  # type: ignore[arg-type]
                self.assertIn("count", str(ctx.exception))

    # --- validate_non_empty_path ---

    def test_validate_non_empty_path_returns_valid_path(self) -> None:
        path = Path("data/history.json")
        result = validate_non_empty_path("history_file", path)
        self.assertIs(result, path)

    def test_validate_non_empty_path_rejects_non_path(self) -> None:
        invalid_paths = ["data/history.json", "", None, 123]
        for bad in invalid_paths:
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError) as ctx:
                    validate_non_empty_path("secrets_file", bad)  # type: ignore[arg-type]
                self.assertIn("secrets_file", str(ctx.exception))

    # --- validate_not_none ---

    def test_validate_not_none_returns_value_including_falsy_non_none(self) -> None:
        for valid in [0, "", False, [], {}, "abc"]:
            with self.subTest(valid=valid):
                self.assertEqual(validate_not_none("field", valid), valid)

    def test_validate_not_none_raises_value_error_on_none(self) -> None:
        with self.assertRaises(ValueError) as ctx:
            validate_not_none("cfg", None)
        self.assertIn("cfg", str(ctx.exception))

    # --- validate_has_attr ---

    def test_validate_has_attr_returns_object_when_attribute_exists(self) -> None:
        obj = _SampleObj()
        self.assertIs(validate_has_attr("obj", obj, "value"), obj)
        self.assertIs(
            validate_has_attr("obj", obj, "run", callable_required=True),
            obj,
        )

    def test_validate_has_attr_raises_attribute_error_when_missing(self) -> None:
        obj = _SampleObj()
        with self.assertRaises(AttributeError) as ctx:
            validate_has_attr("obj", obj, "missing_attr")
        self.assertIn("obj", str(ctx.exception))
        self.assertIn("missing_attr", str(ctx.exception))

    def test_validate_has_attr_raises_type_error_when_callable_required_but_not_callable(self) -> None:
        obj = _SampleObj()
        with self.assertRaises(TypeError) as ctx:
            validate_has_attr("obj", obj, "value", callable_required=True)
        self.assertIn("obj.'value'", str(ctx.exception))

    # --- validate_isinstance ---

    def test_validate_isinstance_accepts_single_and_tuple_types(self) -> None:
        self.assertEqual(validate_isinstance("secret", "crane", str), "crane")
        self.assertEqual(validate_isinstance("num", 10, (int, float)), 10)
        self.assertEqual(validate_isinstance("num", 2.5, (int, float)), 2.5)

    def test_validate_isinstance_blocks_bool_by_default_and_allows_when_opted_in(self) -> None:
        with self.assertRaises(TypeError) as ctx:
            validate_isinstance("flag", True, int)
        self.assertIn("got bool", str(ctx.exception))

        self.assertIs(
            validate_isinstance("flag", True, int, allow_bool=True),
            True,
        )
        self.assertIs(
            validate_isinstance("flag", False, bool),
            False,
        )

    def test_validate_isinstance_raises_type_error_on_mismatch(self) -> None:
        with self.assertRaises(TypeError) as ctx:
            validate_isinstance("data", ["not", "a", "dict"], dict)
        self.assertIn("data", str(ctx.exception))
        self.assertIn("list", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()