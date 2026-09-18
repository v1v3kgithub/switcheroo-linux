"""Unit tests for Switcheroo matchers, matching original C# NUnit tests."""

import unittest
from switcheroo.core.matchers import (
    ContainsMatcher,
    IndividualCharactersMatcher,
    SignificantCharactersMatcher,
    StartsWithMatcher,
)


class TestStartsWithMatcher(unittest.TestCase):
    def setUp(self):
        self.matcher = StartsWithMatcher()

    def test_input_none_returns_non_match(self):
        res = self.matcher.evaluate(None, "google")
        self.assertFalse(res.matched)
        self.assertEqual(len(res.string_parts), 0)

    def test_pattern_none_returns_non_match(self):
        res = self.matcher.evaluate("google chrome", None)
        self.assertFalse(res.matched)
        self.assertEqual(len(res.string_parts), 1)
        self.assertEqual(res.string_parts[0].value, "google chrome")

    def test_input_starts_with_pattern_score_is_four(self):
        res = self.matcher.evaluate("Google Chrome", "goo")
        self.assertTrue(res.matched)
        self.assertEqual(res.score, 4)
        self.assertEqual(len(res.string_parts), 2)
        self.assertEqual(res.string_parts[0].value, "Goo")
        self.assertTrue(res.string_parts[0].is_match)
        self.assertEqual(res.string_parts[1].value, "gle Chrome")
        self.assertFalse(res.string_parts[1].is_match)

    def test_input_does_not_start_with_pattern(self):
        res = self.matcher.evaluate("Google Chrome", "chrome")
        self.assertFalse(res.matched)
        self.assertEqual(res.score, 0)


class TestContainsMatcher(unittest.TestCase):
    def setUp(self):
        self.matcher = ContainsMatcher()

    def test_input_none_returns_non_match(self):
        res = self.matcher.evaluate(None, "google")
        self.assertFalse(res.matched)

    def test_pattern_none_returns_non_match(self):
        res = self.matcher.evaluate("google chrome", None)
        self.assertFalse(res.matched)

    def test_does_not_contain_score_zero(self):
        res = self.matcher.evaluate("google", "chrome")
        self.assertFalse(res.matched)
        self.assertEqual(res.score, 0)

    def test_contains_score_two(self):
        res = self.matcher.evaluate("google chrome", "chrome")
        self.assertTrue(res.matched)
        self.assertEqual(res.score, 2)
        self.assertEqual(len(res.string_parts), 2)
        self.assertEqual(res.string_parts[0].value, "google ")
        self.assertFalse(res.string_parts[0].is_match)
        self.assertEqual(res.string_parts[1].value, "chrome")
        self.assertTrue(res.string_parts[1].is_match)

    def test_contains_in_middle(self):
        res = self.matcher.evaluate("google chrome v28", "chrome")
        self.assertTrue(res.matched)
        self.assertEqual(len(res.string_parts), 3)
        self.assertEqual(res.string_parts[0].value, "google ")
        self.assertEqual(res.string_parts[1].value, "chrome")
        self.assertTrue(res.string_parts[1].is_match)
        self.assertEqual(res.string_parts[2].value, " v28")
        self.assertFalse(res.string_parts[2].is_match)


class TestSignificantCharactersMatcher(unittest.TestCase):
    def setUp(self):
        self.matcher = SignificantCharactersMatcher()

    def test_word_boundaries(self):
        res = self.matcher.evaluate("Google Chrome", "gc")
        self.assertTrue(res.matched)
        self.assertEqual(res.score, 2)
        # Matches 'G' and 'C'
        matched_chars = "".join(p.value for p in res.string_parts if p.is_match)
        self.assertEqual(matched_chars.lower(), "gc")

    def test_acronym_multi_word(self):
        res = self.matcher.evaluate("Visual Studio Code", "vsc")
        self.assertTrue(res.matched)
        matched_chars = "".join(p.value for p in res.string_parts if p.is_match)
        self.assertEqual(matched_chars.lower(), "vsc")

    def test_camel_case(self):
        res = self.matcher.evaluate("camelCaseString", "ccs")
        self.assertTrue(res.matched)
        matched_chars = "".join(p.value for p in res.string_parts if p.is_match)
        self.assertEqual(matched_chars.lower(), "ccs")


class TestIndividualCharactersMatcher(unittest.TestCase):
    def setUp(self):
        self.matcher = IndividualCharactersMatcher()

    def test_single_character(self):
        res = self.matcher.evaluate("chrome", "r")
        self.assertTrue(res.matched)
        self.assertEqual(res.score, 1)
        self.assertEqual(len(res.string_parts), 3)
        self.assertEqual(res.string_parts[0].value, "ch")
        self.assertFalse(res.string_parts[0].is_match)
        self.assertEqual(res.string_parts[1].value, "r")
        self.assertTrue(res.string_parts[1].is_match)
        self.assertEqual(res.string_parts[2].value, "ome")
        self.assertFalse(res.string_parts[2].is_match)

    def test_subsequence(self):
        res = self.matcher.evaluate("chrome", "re")
        self.assertTrue(res.matched)
        self.assertEqual(len(res.string_parts), 4)
        self.assertEqual(res.string_parts[0].value, "ch")
        self.assertEqual(res.string_parts[1].value, "r")
        self.assertTrue(res.string_parts[1].is_match)
        self.assertEqual(res.string_parts[2].value, "om")
        self.assertEqual(res.string_parts[3].value, "e")
        self.assertTrue(res.string_parts[3].is_match)


if __name__ == "__main__":
    unittest.main()
