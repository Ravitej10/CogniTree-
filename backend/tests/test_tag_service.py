import unittest
import json
from unittest.mock import patch

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from core.database import Base
from core.models import ConceptTag, DocumentTagEvidence, Question, SourceDocument
import services.question_factory as question_factory
from services.tag_service import (
    link_document_evidence,
    normalize_tag_name,
    resolve_canonical_tag,
)


class CanonicalTagServiceTests(unittest.TestCase):
    def setUp(self):
        self.engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(self.engine)
        self.db = sessionmaker(bind=self.engine)()

    def tearDown(self):
        self.db.close()
        self.engine.dispose()

    def test_normalize_tag_name(self):
        self.assertEqual(normalize_tag_name("  Lexical--Analysis! "), "lexical analysis")

    def test_aliases_reuse_one_tag_across_two_documents(self):
        first_document = SourceDocument(filename="Dragon Book.pdf")
        second_document = SourceDocument(filename="Compiler Notes.pdf")
        self.db.add_all([first_document, second_document])
        self.db.flush()

        first_tag, first_method = resolve_canonical_tag(
            self.db,
            name="Lexical Analysis",
            definition="Converts source characters into tokens.",
            subject="Compiler Design",
        )
        second_tag, second_method = resolve_canonical_tag(
            self.db,
            name="Scanner",
            definition="Recognizes lexemes and emits tokens.",
            subject="Compiler Design",
        )
        link_document_evidence(
            self.db,
            document_id=first_document.id,
            tag_id=first_tag.id,
            chunk_index=3,
            source_excerpt="The lexical analyzer emits tokens.",
        )
        link_document_evidence(
            self.db,
            document_id=second_document.id,
            tag_id=second_tag.id,
            chunk_index=7,
            source_excerpt="The scanner recognizes lexemes.",
        )
        self.db.commit()

        self.assertEqual(first_method, "created")
        self.assertIn(second_method, {"exact", "alias"})
        self.assertEqual(first_tag.id, second_tag.id)
        self.assertEqual(self.db.query(ConceptTag).count(), 1)
        self.assertEqual(len(first_tag.evidence), 2)
        self.assertIn("scanner", {alias.normalized_alias for alias in first_tag.aliases})

    def test_generic_suffix_does_not_create_duplicate_tag(self):
        first, _ = resolve_canonical_tag(
            self.db,
            name="Lexical Analyzer Implementation",
            definition="Construction of a lexical analyzer.",
            subject="Compiler Design",
        )
        second, _ = resolve_canonical_tag(
            self.db,
            name="Lexical Analysis",
            definition="Conversion of characters into tokens.",
            subject="Compiler Design",
        )

        self.assertEqual(first.id, second.id)

    def test_generated_questions_store_canonical_tags_and_evidence(self):
        document = SourceDocument(id=1, filename="Compiler Design.pdf")
        self.db.add(document)
        self.db.commit()

        payload = []
        for group_index in range(2):
            for question_index in range(4):
                payload.append(
                    {
                        "topic": "Compiler Design",
                        "subtopic": ["Lexical Analysis", "Parsing"][group_index],
                        "skill_type": "memorization" if question_index < 2 else "application",
                        "question_text": f"Distinct question {group_index}-{question_index}?",
                        "options": ["A", "B", "C", "D"],
                        "answer_index": 0,
                        "explanation": "A grounded explanation.",
                    }
                )

        class FakeResponse:
            text = json.dumps(payload)

        class FakeModel:
            def generate_content(self, *args, **kwargs):
                return FakeResponse()

        original_model = question_factory._gemini_model
        question_factory._gemini_model = FakeModel()
        try:
            with patch(
                "services.vector_store.get_all_chunks_for_document",
                return_value=["Lexical source material", "Parsing source material"],
            ):
                questions = question_factory.generate_from_document_chunks(
                    self.db, document.id, count=8
                )
        finally:
            question_factory._gemini_model = original_model

        self.assertEqual(len(questions), 8)
        self.assertEqual(self.db.query(Question).filter(Question.tag_id.is_(None)).count(), 0)
        self.assertEqual(self.db.query(ConceptTag).count(), 2)
        self.assertEqual(self.db.query(DocumentTagEvidence).count(), 2)


if __name__ == "__main__":
    unittest.main()
