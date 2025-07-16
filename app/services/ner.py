from collections import defaultdict
from functools import lru_cache
from pathlib import Path
from typing import List

from transformers import (
    AutoTokenizer,
    AutoModelForTokenClassification,
    pipeline,
)
from app.utils.logger import log_info, log_error

from app.config.settings import (
    SKILL_DIR,
    ENTITY_MODEL
)

from app.pydantics.schemas import ExtractedEntities, GenericServiceResponse

TARGET = {"PER", "ORG", "LOC", "MISC"}

DATA_DIR = Path(__file__).parent.parent / "data"


class NERService:

    def __init__(self):
        self.target = TARGET
        self.known_skills = self._load_known_skills()

    def _load_known_skills(self) -> set:
        """Load predefined skills from a text file."""
        skills_file = SKILL_DIR / "skills.txt"
        if not skills_file.exists():
            return set()
        with open(skills_file, "r", encoding="utf-8") as f:
            return {line.strip().lower() for line in f if line.strip()}

    @staticmethod
    @lru_cache(maxsize=1)
    def _load_pipeline():
        """Load and memoise the HuggingFace NER pipeline once per process."""
        tokenizer = AutoTokenizer.from_pretrained(ENTITY_MODEL)
        model = AutoModelForTokenClassification.from_pretrained(ENTITY_MODEL)
        return pipeline(
            "ner",
            model=model,
            tokenizer=tokenizer,
            aggregation_strategy="simple",
        )

    def run_ner(self, text: str):
        """Return aggregated spans from the DSLIM model."""
        try:
            ner_pipe = self._load_pipeline()
            spans = ner_pipe(text)
            entities = self.spans_to_entity(spans, text)
            return GenericServiceResponse(
                   result=entities
                   )

        except Exception as e:
            return GenericServiceResponse(
                   success=False,
                   error=str(e)
                   )

    @staticmethod
    def _flush(chunk: List[str]) -> str:
        """Turn the current chunk list into a single clean phrase."""
        return " ".join(chunk).strip() if chunk else ""

    def spans_to_entity(self, spans, text: str = ""):
        """
        Group contiguous tokens that share the same label and rebuild
        word‑pieces so we get clean phrases like “Priya Sharma” or “PostgreSQL”.
        """
        try:
            grouped = defaultdict(list)
            prev_label = None
            chunk: List[str] = []

            for span in spans:
                label = span["entity_group"]
                tok = span["word"]  # keep original token with possible '##'
                if label not in self.target:
                    # flush any open chunk when we hit an irrelevant label
                    if prev_label in self.target and chunk:
                        grouped[prev_label].append(self._flush(chunk))
                        chunk = []
                    prev_label = None
                    continue

                # if label changes, flush the previous chunk
                if label != prev_label and chunk:
                    grouped[prev_label].append(self._flush(chunk))
                    chunk = []

                # ── smart join: handle WordPiece continuation ──────────
                if tok.startswith("##"):
                    if chunk:
                        chunk[-1] += tok[2:]
                    else:
                        chunk.append(tok[2:])  # edge case: chunk empty
                else:
                    chunk.append(tok)

                prev_label = label

            # flush last chunk
            if prev_label in self.target and chunk:
                grouped[prev_label].append(self._flush(chunk))

            # ── Match MISC tokens with known skills ──
            misc_tokens = grouped["MISC"]
            skill_bucket = {}

            for tok in misc_tokens:
                low = tok.lower()
                if low in self.known_skills and low not in skill_bucket:
                    skill_bucket[low] = tok

                    # ── Also search full text for known skills ──
            text_lower = text.lower()
            for skill in self.known_skills:
                if skill in text_lower and skill not in skill_bucket:
                    skill_bucket[skill] = skill  # use original or title case

            clean_skills_list = list(skill_bucket.values())
            clean_skills = ", ".join(clean_skills_list) if clean_skills_list else None

            # Build EntityBase
            entities = ExtractedEntities(
                name=grouped["PER"][0] if grouped["PER"] else None,
                current_company=grouped["ORG"][0] if grouped["ORG"] else None,
                location=grouped["LOC"][0] if grouped["LOC"] else None,
                skills=clean_skills,
            )

            return entities

        except Exception as e:
            log_error(f"Error in NER service. "
                      f"Error: {str(e)}")
            return GenericServiceResponse(
                   success=False,
                   error=str(e)
                   )

