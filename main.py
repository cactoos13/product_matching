"""
Entity Matching API - Main Application

This FastAPI application provides endpoints for finding similar products
based on advertisement text using ParsBERT embeddings, LSH, and cosine similarity.
"""

import logging
from typing import List, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import text

from bootstrap import bootstrap
from modules import Modules
from packages.core.registry import Registry
from packages.business.modules.advertisement.services.advertisement_redis_service import AdvertisementRedisService
from packages.business.modules.product.services.product_sql_service import ProductSqlService
from packages.core.sql_connector import SqlConnector
from redis import Redis

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Bootstrap the application
bootstrap(total=True, modules=Modules)

# Initialize FastAPI app
app = FastAPI(
    title="Entity Matching API",
    description="API for finding similar products based on advertisement text using ParsBERT + LSH + Cosine Similarity",
    version="1.0.0"
)


# ============================================================================
# Request/Response Models
# ============================================================================

class AdvertisementInput(BaseModel):
    """Input model for advertisement matching"""
    text: str = Field(..., description="Advertisement text to match against products", min_length=1)
    limit: Optional[int] = Field(10, description="Maximum number of products to return", ge=1, le=100)
    min_similarity: Optional[float] = Field(0.0, description="Minimum similarity threshold (0.0 to 1.0)", ge=0.0, le=1.0)


class ProductMatch(BaseModel):
    """Product match result with similarity score"""
    product_id: int = Field(..., description="Product ID")
    title: str = Field(..., description="Product title")
    description: Optional[str] = Field(None, description="Product description")
    similarity_score: float = Field(..., description="Similarity score (0.0 to 1.0)", ge=0.0, le=1.0)


class FindResponse(BaseModel):
    """Response model for find endpoint"""
    query_text: str = Field(..., description="The advertisement text that was searched")
    matches: List[ProductMatch] = Field(..., description="List of matched products with similarity scores")
    total_matches: int = Field(..., description="Total number of matches found")


class BatchAdvertisementInput(BaseModel):
    """Input model for batch advertisement matching"""
    advertisements: List[str] = Field(..., description="List of advertisement texts", min_items=1, max_items=100)


class BatchFindResponse(BaseModel):
    """Response model for batch find endpoint"""
    results: List[FindResponse] = Field(..., description="Results for each advertisement")


# ============================================================================
# Core Business Logic
# ============================================================================

def find_similar_products(
    advertisement_text: str,
    limit: int = 10,
    min_similarity: float = 0.0
) -> List[ProductMatch]:
    """
    Main function to find similar products for an advertisement.
    
    This is the core business logic that:
    1. Uses LSH to find candidate products (fast)
    2. Uses ParsBERT embeddings + cosine similarity to rank candidates (accurate)
    3. Retrieves product details from database
    4. Returns products with similarity scores
    
    Args:
        advertisement_text: The advertisement text to match
        limit: Maximum number of products to return
        min_similarity: Minimum similarity threshold
    
    Returns:
        List of ProductMatch objects sorted by similarity (highest first)
    """
    try:
        # Get services
        ad_service = Registry().get(AdvertisementRedisService)
        product_service = Registry().get(ProductSqlService)
        
        # Find similar products with scores using LSH + ParsBERT
        similar_products_with_scores = ad_service.query_with_scores(
            text=advertisement_text,
            limit=limit,
            min_similarity=min_similarity
        )
        
        if not similar_products_with_scores:
            return []
        
        # Get product details from database
        product_matches = []
        for product_id, similarity_score in similar_products_with_scores:
            try:
                product = product_service.get_by_id(product_id)
                if product:
                    product_matches.append(ProductMatch(
                        product_id=product.id,
                        title=product.title,
                        description=product.description if hasattr(product, 'description') else None,
                        similarity_score=round(similarity_score, 4)
                    ))
            except Exception as e:
                logger.warning(f"Failed to retrieve product {product_id}: {str(e)}")
                # Still include the product with limited info
                product_matches.append(ProductMatch(
                    product_id=product_id,
                    title=f"Product {product_id}",
                    description=None,
                    similarity_score=round(similarity_score, 4)
                ))
        
        return product_matches
        
    except Exception as e:
        logger.error(f"Error finding similar products: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


# ============================================================================
# API Endpoints
# ============================================================================

@app.post("/find", response_model=FindResponse, summary="Find similar products for an advertisement")
async def find_products(input_data: AdvertisementInput) -> FindResponse:
    """
    Find similar products based on advertisement text.
    
    This endpoint uses a hybrid approach:
    - **LSH (Locality-Sensitive Hashing)** for fast candidate retrieval
    - **ParsBERT embeddings** for semantic understanding
    - **Cosine similarity** for accurate ranking
    
    **Process:**
    1. Tokenize the advertisement text
    2. Use LSH to quickly find candidate products (fast approximate search)
    3. Generate ParsBERT embedding for the query
    4. Calculate cosine similarity for each candidate
    5. Rank and filter results
    6. Retrieve product details from database
    
    **Example Request:**
    ```json
    {
        "text": "iPhone 14 Pro Max 256GB Space Black",
        "limit": 10,
        "min_similarity": 0.5
    }
    ```
    
    **Example Response:**
    ```json
    {
        "query_text": "iPhone 14 Pro Max 256GB Space Black",
        "matches": [
            {
                "product_id": 123,
                "title": "iPhone 14 Pro Max 256GB",
                "description": "...",
                "similarity_score": 0.9234
            }
        ],
        "total_matches": 1
    }
    ```
    """
    matches = find_similar_products(
        advertisement_text=input_data.text,
        limit=input_data.limit,
        min_similarity=input_data.min_similarity
    )
    
    return FindResponse(
        query_text=input_data.text,
        matches=matches,
        total_matches=len(matches)
    )


@app.post("/find/batch", response_model=BatchFindResponse, summary="Find similar products for multiple advertisements")
async def find_products_batch(input_data: BatchAdvertisementInput) -> BatchFindResponse:
    """
    Find similar products for multiple advertisements in batch.
    
    This endpoint processes multiple advertisements and returns results for each.
    Useful for bulk matching operations.
    
    **Example Request:**
    ```json
    {
        "advertisements": [
            "iPhone 14 Pro Max",
            "Samsung Galaxy S23 Ultra"
        ]
    }
    ```
    
    **Limits:**
    - Maximum 100 advertisements per request
    - Each advertisement uses default limit (10) and min_similarity (0.0)
    """
    if len(input_data.advertisements) > 100:
        raise HTTPException(status_code=400, detail="Maximum 100 advertisements per batch request")
    
    results = []
    for ad_text in input_data.advertisements:
        matches = find_similar_products(
            advertisement_text=ad_text,
            limit=10,  # Default limit for batch
            min_similarity=0.0  # Default threshold for batch
        )
        results.append(FindResponse(
            query_text=ad_text,
            matches=matches,
            total_matches=len(matches)
        ))
    
    return BatchFindResponse(results=results)


@app.get("/health", summary="Health check endpoint")
async def health():
    """
    Check the health status of the system.
    
    Returns the status of:
    - Redis connection
    - Source database connection
    - Destination database connection
    """
    health_status = {
        "status": "ok",
        "redis": False,
        "source_db": False,
        "dest_db": False
    }
    
    # Check Redis
    try:
        redis = Registry().get(Redis)
        if redis.ping():
            health_status["redis"] = True
    except Exception as e:
        logger.error(f"Redis health check failed: {str(e)}")
        health_status["status"] = "degraded"
    
    # Check source database
    try:
        source_connector = Registry().get(SqlConnector, salt='source')
        session = source_connector.get_session()
        session.execute(text("SELECT 1"))
        session.close()
        health_status["source_db"] = True
    except Exception as e:
        logger.error(f"Source database health check failed: {str(e)}")
        health_status["status"] = "degraded"
    
    # Check destination database
    try:
        dest_connector = Registry().get(SqlConnector)
        session = dest_connector.get_session()
        session.execute(text("SELECT 1"))
        session.close()
        health_status["dest_db"] = True
    except Exception as e:
        logger.error(f"Destination database health check failed: {str(e)}")
        health_status["status"] = "degraded"
    
    # Overall status
    if not all([health_status["redis"], health_status["source_db"], health_status["dest_db"]]):
        health_status["status"] = "degraded"
    
    return health_status


@app.get("/ping", summary="Simple ping endpoint")
async def ping():
    """Simple ping endpoint to check if the API is running."""
    return {"status": "ok", "message": "pong"}


# ============================================================================
# Application Startup
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize services on application startup"""
    logger.info("Starting Entity Matching API...")
    logger.info("Services initialized successfully")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on application shutdown"""
    logger.info("Shutting down Entity Matching API...")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
