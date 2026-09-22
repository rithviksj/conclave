#!/usr/bin/env python3
"""Unit tests for skills/counsel/quotecheck.py. Run: python3 tests/test_quotecheck.py"""
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "skills", "counsel"))
from quotecheck import check  # noqa: E402

A = "Adopting it doubles the on-call load for a team of three.\nAlso the vendor is new."
B = "Rolling back is one config flag, so the risk is small.\nThe cost is flat."


class QuoteCheck(unittest.TestCase):
    def test_valid_quotes_pass(self):
        d = "> [A] doubles the on-call load for a team of three\n> [B] Rolling back is one config flag"
        self.assertEqual(check(d, {"A": A, "B": B})[1], 0)

    def test_stitched_across_members_fails(self):
        # the tail of A's text plus the head of B's text, attributed to either member
        d = "> [A] the vendor is new. Rolling back is one config flag\n> [B] Rolling back is one config flag"
        self.assertEqual(check(d, {"A": A, "B": B})[1], 1)

    def test_misattributed_quote_fails(self):
        d = "> [A] Rolling back is one config flag\n> [B] Rolling back is one config flag"
        self.assertGreaterEqual(check(d, {"A": A, "B": B})[1], 1)

    def test_member_never_quoted_fails(self):
        d = "> [A] doubles the on-call load for a team of three"
        lines, bad = check(d, {"A": A, "B": B})
        self.assertEqual(bad, 1)
        self.assertIn("never quoted", lines[-1])

    def test_stray_quote_marks_in_prose_do_not_fail(self):
        d = 'The chair says "this is only prose, not a quote at all" here.\n' \
            "> [A] doubles the on-call load for a team of three\n> [B] the risk is small"
        self.assertEqual(check(d, {"A": A, "B": B})[1], 0)

    def test_curly_quotes_and_whitespace_normalised(self):
        members = {"A": "It “just works”   in  staging only.", "B": B}
        d = '> [A] It "just works" in staging only.\n> [B] The cost is flat.'
        self.assertEqual(check(d, members)[1], 0)

    def test_unknown_tag_and_short_quote_fail(self):
        d = "> [C] doubles the on-call load\n> [A] team\n> [B] the risk is small"
        self.assertGreaterEqual(check(d, {"A": A, "B": B})[1], 2)

    def test_no_quotes_fails(self):
        self.assertEqual(check("no quotes here", {"A": A})[1], 1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
