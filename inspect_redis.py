"""
Script to inspect what's stored in Redis

This script shows:
1. All keys in Redis
2. Advertisement index keys (if ADS_REDIS_INDEX_PREFIX is set)
3. LSH (MinHash) related keys
4. Last sync timestamp
5. Sample values for advertisement keys
"""

import os
from bootstrap import bootstrap
from modules import Modules
from packages.core.registry import Registry
from redis import Redis
from datasketch import MinHashLSH

# Bootstrap the application
bootstrap(total=True, modules=Modules)

# Get Redis client
redis_client = Registry().get(Redis)
lsh = Registry().get(MinHashLSH)

print("=" * 60)
print("Redis Inspection Report")
print("=" * 60)

# Create a temporary Redis client without decode_responses to handle binary keys
from redis import Redis as RedisClient

host = os.getenv('LSH_REDIS_HOST')
port = os.getenv('LSH_REDIS_PORT')
db = os.getenv('LSH_REDIS_DB')

if not host or not port or not db:
    print("Error: Redis connection details not found in environment")
    exit(1)

# Create a client without decode_responses to handle binary keys
raw_redis = RedisClient(
    host=host,
    port=int(port),
    db=int(db),
    decode_responses=False  # Don't decode, handle binary keys
)

# Get all keys using SCAN (safer than KEYS for large datasets)
all_keys = []
cursor = 0
try:
    while True:
        cursor, keys = raw_redis.scan(cursor, match="*", count=1000)
        for key in keys:
            try:
                # Try to decode as UTF-8
                decoded_key = key.decode('utf-8')
                all_keys.append(decoded_key)
            except UnicodeDecodeError:
                # Binary key (likely from LSH), represent as hex
                all_keys.append(f"<binary:{key[:20].hex()}>")
        if cursor == 0:
            break
except Exception as e:
    print(f"Error scanning keys: {e}")
finally:
    raw_redis.close()

print(f"\nTotal keys in Redis: {len(all_keys)}")

# Group keys by type
ad_keys = []
lsh_keys = []
other_keys = []

ad_idx_prefix = os.getenv('ADS_REDIS_INDEX_PREFIX', '')
last_sync_key = os.getenv('LAST_SYNC_KEY', 'last_sync')

for key in all_keys:
    key_str = str(key)
    if key_str.startswith('minhash') or '<binary' in key_str:
        lsh_keys.append(key_str)
    elif ad_idx_prefix and key_str.startswith(ad_idx_prefix):
        ad_keys.append(key_str)
    elif not ad_idx_prefix and key_str.isdigit():
        # If no prefix, numeric keys are likely ad IDs
        ad_keys.append(key_str)
    elif key_str == last_sync_key:
        other_keys.append(key_str)
    elif '<binary' not in key_str and '<unable' not in key_str:
        other_keys.append(key_str)

print(f"\nAdvertisement Index Keys: {len(ad_keys)}")
if ad_keys:
    print(f"  Sample keys (first 10): {ad_keys[:10]}")
    # Show sample values (skip binary keys)
    print("\n  Sample values:")
    for key in ad_keys[:5]:
        if '<binary' not in str(key):
            try:
                value = redis_client.get(key)
                print(f"    {key}: {value}")
            except Exception as e:
                print(f"    {key}: <error reading: {e}>")
        else:
            print(f"    {key}: <binary key - value not readable>")

print(f"\nLSH (MinHash) Keys: {len(lsh_keys)}")
if lsh_keys:
    print(f"  Sample keys (first 10): {lsh_keys[:10]}")

print(f"\nOther Keys: {len(other_keys)}")
for key in other_keys:
    value = redis_client.get(key)
    if key == last_sync_key:
        from datetime import datetime
        try:
            timestamp = int(value)
            dt = datetime.fromtimestamp(timestamp)
            print(f"  {key}: {value} ({dt})")
        except:
            print(f"  {key}: {value}")
    else:
        print(f"  {key}: {value}")

# Show LSH statistics if available
print("\n" + "=" * 60)
print("LSH Statistics")
print("=" * 60)
try:
    # Try to get some info about the LSH structure
    # Note: datasketch doesn't expose all keys directly, but we can see what's stored
    print(f"LSH threshold: {lsh.threshold}")
    print(f"LSH permutations: {lsh.h}")
    print(f"LSH storage type: Redis")
    print("\nNote: LSH stores data in hash buckets. Use Redis CLI to see all 'minhash:*' keys")
except Exception as e:
    print(f"Could not get LSH stats: {e}")

print("\n" + "=" * 60)
print("How to inspect Redis using CLI:")
print("=" * 60)
print("\n1. Connect to Redis CLI:")
print("   docker exec -it <redis_container_name> redis-cli")
print("   OR if running locally:")
print("   redis-cli -h <host> -p <port> -n <db>")
print("\n2. Useful commands:")
print("   KEYS *                    # List all keys")
print("   KEYS minhash:*            # List LSH keys")
print("   GET <key>                 # Get value for a key")
print("   TYPE <key>                # Get type of a key")
print("   TTL <key>                 # Get time-to-live")
print("   DBSIZE                    # Get total number of keys")
print("   INFO keyspace             # Get keyspace info")
print("\n3. For advertisement keys:")
if ad_idx_prefix:
    print(f"   KEYS {ad_idx_prefix}_*")
else:
    print("   KEYS [0-9]*             # Numeric keys are ad IDs")

