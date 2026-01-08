import os
import pickle
import base64
import re
from datetime import datetime
from typing import Type, List, Tuple
import numpy as np

from redis import Redis
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from datasketch import MinHashLSH, MinHash
from packages.business.modules.advertisement.entities.advertisement_idx_entity import AdvertisementIdx
from packages.core.registry import Registry
from packages.core.repository.redis_repository import RedisRepository


class AdvertisementRedisRepository(RedisRepository[AdvertisementIdx]):
    def __init__(self, entity: Type[AdvertisementIdx], redis_client: Redis):
        super().__init__(entity, redis_client)
        self.redis_client = redis_client
        self.entity = entity
        
        # Initialize ParsBERT model
        model_name = os.getenv('PARSBERT_MODEL_NAME', 'HooshvareLab/bert-fa-base-uncased')
        device = os.getenv('PARSBERT_DEVICE', None)
        
        # Auto-detect device if not specified
        if device is None:
            try:
                import torch
                device = 'cuda' if torch.cuda.is_available() else 'cpu'
            except:
                device = 'cpu'
        
        try:
            self.model = SentenceTransformer(model_name, device=device)
            self.model_name = model_name
            self.device = device
        except Exception as e:
            print(f"Error loading ParsBERT model {model_name}: {e}")
            print("Trying alternative: HooshvareLab/bert-fa-base-uncased")
            try:
                self.model = SentenceTransformer("HooshvareLab/bert-fa-base-uncased", device=device)
                self.model_name = "HooshvareLab/bert-fa-base-uncased"
                self.device = device
            except Exception as e2:
                raise ImportError(f"Could not load ParsBERT model. Error: {e2}")
        
        # Cache for product embeddings matrix (loaded from Redis)
        self._product_embeddings_cache = None
        self._product_ids_cache = None
        self._product_texts_cache = {}
        
        # Get embedding dimension from model
        try:
            # Get dimension by encoding a dummy text
            dummy_embedding = self.model.encode("test", convert_to_numpy=True)
            self.embedding_dim = dummy_embedding.shape[0]
        except:
            # Default to 768 (common BERT dimension)
            self.embedding_dim = 768
        
        # Initialize LSH for fast candidate retrieval
        # Get LSH parameters from environment or use defaults
        lsh_threshold = float(os.getenv('LSH_SIMILARITY_THRESHOLD', '0.3'))
        lsh_num_perm = int(os.getenv('LSH_PERMUTATIONS', '128'))
        
        # Try to get LSH from registry first (if it exists)
        try:
            self.lsh = Registry().get(MinHashLSH)
            # Get actual threshold and num_perm from the LSH instance
            # Note: MinHashLSH stores threshold as an attribute, num_perm as 'h'
            self.threshold = getattr(self.lsh, 'threshold', lsh_threshold)
            self.num_perm = getattr(self.lsh, 'h', lsh_num_perm)
            print(f"✓ Using LSH from registry (threshold={self.threshold}, num_perm={self.num_perm})")
        except:
            # Create new LSH instance
            # Get Redis connection details for LSH storage
            lsh_redis_host = os.getenv('LSH_REDIS_HOST')
            lsh_redis_port = os.getenv('LSH_REDIS_PORT')
            lsh_redis_db = os.getenv('LSH_REDIS_DB')
            
            if lsh_redis_host and lsh_redis_port and lsh_redis_db:
                # Use Redis-backed LSH
                self.lsh = MinHashLSH(
                    threshold=lsh_threshold,
                    num_perm=lsh_num_perm,
                    storage_config={
                        'type': 'redis',
                        'redis': {
                            'host': lsh_redis_host,
                            'port': int(lsh_redis_port),
                            'db': int(lsh_redis_db),
                        },
                        'basename': b'minhash',
                        'key': 'minhash'
                    }
                )
            else:
                # Use in-memory LSH (for testing/development)
                self.lsh = MinHashLSH(threshold=lsh_threshold, num_perm=lsh_num_perm)
            
            self.threshold = lsh_threshold
            self.num_perm = lsh_num_perm
            print(f"✓ Initialized LSH (threshold={lsh_threshold}, num_perm={lsh_num_perm})")

    def _get_embedding_key(self, product_id: int) -> str:
        """Get Redis key for storing product embedding"""
        prefix = os.getenv('ADS_REDIS_INDEX_PREFIX', '')
        if prefix:
            return f"{prefix}_embedding_{product_id}"
        return f"embedding_{product_id}"

    def _get_text_key(self, product_id: int) -> str:
        """Get Redis key for storing product text"""
        prefix = os.getenv('ADS_REDIS_INDEX_PREFIX', '')
        if prefix:
            return f"{prefix}_text_{product_id}"
        return f"text_{product_id}"

    def _get_all_products_key(self) -> str:
        """Get Redis key for storing list of all product IDs"""
        prefix = os.getenv('ADS_REDIS_INDEX_PREFIX', '')
        if prefix:
            return f"{prefix}_all_products"
        return "all_products"

    def _encode_text(self, text: str) -> np.ndarray:
        """Generate embedding for a single text using ParsBERT"""
        embedding = self.model.encode(text, convert_to_numpy=True)
        return embedding

    def _encode_texts_batch(self, texts: List[str], batch_size: int = 32) -> np.ndarray:
        """Generate embeddings for multiple texts in batches"""
        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            convert_to_numpy=True,
            show_progress_bar=True
        )
        return embeddings

    def _serialize_embedding(self, embedding: np.ndarray) -> str:
        """Serialize numpy array to base64 string for Redis storage"""
        return base64.b64encode(pickle.dumps(embedding)).decode('utf-8')

    def _deserialize_embedding(self, data: str) -> np.ndarray:
        """Deserialize base64 string from Redis to numpy array"""
        return pickle.loads(base64.b64decode(data.encode('utf-8')))

    def _tokenize(self, text: str) -> List[str]:
        """Tokenize text into a list of tokens (words)"""
        tokens = re.findall(r'\b\w+\b', text.lower())
        return tokens

    def _create_minhash_from_tokens(self, tokens: List[str]) -> MinHash:
        """Create a MinHash from tokens"""
        m = MinHash(self.num_perm)
        for token in tokens:
            m.update(token.encode('utf-8'))
        return m

    def _load_all_product_embeddings(self) -> Tuple[np.ndarray, List[int]]:
        """Load all product embeddings from Redis and return as matrix"""
        if self._product_embeddings_cache is not None:
            return self._product_embeddings_cache, self._product_ids_cache
        
        # Get all product IDs
        all_products_key = self._get_all_products_key()
        product_ids_str = self.redis_client.get(all_products_key)
        
        if not product_ids_str:
            # No products indexed yet
            self._product_embeddings_cache = np.array([]).reshape(0, self.embedding_dim)
            self._product_ids_cache = []
            return self._product_embeddings_cache, self._product_ids_cache
        
        # Parse product IDs
        product_ids = [int(pid) for pid in product_ids_str.split(',') if pid]
        
        if not product_ids:
            self._product_embeddings_cache = np.array([]).reshape(0, self.embedding_dim)
            self._product_ids_cache = []
            return self._product_embeddings_cache, self._product_ids_cache
        
        # Load embeddings for all products
        embeddings_list = []
        valid_product_ids = []
        
        for product_id in product_ids:
            embedding_key = self._get_embedding_key(product_id)
            embedding_data = self.redis_client.get(embedding_key)
            if embedding_data:
                try:
                    embedding = self._deserialize_embedding(embedding_data)
                    embeddings_list.append(embedding)
                    valid_product_ids.append(product_id)
                except Exception as e:
                    print(f"Warning: Failed to deserialize embedding for product {product_id}: {e}")
                    continue
        
        if not embeddings_list:
            self._product_embeddings_cache = np.array([]).reshape(0, 768)
            self._product_ids_cache = []
            return self._product_embeddings_cache, self._product_ids_cache
        
        # Convert to numpy matrix
        embeddings_matrix = np.vstack(embeddings_list)
        
        # Cache results
        self._product_embeddings_cache = embeddings_matrix
        self._product_ids_cache = valid_product_ids
        
        return embeddings_matrix, valid_product_ids

    def query(self, text: str, limit: int = 10, min_similarity: float = 0.0) -> List[int]:
        """
        Find similar products using LSH + ParsBERT embeddings + cosine similarity.
        
        Process:
        1. Use LSH to find candidate products (fast)
        2. Rank candidates using ParsBERT embeddings + cosine similarity (accurate)
        
        Args:
            text: Query text to search for
            limit: Maximum number of products to return
            min_similarity: Minimum similarity threshold (0.0 to 1.0)
        
        Returns:
            List of product IDs sorted by similarity (highest first)
        """
        results = self.query_with_scores(text, limit=limit, min_similarity=min_similarity)
        return [product_id for product_id, _ in results]
    
    def query_with_scores(self, text: str, limit: int = 10, min_similarity: float = 0.0) -> List[Tuple[int, float]]:
        """
        Find similar products using LSH + ParsBERT embeddings + cosine similarity.
        Returns products with their similarity scores.
        
        Process:
        1. Use LSH to find candidate products (fast)
        2. Rank candidates using ParsBERT embeddings + cosine similarity (accurate)
        
        Args:
            text: Query text to search for
            limit: Maximum number of products to return
            min_similarity: Minimum similarity threshold (0.0 to 1.0)
        
        Returns:
            List of tuples: (product_id, similarity_score) sorted by similarity (highest first)
        """
        # Step 1: Use LSH to find candidates (fast)
        query_tokens = self._tokenize(text)
        query_minhash = self._create_minhash_from_tokens(query_tokens)
        candidate_ids = self.lsh.query(query_minhash)
        
        if not candidate_ids:
            return []
        
        # Step 2: Generate ParsBERT embedding for query
        query_embedding = self._encode_text(text)
        query_embedding = query_embedding.reshape(1, -1)  # Reshape for cosine_similarity
        
        # Step 3: Calculate cosine similarity for each candidate using ParsBERT embeddings
        similarities = []
        for product_id in candidate_ids:
            # Load embedding for this product
            embedding_key = self._get_embedding_key(product_id)
            embedding_data = self.redis_client.get(embedding_key)
            
            if embedding_data:
                try:
                    product_embedding = self._deserialize_embedding(embedding_data)
                    product_embedding = product_embedding.reshape(1, -1)
                    cosine_sim = cosine_similarity(query_embedding, product_embedding)[0][0]
                    
                    if cosine_sim >= min_similarity:
                        similarities.append((product_id, float(cosine_sim)))
                except Exception as e:
                    # Skip products with invalid embeddings
                    continue
        
        # Sort by cosine similarity (highest first)
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        # Return top N with scores
        return similarities[:limit]

    def save(self, entity: AdvertisementIdx):
        """
        Save product embedding to Redis and index in LSH.
        
        Steps:
        1. Generate ParsBERT embedding
        2. Store embedding in Redis
        3. Create MinHash signature and index in LSH
        """
        # Generate ParsBERT embedding
        embedding = self._encode_text(entity.text)
        
        # Serialize and store embedding
        embedding_key = self._get_embedding_key(entity.id)
        embedding_data = self._serialize_embedding(embedding)
        self.redis_client.set(embedding_key, embedding_data)
        
        # Store product text
        text_key = self._get_text_key(entity.id)
        self.redis_client.set(text_key, entity.text)
        self._product_texts_cache[entity.id] = entity.text
        
        # Index in LSH using MinHash
        tokens = self._tokenize(entity.text)
        minhash = self._create_minhash_from_tokens(tokens)
        
        # Insert into LSH (handle case where key already exists)
        try:
            self.lsh.insert(entity.id, minhash)
        except ValueError:
            # Key already exists, remove and re-insert
            try:
                self.lsh.remove(entity.id)
            except:
                pass
            self.lsh.insert(entity.id, minhash)
        
        # Update list of all product IDs
        all_products_key = self._get_all_products_key()
        existing_ids_str = self.redis_client.get(all_products_key)
        
        if existing_ids_str:
            existing_ids = set(int(pid) for pid in existing_ids_str.split(',') if pid)
            existing_ids.add(entity.id)
            product_ids_str = ','.join(str(pid) for pid in sorted(existing_ids))
        else:
            product_ids_str = str(entity.id)
        
        self.redis_client.set(all_products_key, product_ids_str)
        
        # Mark as indexed
        ad_idx_prefix = os.getenv('ADS_REDIS_INDEX_PREFIX')
        entity_id = str(entity.id)
        if ad_idx_prefix:
            entity_id = f"{ad_idx_prefix}_{entity.id}"
        self.redis_client.set(entity_id, "1")
        
        # Invalidate cache
        self._product_embeddings_cache = None
        self._product_ids_cache = None

    def save_all(self, entities: List[AdvertisementIdx], batch_size: int = 32):
        """
        Save multiple products efficiently using batch encoding and LSH indexing.
        
        Steps:
        1. Generate ParsBERT embeddings in batch
        2. Store embeddings in Redis
        3. Create MinHash signatures and index in LSH
        """
        if not entities:
            return
        
        # Extract texts for batch encoding
        texts = [entity.text for entity in entities]
        
        # Step 1: Generate ParsBERT embeddings in batch
        print(f"Step 1: Generating ParsBERT embeddings for {len(entities)} products...")
        embeddings = self._encode_texts_batch(texts, batch_size=batch_size)
        
        # Step 2: Store embeddings and index in LSH
        print(f"Step 2: Storing embeddings and indexing in LSH...")
        all_products_key = self._get_all_products_key()
        existing_ids_str = self.redis_client.get(all_products_key)
        existing_ids = set()
        if existing_ids_str:
            existing_ids = set(int(pid) for pid in existing_ids_str.split(',') if pid)
        
        for i, entity in enumerate(entities):
            # Store ParsBERT embedding
            embedding_key = self._get_embedding_key(entity.id)
            embedding_data = self._serialize_embedding(embeddings[i])
            self.redis_client.set(embedding_key, embedding_data)
            
            # Store text
            text_key = self._get_text_key(entity.id)
            self.redis_client.set(text_key, entity.text)
            self._product_texts_cache[entity.id] = entity.text
            
            # Index in LSH using MinHash
            tokens = self._tokenize(entity.text)
            minhash = self._create_minhash_from_tokens(tokens)
            
            # Insert into LSH (handle case where key already exists)
            try:
                self.lsh.insert(entity.id, minhash)
            except ValueError:
                # Key already exists, remove and re-insert
                try:
                    self.lsh.remove(entity.id)
                except:
                    pass
                self.lsh.insert(entity.id, minhash)
            
            # Add to existing IDs
            existing_ids.add(entity.id)
            
            # Mark as indexed
            ad_idx_prefix = os.getenv('ADS_REDIS_INDEX_PREFIX')
            entity_id = str(entity.id)
            if ad_idx_prefix:
                entity_id = f"{ad_idx_prefix}_{entity.id}"
            self.redis_client.set(entity_id, "1")
        
        # Update list of all product IDs
        product_ids_str = ','.join(str(pid) for pid in sorted(existing_ids))
        self.redis_client.set(all_products_key, product_ids_str)
        
        # Invalidate cache
        self._product_embeddings_cache = None
        self._product_ids_cache = None
        
        print(f"✓ Successfully indexed {len(entities)} products!")
        print(f"  - ParsBERT embeddings: {len(entities)}")
        print(f"  - LSH indexed: {len(entities)}")
        print(f"  Method: LSH for candidate retrieval + ParsBERT embeddings + cosine similarity for ranking")


    def update_last_sync(self):
        key = os.getenv('LAST_SYNC_KEY')
        if not key:
            key = 'last_sync'
        self.redis_client.set(key, str(int(datetime.now().timestamp())))


    async def get_last_sync(self)-> datetime | None:
        key = os.getenv('LAST_SYNC_KEY')
        if not key:
            key = 'last_sync'
        result = await self.redis_client.get(key)
        if result:
            return datetime.fromtimestamp(int(result))
        return None




