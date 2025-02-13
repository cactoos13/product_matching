# from datasketch import MinHashLSH, MinHash
# from redis import Redis
#
#
# red = Redis(
#     host='localhost',
#     port=6379,
#     db=2,
#     decode_responses=True
# )
# minhash_lsh = MinHashLSH(
#     threshold=0.5,
#     num_perm=128,
#     storage_config={
#         'type': 'redis',
#         'base_name': 'minhash',
#         'redis': {
#             'host': 'localhost',
#             'port': 6379,
#             'db': 3,
#
#         },
#     }
# )
#
# m1 = MinHash(128)
# m1.update("salam khubi amir hossein advari a er rer df ".encode('utf-8'))
#
# m2 = MinHash(128)
# m2.update("salam khubi khoobam mersi".encode('utf-8'))
#
# m3 = MinHash(128)
# m3.update("salam khubi advari".encode('utf-8'))
# minhashes = [
#     m1, m2, m3
# ]
#
#
# with minhash_lsh.insertion_session() as session:
#     for i, minhash in enumerate(minhashes):
#         session.insert("m%d" % i, minhash)
#
#
# result = list(minhash_lsh.query(m1))
#
# print("Approximate neighbours with Jaccard similarity > 0.5", result)
# # Output: Approximate neighbours with Jaccard similarity > 0.5 ['m1', 'm2', 'm3']