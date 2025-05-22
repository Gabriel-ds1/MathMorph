# models/nlp_encoder.py

import torch
import numpy as np
from transformers import AutoTokenizer, AutoModel
from config.settings import DEFAULT_TRANSFORMER_MODEL
from utils.cache_helpers import DiskCache
from utils.general_helpers import annotate_error

class NLPEncoder:
    def __init__(self, model_name: str = None, device: str = None):
        """
        Loads transformer model/tokenizer for encoding sentences.
        Defaults to MathBERT.
        """

        self.model_name = model_name or DEFAULT_TRANSFORMER_MODEL
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModel.from_pretrained(self.model_name)
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self.disk_cache = DiskCache()

    def encode(self, text:str, as_tensor:bool = False, fuzzy_cache:bool = True):
        """
        Given a string, or list of sentences, returns its embedding (mean pooled).
        Returns: numpy array or torch tensor (if as_tensor=True)
        """
        try:
            if not text or not isinstance(text, (str, list, tuple)):
                raise ValueError("Input text must be a non-empty string or list")
            
            # Text will be a list or string
            single_text = isinstance(text, str)
            text_list = [text] if single_text else list(text)

            # to cache
            results = [None] * len(text_list)
            to_encode = []
            to_encode_indices = []

            # Try to pull each text from cache
            for idx, t in enumerate(text_list):
                t_key = t.strip().lower()
                cached = self.disk_cache.get(t_key)
                if cached is not None:
                    results[idx] = cached if not as_tensor else torch.tensor(cached)
                else:
                    to_encode.append(t)
                    to_encode_indices.append(idx)
            
            # Encode only uncached texts
            if to_encode:

                # Batch tokenize/encode
                inputs = self.tokenizer(to_encode, return_tensors='pt', padding=True, truncation=True) # maybe add truncation=True, max_length=128
                inputs = {k: v.to(self.device) for k, v in inputs.items()}

                # set model to device and eval mode
                self.model.to(self.device)
                self.model.eval()

                # encode
                with torch.no_grad():
                    outputs = self.model(**inputs)
                    # Mean pooling (ignoring padding)
                    last_hidden_layer = outputs.last_hidden_state # [batch, seq, hidden]
                    mask = inputs['attention_mask'].unsqueeze(-1).expand(last_hidden_layer.shape)
                    summed = torch.sum(last_hidden_layer * mask, dim=1)
                    count = torch.clamp(mask.sum(dim=1), min=1e-9)
                    mean_pool = summed / count
                
                # embeddings
                for i, idx in enumerate(to_encode_indices):
                    emb_npy = mean_pool[i].cpu().numpy()
                    # Fuzzy check (optional)
                    if fuzzy_cache:
                        fuzzy_val = self.disk_cache.get(to_encode[i], fuzzy=True, embedding=emb_npy)
                        if fuzzy_val is not None:
                            results[idx] = fuzzy_val if not as_tensor else torch.tensor(fuzzy_val)
                            continue
                    # Cache the embedding
                    self.disk_cache.set(to_encode[i], emb_npy, embedding=emb_npy)
                    results[idx] = mean_pool[i] if as_tensor else emb_npy

            # Return single or list
            return results[0] if single_text else results
        except Exception as e:
            return annotate_error("semantic_parser", e, text)
                
    @staticmethod        
    def cosine_similarity(vec1, vec2):
        """Compute cosine similarity between two 1D numpy arrays or tensors."""
        # For torch or numpy arrays
        v1 = vec1.cpu().numpy() if hasattr(vec1, "cpu") else np.asarray(vec1)
        v2 = vec2.cpu().numpy() if hasattr(vec2, "cpu") else np.asarray(vec2)
        return np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2) + 1e-9)
    
    def find_most_similar(self, query, all_texts):
        """
        Given a query sentence and a list of texts, finds the most similar by encoding and comparing.
        Returns: (index, text, score)
        """

        query_vec = self.encode(query)
        all_vecs = self.encode(all_texts)
        scores = [self.cosine_similarity(query_vec, vec) for vec in all_vecs]
        best_idx = int(np.argmax(scores))
        return best_idx, all_texts[best_idx], scores[best_idx]

    def to_sentence_embedding_matrix(self, texts, as_tensor=False):
        """
        Given a list of texts, returns a (num_texts, embedding_dim) numpy array or tensor.
        """

        vectors = self.encode(texts, as_tensor=as_tensor)
        if as_tensor:
            return torch.stack(vectors)
        return np.stack(vectors)
    
