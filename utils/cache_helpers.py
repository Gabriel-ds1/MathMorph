# utils/cache_helpers.py

import os
import pickle
import numpy as np
from time import time
from config.settings import cache_dir, embedding_cache_file

CACHE_VERSION = "0.2.0"
DEFAULT_TTL = 60 * 60 * 24 # time-to-live (60 * 60 * 24 is 1 day (in seconds))

def default_key(text):
    # Basic normalization for cache keys
    return text.strip().lower()

class DiskCache:
    def __init__(self, cache_path="", key_func=default_key, similarity_threshold=0.97, ttl=DEFAULT_TTL):
        if cache_path is not None:
            cache_path = os.path.join(cache_dir, embedding_cache_file)

        self.cache_path = cache_path
        self.key_func = key_func
        self.similarity_threshold = similarity_threshold
        self.ttl = ttl
        self.cache = {}
        self.embs = {}  # key:text, value: np.array (for fast cosine search)

        # Load cache if available
        if os.path.exists(cache_path):
            with open(cache_path, "rb") as f:
                data = pickle.load(f)
                if isinstance(data, dict) and 'version' in data:
                    self.cache = data.get('cache', {})
                    self.embs = data.get('embs', {})
                else:  # old version; fallback
                    self.cache = data
                    self.embs = {}
            # Purge old entries on load
            self._purge_expired()
            # Try to restore emb matrix for fuzzy search
            if self.embs and isinstance(self.embs, dict):
                self._rebuild_matrix()

    def _current_time(self):
        return time()

    def _rebuild_matrix(self):
        """ Rebuilds the matrix index for fast fuzzy search """
        # Remove expired from embs
        self._purge_expired()
        self.mat_keys = [k for k in self.embs.keys() if k in self.cache and not self._is_expired(self.cache[k])]
        if self.mat_keys:
            self.mat = np.stack([self.embs[k] for k in self.mat_keys])
        else:
            self.mat = np.zeros((0, 0))
    
    def _is_expired(self, entry):
        # entry may be a dict with timestamp; if old, expire
        if isinstance(entry, dict) and "timestamp" in entry:
            return (self._current_time() - entry["timestamp"]) > self.ttl
        return False

    def _purge_expired(self):
        to_delete = []
        for k, v in self.cache.items():
            if self._is_expired(v):
                to_delete.append(k)
        for k in to_delete:
            self.cache.pop(k, None)
            self.embs.pop(k, None)  # clean embedding as well

    def get(self, key, fuzzy=False, embedding=None):
        norm_key = self.key_func(key)
        data = self.cache.get(norm_key)
        if data is not None:
            # TTL check
            if self._is_expired(data):
                self.cache.pop(norm_key, None)
                self.embs.pop(norm_key, None)
                return None
            val = data["value"] if isinstance(data, dict) and "value" in data else data
        else:
            val = None
        val = self.cache.get(norm_key)
        if val is not None or not fuzzy:
            return val
        if embedding is None: 
            return None
        
        # Fuzzy matching: use cosine similarity with existing embeddings
        self._rebuild_matrix()
        if self.mat.shape[0] == 0: 
            return None
        scores = np.dot(self.mat, embedding) / (np.linalg.norm(embedding) * np.linalg.norm(self.mat, axis=1) + 1e-9)
        idx = np.argmax(scores)

        match_key = self.mat_keys[idx] if idx < len(self.mat_keys) else None
        if match_key and scores[idx] > self.similarity_threshold:
            data = self.cache.get(match_key)
            if data is not None and not self._is_expired(data):
                return data["value"] if isinstance(data, dict) and "value" in data else data
            else:
                # Found expired
                self.cache.pop(match_key, None)
                self.embs.pop(match_key, None)
        return None

    def set(self, key, value, embedding=None):
        norm_key = self.key_func(key)
        self.cache[norm_key] = {
            "timestamp": self._current_time(),  # -- TTL
            "value": value}
        
        if embedding is not None:
            self.embs[norm_key] = embedding
            self._rebuild_matrix()
        self.save()

    def save(self):
        # Purge expired before saving to disk
        self._purge_expired()
        with open(self.cache_path, "wb") as f:
            pickle.dump({'version': CACHE_VERSION, 'cache': self.cache, 'embs': self.embs}, f)

    def __contains__(self, key):
        norm = self.key_func(key)
        entry = self.cache.get(norm)
        if entry and not self._is_expired(entry):
            return True
        return False

    def clear(self):
        self.cache = {}
        self.embs = {}
        if os.path.exists(self.cache_path):
            os.remove(self.cache_path)