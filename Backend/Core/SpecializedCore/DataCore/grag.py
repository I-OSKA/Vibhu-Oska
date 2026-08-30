"""
Vibhu-Oska AI-OS — GRAG (Graph RAG)
Full Graph Retrieval-Augmented Generation implementation.

Based on Microsoft Research's "From Local to Global: A Graph RAG Approach"

Architecture:
  EntityExtractor     → Extracts entities and relationships from text
  CommunityDetector   → Groups related entities using Leiden-like clustering
  CommunitySummarizer → Generates summaries for each community
  GRAGQuerier         → Local, Global, and DRIFT search patterns

Integration:
  GRAG is a sub-module of DataCore. It extends the basic knowledge graph
  with community detection and hierarchical summarization.

All processing is local. Zero external APIs.
"""

from __future__ import annotations

import logging
import re
import time
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any, Optional

logger = logging.getLogger("GRAG")

# Lazy spaCy loading
_spacy_nlp = None

def _get_spacy_nlp():
    """Lazy-load spaCy model for NER."""
    global _spacy_nlp
    if _spacy_nlp is None:
        try:
            import spacy
            _spacy_nlp = spacy.load("en_core_web_sm")
            logger.info("spaCy NER model loaded for GRAG entity extraction")
        except Exception as e:
            logger.warning("spaCy model not available: %s. Falling back to regex extraction.", e)
            _spacy_nlp = False  # Mark as unavailable
    return _spacy_nlp if _spacy_nlp is not False else None


# ==================================================================================================
# # Internal Separation Division
# ==================================================================================================


@dataclass
class Entity:
    """Extracted entity from text."""
    name: str
    entity_type: str  # PERSON, ORG, CONCEPT, HARDWARE, etc.
    description: str = ""
    source_text: str = ""
    frequency: int = 1


@dataclass
class Relationship:
    """Extracted relationship between entities."""
    source: str
    target: str
    relation: str
    weight: float = 1.0
    source_text: str = ""


@dataclass
class Community:
    """A cluster of related entities."""
    id: int
    entities: list[str] = field(default_factory=list)
    summary: str = ""
    level: int = 0  # Hierarchy level (0 = finest)


@dataclass
class GRAGResult:
    """Result from a GRAG query."""
    answer: str
    source_entities: list[str] = field(default_factory=list)
    source_communities: list[int] = field(default_factory=list)
    search_type: str = "local"
    confidence: float = 0.0


# ==================================================================================================
# # Internal Separation Division
# ==================================================================================================


class EntityExtractor:
    """
    Extracts entities and relationships from text.
    Uses spaCy NER (when available) + regex patterns for maximum coverage.
    """

    # Entity type patterns (fallback when spaCy unavailable)
    ENTITY_PATTERNS = {
        "PERSON": [
            r"\b([A-Z][a-z]+ (?:[A-Z][a-z]+ )*[A-Z][a-z]+)\b",  # Full names
            r"\b(Dr|Prof|Mr|Mrs|Ms|Sir)\.?\s+([A-Z][a-z]+)\b",
        ],
        "ORG": [
            r"\b(Google|Microsoft|Apple|Meta|Amazon|NVIDIA|AMD|Intel|OpenAI|Anthropic)\b",
            r"\b([A-Z][A-Za-z]+ (?:Inc|Corp|Ltd|LLC|Co))\b",
        ],
        "HARDWARE": [
            r"\b(RTX\s*\d{4}|GTX\s*\d{4}|GeForce|RTX|GTX)\b",
            r"\b(Ryzen\s*\d|Core\s*i\d|Intel|AMD)\b",
            r"\b(\d+GB\s*VRAM|\d+GB\s*RAM|\d+GB)\b",
        ],
        "CONCEPT": [
            r"\b(quantum|neural|transformer|attention|embedding|GRAG|RAG|LLM|SLM)\b",
            r"\b(inference|training|fine-tuning|quantization|pruning)\b",
        ],
        "CODING": [
            r"\b(Python|JavaScript|TypeScript|Rust|Go|C\+\+|Java|SQL)\b",
            r"\b(FastAPI|PyTorch|TensorFlow|React|Vue|Angular)\b",
        ],
    }

    # spaCy label → our entity type mapping
    _SPACY_TYPE_MAP = {
        "PERSON": "PERSON",
        "ORG": "ORG",
        "GPE": "LOCATION",
        "LOC": "LOCATION",
        "PRODUCT": "HARDWARE",
        "EVENT": "EVENT",
        "WORK_OF_ART": "CONCEPT",
        "LAW": "CONCEPT",
        "LANGUAGE": "CONCEPT",
        "DATE": "DATE",
        "TIME": "TIME",
        "MONEY": "MONEY",
        "QUANTITY": "QUANTITY",
        "ORDINAL": "ORDINAL",
        "CARDINAL": "CARDINAL",
    }

    RELATION_PATTERNS = [
        (r"(\w+)\s+is\s+(?:a|an)\s+(\w+)", "is_a"),
        (r"(\w+)\s+runs\s+on\s+(\w+)", "runs_on"),
        (r"(\w+)\s+uses\s+(\w+)", "uses"),
        (r"(\w+)\s+supports\s+(\w+)", "supports"),
        (r"(\w+)\s+implements\s+(\w+)", "implements"),
        (r"(\w+)\s+depends\s+on\s+(\w+)", "depends_on"),
        (r"(\w+)\s+contains\s+(\w+)", "contains"),
        (r"(\w+)\s+is\s+part\s+of\s+(\w+)", "part_of"),
    ]

    def __init__(self) -> None:
        """Initialize extractor and attempt to load spaCy NER."""
        self._spacy_available = False
        self._nlp = _get_spacy_nlp()
        if self._nlp:
            self._spacy_available = True

    def _extract_spacy(self, text: str) -> list[Entity]:
        """Extract entities using spaCy NER."""
        if not self._spacy_available:
            return []

        try:
            doc = self._nlp(text)
            entities = []
            for ent in doc.ents:
                etype = self._SPACY_TYPE_MAP.get(ent.label_, ent.label_)
                # Only keep entities with reasonable length
                if 2 <= len(ent.text) <= 100:
                    entities.append(Entity(
                        name=ent.text.strip(),
                        entity_type=etype,
                        source_text=text[max(0, ent.start_char-50):ent.end_char+50],
                        description=f"spaCy {ent.label_}",
                    ))
            return entities
        except Exception as e:
            logger.warning("spaCy extraction failed: %s", e)
            return []

    def _extract_regex(self, text: str) -> list[Entity]:
        """Extract entities using regex patterns (fallback)."""
        entities = []
        for etype, patterns in self.ENTITY_PATTERNS.items():
            for pattern in patterns:
                for match in re.finditer(pattern, text):
                    name = match.group(1) if match.lastindex else match.group(0)
                    entities.append(Entity(
                        name=name.strip(),
                        entity_type=etype,
                        source_text=text[max(0, match.start()-50):match.end()+50],
                    ))
        return entities

    def extract(self, text: str) -> tuple[list[Entity], list[Relationship]]:
        """
        Extract entities and relationships from text.
        Uses spaCy NER first, then supplements with regex patterns.

        Parameters:
            text: Input text to analyze
        Returns: (entities, relationships)
        """
        entities = []
        relationships = []

        # ── spaCy NER extraction (primary) ──────────────────────────────
        if self._spacy_available:
            spacy_entities = self._extract_spacy(text)
            entities.extend(spacy_entities)
            logger.debug("spaCy extracted %d entities", len(spacy_entities))

        # ── Regex extraction (supplementary) ────────────────────────────
        regex_entities = self._extract_regex(text)
        entities.extend(regex_entities)
        logger.debug("Regex extracted %d entities", len(regex_entities))

        # ── Dedup entities ──────────────────────────────────────────────
        seen = set()
        unique_entities = []
        for e in entities:
            key = (e.name.lower(), e.entity_type)
            if key not in seen:
                seen.add(key)
                unique_entities.append(e)
            else:
                # Increment frequency
                for ue in unique_entities:
                    if ue.name.lower() == e.name.lower():
                        ue.frequency += 1

        # ── Extract relationships (regex-based) ────────────────────────
        for pattern, rel_type in self.RELATION_PATTERNS:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                if match.lastindex and match.lastindex >= 2:
                    source = match.group(1).strip()
                    target = match.group(2).strip()
                    if len(source) > 2 and len(target) > 2:
                        relationships.append(Relationship(
                            source=source,
                            target=target,
                            relation=rel_type,
                            source_text=text[max(0, match.start()-30):match.end()+30],
                        ))

        return unique_entities, relationships


class CommunityDetector:
    """
    Detects communities (clusters) of related entities.
    Uses a simplified Leiden-like algorithm for community detection.
    """

    def __init__(self, resolution: float = 1.0) -> None:
        """
        Parameters:
            resolution: Higher = more, smaller communities. Lower = fewer, larger.
        """
        self._resolution = resolution

    def detect(
        self,
        entities: list[Entity],
        relationships: list[Relationship],
        max_levels: int = 3,
    ) -> list[Community]:
        """
        Detect communities from entities and relationships.

        Parameters:
            entities: Extracted entities
            relationships: Extracted relationships
            max_levels: Maximum hierarchy levels
        Returns: List of communities
        """
        # Build adjacency graph
        adj: dict[str, set[str]] = defaultdict(set)
        for rel in relationships:
            adj[rel.source].add(rel.target)
            adj[rel.target].add(rel.source)

        entity_names = [e.name for e in entities]
        
        # Initialize each entity as its own community
        communities: dict[int, set[str]] = {}
        for i, name in enumerate(entity_names):
            communities[i] = {name}

        # Iteratively merge communities
        for level in range(max_levels):
            merged = False
            community_list = list(communities.items())
            
            for i in range(len(community_list)):
                for j in range(i + 1, len(community_list)):
                    comm_i = community_list[i][1]
                    comm_j = community_list[j][1]
                    
                    # Check if communities have connections
                    connections = 0
                    for entity in comm_i:
                        connections += len(adj[entity] & comm_j)
                    
                    # Merge if enough connections (resolution-dependent threshold)
                    threshold = max(1, len(comm_i) * len(comm_j) * 0.1 * self._resolution)
                    
                    if connections >= threshold:
                        # Merge j into i
                        communities[community_list[i][0]] = comm_i | comm_j
                        del communities[community_list[j][0]]
                        merged = True
                        break
                if merged:
                    break
            
            if not merged:
                break

        # Convert to Community objects
        result = []
        for idx, (comm_id, member_set) in enumerate(communities.items()):
            result.append(Community(
                id=idx,
                entities=list(member_set),
                level=0,
            ))

        return result


class CommunitySummarizer:
    """
    Generates summaries for each community.
    Uses template-based summarization (no external LLM).
    """

    def summarize(
        self,
        community: Community,
        entities: list[Entity],
        relationships: list[Relationship],
    ) -> str:
        """
        Generate a summary for a community.

        Parameters:
            community: Community to summarize
            entities: All entities (filtered by community)
            relationships: All relationships (filtered by community)
        Returns: Summary string
        """
        entity_set = set(community.entities)
        
        # Filter entities in this community
        community_entities = [e for e in entities if e.name in entity_set]
        
        # Filter relationships in this community
        community_relationships = [
            r for r in relationships 
            if r.source in entity_set or r.target in entity_set
        ]

        # Group entities by type
        by_type: dict[str, list[Entity]] = defaultdict(list)
        for e in community_entities:
            by_type[e.entity_type].append(e)

        # Build summary
        parts = []
        
        # Entity listing by type
        for etype, elist in by_type.items():
            names = [e.name for e in elist]
            parts.append(f"{etype}: {', '.join(names[:5])}")

        # Key relationships
        if community_relationships:
            rel_parts = []
            for r in community_relationships[:10]:
                rel_parts.append(f"{r.source} --[{r.relation}]--> {r.target}")
            parts.append("Relationships: " + "; ".join(rel_parts))

        return " | ".join(parts) if parts else "Empty community"


# ==================================================================================================
# # Internal Separation Division
# ==================================================================================================


class GRAGQuerier:
    """
    Executes GRAG queries using three search patterns:
    - Local: Entity-centric, 1-2 hop traversal
    - Global: Community summary-based
    - DRIFT: Adaptive hopping between local and global
    """

    def __init__(self) -> None:
        pass

    def local_search(
        self,
        query: str,
        entities: list[Entity],
        relationships: list[Relationship],
        communities: list[Community],
        top_k: int = 5,
    ) -> GRAGResult:
        """
        Local search — entity-centric, finds matching entities and their neighbors.

        Best for: Specific factual questions (e.g., "What VRAM does my GPU have?")
        """
        query_lower = query.lower()
        query_words = set(query_lower.split())

        # Score entities by relevance
        scored_entities = []
        for e in entities:
            score = 0.0
            name_lower = e.name.lower()
            
            # Exact name match
            if name_lower in query_lower:
                score += 1.0
            
            # Word overlap
            name_words = set(name_lower.split())
            overlap = len(query_words & name_words)
            score += overlap * 0.3
            
            # Type bonus
            if e.entity_type in query_upper_types(query):
                score += 0.2
            
            # Frequency bonus
            score += min(e.frequency * 0.1, 0.5)
            
            if score > 0:
                scored_entities.append((e, score))

        # Sort by score, take top_k
        scored_entities.sort(key=lambda x: x[1], reverse=True)
        top_entities = scored_entities[:top_k]

        if not top_entities:
            return GRAGResult(answer="No relevant entities found", search_type="local")

        # Find connected entities (1-hop)
        entity_names = {e.name for e, _ in top_entities}
        connected = set()
        for rel in relationships:
            if rel.source in entity_names:
                connected.add(rel.target)
            if rel.target in entity_names:
                connected.add(rel.source)

        # Build context
        context_parts = []
        for e, score in top_entities:
            context_parts.append(f"{e.name} ({e.entity_type}): {e.description}")
        
        for name in list(connected)[:5]:
            for e in entities:
                if e.name == name:
                    context_parts.append(f"{e.name} ({e.entity_type}): {e.description}")
                    break

        return GRAGResult(
            answer="\n".join(context_parts),
            source_entities=[e.name for e, _ in top_entities],
            search_type="local",
            confidence=top_entities[0][1] if top_entities else 0.0,
        )

    def global_search(
        self,
        query: str,
        communities: list[Community],
        top_k: int = 3,
    ) -> GRAGResult:
        """
        Global search — queries community summaries for thematic understanding.

        Best for: Holistic questions (e.g., "What are the main themes in this data?")
        """
        query_lower = query.lower()
        query_words = set(query_lower.split())

        # Score communities by relevance to query
        scored_communities = []
        for comm in communities:
            if not comm.summary:
                continue
            
            summary_lower = comm.summary.lower()
            summary_words = set(summary_lower.split())
            overlap = len(query_words & summary_words)
            
            if overlap > 0:
                scored_communities.append((comm, overlap))

        scored_communities.sort(key=lambda x: x[1], reverse=True)
        top_communities = scored_communities[:top_k]

        if not top_communities:
            return GRAGResult(answer="No relevant communities found", search_type="global")

        # Build answer from community summaries
        summaries = []
        community_ids = []
        for comm, score in top_communities:
            summaries.append(f"Community {comm.id}: {comm.summary}")
            community_ids.append(comm.id)

        return GRAGResult(
            answer="\n\n".join(summaries),
            source_communities=community_ids,
            search_type="global",
            confidence=min(scored_communities[0][1] / 5.0, 1.0) if scored_communities else 0.0,
        )

    def drift_search(
        self,
        query: str,
        entities: list[Entity],
        relationships: list[Relationship],
        communities: list[Community],
        max_hops: int = 3,
    ) -> GRAGResult:
        """
        DRIFT search — adaptive hopping between local and global.

        Best for: Complex questions needing both specific details and big picture.
        """
        # Start with local search
        local_result = self.local_search(query, entities, relationships, communities)
        
        # If confidence is low, expand to global
        if local_result.confidence < 0.3:
            global_result = self.global_search(query, communities)
            
            # Merge results
            combined_answer = f"Local context:\n{local_result.answer}\n\nGlobal context:\n{global_result.answer}"
            
            return GRAGResult(
                answer=combined_answer,
                source_entities=local_result.source_entities,
                source_communities=global_result.source_communities,
                search_type="drift",
                confidence=max(local_result.confidence, global_result.confidence),
            )
        
        return local_result


def query_upper_types(query: str) -> set[str]:
    """Helper to detect entity types mentioned in query."""
    types = set()
    query_lower = query.lower()
    
    if any(w in query_lower for w in ["who", "person", "people", "author"]):
        types.add("PERSON")
    if any(w in query_lower for w in ["company", "org", "organization"]):
        types.add("ORG")
    if any(w in query_lower for w in ["gpu", "cpu", "hardware", "ram", "vram"]):
        types.add("HARDWARE")
    if any(w in query_lower for w in ["concept", "idea", "theory", "what is"]):
        types.add("CONCEPT")
    if any(w in query_lower for w in ["code", "programming", "language", "framework"]):
        types.add("CODING")
    
    return types


# ==================================================================================================
# # Internal Separation Division
# ==================================================================================================


class GRAGEngine:
    """
    GRAGEngine — Full Graph RAG implementation for DataCore.

    Usage:
        grag = GRAGEngine()
        
        # Ingest text
        grag.ingest("Text content to process...")
        
        # Query
        result = grag.query("What hardware is mentioned?", search_type="local")
    """

    def __init__(self) -> None:
        self._extractor = EntityExtractor()
        self._community_detector = CommunityDetector(resolution=1.0)
        self._summarizer = CommunitySummarizer()
        self._querier = GRAGQuerier()
        
        self._entities: list[Entity] = []
        self._relationships: list[Relationship] = []
        self._communities: list[Community] = []
        self._ingested_count = 0

    def ingest(self, text: str) -> dict[str, int]:
        """
        Ingest text into the GRAG knowledge graph.

        Parameters:
            text: Text to process
        Returns: Dict with counts of extracted items
        """
        entities, relationships = self._extractor.extract(text)
        
        self._entities.extend(entities)
        self._relationships.extend(relationships)
        self._ingested_count += 1

        # Rebuild communities periodically
        if self._ingested_count % 5 == 0:
            self._rebuild_communities()

        return {
            "entities_extracted": len(entities),
            "relationships_extracted": len(relationships),
            "total_entities": len(self._entities),
            "total_relationships": len(self._relationships),
            "total_communities": len(self._communities),
        }

    def _rebuild_communities(self) -> None:
        """Rebuild community detection from current entities/relationships."""
        self._communities = self._community_detector.detect(
            self._entities, self._relationships
        )
        
        # Generate summaries for each community
        for comm in self._communities:
            comm.summary = self._summarizer.summarize(
                comm, self._entities, self._relationships
            )

        logger.info("GRAG: Rebuilt %d communities from %d entities",
                     len(self._communities), len(self._entities))

    def query(
        self,
        query_text: str,
        search_type: str = "auto",
        top_k: int = 5,
    ) -> GRAGResult:
        """
        Query the GRAG knowledge graph.

        Parameters:
            query_text: User query
            search_type: "local", "global", "drift", or "auto"
            top_k: Number of results
        Returns: GRAGResult
        """
        if not self._entities:
            return GRAGResult(answer="Knowledge graph is empty", search_type="none")

        # Auto-detect search type
        if search_type == "auto":
            search_type = self._detect_search_type(query_text)

        if search_type == "local":
            return self._querier.local_search(
                query_text, self._entities, self._relationships, self._communities, top_k
            )
        elif search_type == "global":
            return self._querier.global_search(query_text, self._communities, top_k)
        elif search_type == "drift":
            return self._querier.drift_search(
                query_text, self._entities, self._relationships, self._communities
            )
        else:
            return GRAGResult(answer=f"Unknown search type: {search_type}", search_type="none")

    def _detect_search_type(self, query: str) -> str:
        """Auto-detect the best search type for a query."""
        query_lower = query.lower()
        
        # Global indicators
        global_words = ["overall", "summary", "themes", "main", "general", "all", "overview"]
        if any(w in query_lower for w in global_words):
            return "global"
        
        # Local indicators
        local_words = ["what", "who", "where", "specific", "details", "tell me about"]
        if any(w in query_lower for w in local_words):
            return "local"
        
        # Default to DRIFT for complex queries
        return "drift"

    def get_stats(self) -> dict[str, Any]:
        """Return GRAG statistics."""
        return {
            "total_entities": len(self._entities),
            "total_relationships": len(self._relationships),
            "total_communities": len(self._communities),
            "ingested_documents": self._ingested_count,
            "entity_types": dict(self._count_entity_types()),
        }

    def _count_entity_types(self) -> dict[str, int]:
        """Count entities by type."""
        counts: dict[str, int] = defaultdict(int)
        for e in self._entities:
            counts[e.entity_type] += 1
        return dict(counts)
