"""
[Semantic Cache Engine (API Cost & Rate Limit Optimization)]

Provides local persistent disk and memory caching for candidate career forecasts.
Identical or semantically similar candidate profiles (e.g. similar score buckets,
same domain, similar verified skills) retrieve cached forecasts instantly (0ms, $0 API cost).
"""

import hashlib
import json
import os
import logging
from pathlib import Path
from typing import Dict, Any, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class SemanticCacheEngine:
    """
    Persistent JSON disk & in-memory cache store for candidate forecasting payloads.
    """

    def __init__(self, cache_file_path: Optional[Path] = None):
        if cache_file_path is None:
            cache_dir = Path(__file__).resolve().parent.parent / "storage" / "cache"
            cache_dir.mkdir(parents=True, exist_ok=True)
            cache_file_path = cache_dir / "forecasting_cache.json"

        self.cache_file_path = cache_file_path
        self._memory_cache: Dict[str, dict] = {}
        self._load_cache_from_disk()

    def _load_cache_from_disk(self) -> None:
        if self.cache_file_path.exists():
            try:
                with open(self.cache_file_path, "r", encoding="utf-8") as f:
                    self._memory_cache = json.load(f)
                logging.info(f"[SemanticCache] Loaded {len(self._memory_cache)} cached forecast entries from disk.")
            except Exception as e:
                logging.warning(f"[SemanticCache] Failed to load disk cache: {e}. Starting fresh.")
                self._memory_cache = {}

    def _save_cache_to_disk(self) -> None:
        try:
            with open(self.cache_file_path, "w", encoding="utf-8") as f:
                json.dump(self._memory_cache, f, indent=2)
        except Exception as e:
            logging.error(f"[SemanticCache] Failed to persist cache to disk: {e}")

    @staticmethod
    def compute_profile_hash(
        master_score: float,
        anchored_domain: str,
        github_score: float,
        cp_score: float,
        resume_score: float,
        verified_skills: list = None
    ) -> str:
        """
        Computes a discretized semantic feature hash for a candidate's evaluation metrics.
        Scores are bucketed into 5-point intervals to allow semantic clustering.
        """
        # Discretize scores to 5-point buckets (e.g. 72.3 -> 70, 77.8 -> 75)
        master_bucket = int(master_score // 5) * 5
        github_bucket = int(github_score // 5) * 5
        cp_bucket = int(cp_score // 5) * 5
        resume_bucket = int(resume_score // 5) * 5

        sorted_skills = sorted([s.get("skill", "").lower() for s in (verified_skills or []) if isinstance(s, dict)])
        skills_str = "|".join(sorted_skills)

        vector_str = f"dom:{anchored_domain.lower()}|m:{master_bucket}|gh:{github_bucket}|cp:{cp_bucket}|res:{resume_bucket}|sk:{skills_str}"
        return hashlib.sha256(vector_str.encode('utf-8')).hexdigest()[:16]

    def get(self, profile_hash: str) -> Optional[dict]:
        """
        Retrieves a cached forecast payload if present.
        """
        if profile_hash in self._memory_cache:
            logging.info(f"[SemanticCache] Cache HIT for profile hash '{profile_hash}' (0ms, $0 API cost).")
            cached = self._memory_cache[profile_hash].copy()
            cached["cached_hit"] = True
            cached["forecast_method"] = "Semantic Cache (Local Disk Store)"
            return cached
        return None

    def set(self, profile_hash: str, forecast_data: dict) -> None:
        """
        Stores a forecast payload into the cache and persists to disk.
        """
        data_to_cache = forecast_data.copy()
        data_to_cache["cached_hit"] = False
        self._memory_cache[profile_hash] = data_to_cache
        self._save_cache_to_disk()
        logging.info(f"[SemanticCache] Cached forecast for profile hash '{profile_hash}'.")
