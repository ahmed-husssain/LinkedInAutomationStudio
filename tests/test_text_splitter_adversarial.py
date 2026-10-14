"""
Adversarial Tests for Text Splitter Engine.
Stress-tests boundary conditions, malformed input, nulls, emojis, and degenerate lengths.
"""

import pytest
from src.engines.text_splitter import split_text_for_option


class TestTextSplitterAdversarial:
    def test_null_and_empty_inputs(self):
        """Should handle None, empty strings, and whitespace without crashing."""
        assert split_text_for_option(None) == ("", None)
        assert split_text_for_option("") == ("", None)
        assert split_text_for_option("   ") == ("", None)
        assert split_text_for_option("\n\t  \r\n") == ("", None)

    def test_single_ultra_long_word_no_spaces(self):
        """Single unbroken 250-character word should not enter infinite loops or crash."""
        long_word = "A" * 250
        l1, l2 = split_text_for_option(long_word, max_line1=38, max_line2=95)
        assert len(l1) == 38
        assert l2 is not None
        assert len(l2) <= 95
        assert l1 == "A" * 38

    def test_multibyte_utf8_and_complex_emojis(self):
        """Complex emojis, ZWJ sequences, and foreign characters."""
        text = "🚀 Cloud Architecture 👨‍👩‍👧‍👦 Scalability in Tokyo 東京 and Berlin 🇩🇪"
        l1, l2 = split_text_for_option(text, max_line1=38, max_line2=95)
        assert len(l1) <= 38
        assert l2 is not None
        assert "Cloud" in l1

    def test_degenerate_boundary_parameters(self):
        """Zero or negative limits must fallback to safe defaults without crashing."""
        sample = "How OAuth 2.0 Works in modern microservice applications"
        l1, l2 = split_text_for_option(sample, max_line1=0, max_line2=0)
        assert len(l1) <= 38
        assert l2 is not None

        l1_neg, l2_neg = split_text_for_option(sample, max_line1=-10, max_line2=-50)
        assert len(l1_neg) <= 38

    def test_exact_boundary_conditions(self):
        """Tests exact line lengths at 38 chars, 39 chars, and edge boundaries."""
        # Exactly 38 chars
        exact_38 = "1234567890 1234567890 1234567890 12345"
        assert len(exact_38) == 38
        l1, l2 = split_text_for_option(exact_38, max_line1=38, max_line2=95)
        assert l1 == exact_38
        assert l2 is None

        # 39 chars (1 char overflow)
        overflow_39 = exact_38 + "X"
        l1_over, l2_over = split_text_for_option(overflow_39, max_line1=38, max_line2=95)
        assert len(l1_over) <= 38
        assert l2_over is not None

    def test_zero_truncation_on_natural_sentence(self):
        """Verifies that words are never split across word boundaries."""
        sentence = "In SPAs or Mobile Apps, do you use PKCE directly or a BFF (Backend-for-Frontend) architecture?"
        l1, l2 = split_text_for_option(sentence, max_line1=38, max_line2=95)
        # Verify line 1 does not cut a word mid-letters
        last_word_l1 = l1.split()[-1]
        assert last_word_l1 in sentence
        # Combined lines should contain all words
        combined = f"{l1} {l2}"
        for word in ["SPAs", "Mobile", "Apps", "PKCE"]:
            assert word in combined
