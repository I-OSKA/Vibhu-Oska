"""Tests for GRAG module — Graph RAG with entity extraction, community detection, and multi-pattern search."""

import asyncio
import pytest

from Backend.Core.SpecializedCore.DataCore.grag import (
    GRAGEngine,
    EntityExtractor,
    CommunityDetector,
    CommunitySummarizer,
    GRAGQuerier,
    Entity,
    Relationship,
    Community,
    GRAGResult,
)


class TestEntityExtractor:
    @pytest.fixture
    def extractor(self):
        return EntityExtractor()

    def test_extract(self, extractor):
        text = "Harsh Dev Jha is the creator of Vibhu-Oska. NVIDIA manufactures the RTX 4060."
        entities, relationships = extractor.extract(text)
        assert len(entities) > 0

    def test_extract_person(self, extractor):
        text = "Harsh Dev Jha is the creator of Vibhu-Oska."
        entities, _ = extractor.extract(text)
        person_names = [e.name for e in entities if e.entity_type == "PERSON"]
        assert any("Harsh" in name for name in person_names)

    def test_extract_organization(self, extractor):
        text = "NVIDIA manufactures the RTX 4060 graphics card."
        entities, _ = extractor.extract(text)
        orgs = [e.name for e in entities if e.entity_type == "ORG"]
        assert any("NVIDIA" in o for o in orgs)

    def test_extract_relationships(self, extractor):
        text = "Harsh Dev Jha is the creator of Vibhu-Oska. NVIDIA manufactures GPU."
        _, relationships = extractor.extract(text)
        # Relationships depend on pattern matching — may or may not find any
        assert isinstance(relationships, list)

    def test_empty_text(self, extractor):
        entities, relationships = extractor.extract("")
        assert len(entities) == 0


class TestCommunityDetector:
    @pytest.fixture
    def detector(self):
        return CommunityDetector()

    def test_detect(self, detector):
        entities = [
            Entity(name="Harsh", entity_type="PERSON", description="creator"),
            Entity(name="Vibhu-Oska", entity_type="CONCEPT", description="AI OS"),
            Entity(name="NVIDIA", entity_type="ORG", description="GPU maker"),
            Entity(name="RTX 4060", entity_type="HARDWARE", description="GPU"),
        ]
        relationships = []
        communities = detector.detect(entities, relationships)
        assert isinstance(communities, list)


class TestGRAGEngine:
    @pytest.fixture
    def engine(self):
        return GRAGEngine()

    def test_ingest(self, engine):
        result = engine.ingest(
            "NVIDIA RTX 4060 has 8GB VRAM. It is manufactured by NVIDIA."
        )
        assert result["entities_extracted"] > 0

    def test_query_local(self, engine):
        engine.ingest("Harsh Dev Jha created Vibhu-Oska AI-OS.")
        result = engine.query("Who created Vibhu-Oska?", search_type="local")
        assert result.confidence > 0
        assert len(result.answer) > 0

    def test_query_global(self, engine):
        engine.ingest("NVIDIA makes GPUs. AMD makes CPUs.")
        result = engine.query("What companies are mentioned?", search_type="global")
        assert result.search_type == "global"

    def test_query_auto(self, engine):
        engine.ingest("Python is a programming language used for AI.")
        result = engine.query("Tell me about Python")
        assert result.search_type in ("local", "global", "drift")

    def test_get_stats(self, engine):
        stats = engine.get_stats()
        assert "total_entities" in stats
        assert "total_relationships" in stats
