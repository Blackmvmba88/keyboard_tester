from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from blackmamba_type.learning import PersonalLexicon, extract_words
from blackmamba_type.predictor import PrefixPredictor


class LearningTests(unittest.TestCase):
    def test_extract_words_normalizes_unicode_and_skips_numbers(self) -> None:
        text = "Wey, programación rápida xD abc123 música-motor"
        self.assertEqual(
            extract_words(text),
            ["wey", "programación", "rápida", "xd", "música-motor"],
        )

    def test_personal_lexicon_persists_frequency(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "lexicon.json"
            lexicon = PersonalLexicon(path)
            lexicon.import_text("wey wey bro música")
            self.assertEqual(lexicon.frequency("WEY"), 2)
            self.assertEqual(lexicon.unique_words(), 3)

            reloaded = PersonalLexicon(path)
            self.assertEqual(reloaded.frequency("wey"), 2)
            self.assertEqual(reloaded.suggest("we", limit=3)[0][0], "wey")

    def test_predictor_uses_personal_frequency(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            lexicon = PersonalLexicon(Path(tmp) / "lexicon.json")
            lexicon.import_text("wey wey wey weapon weapon")
            predictor = PrefixPredictor(terms=[], lexicon=lexicon)

            self.assertEqual(predictor.suggest("we", limit=2), ["wey", "weapon"])


if __name__ == "__main__":
    unittest.main()
