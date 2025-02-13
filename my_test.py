from datasketch import MinHashLSH, MinHash

minhash_lsh = MinHashLSH(
    threshold=0.3,
    num_perm=128,
)

m1 = MinHash(128)
m1.update("salam khubi amir hossein advari a er rer df fsdjkfjskd jskjdskjdkjd ".encode('utf-8'))

m2 = MinHash(128)
m2.update("salam khubi khoobam mersi fdjfdk  kjfdfjkdkjf  fjdkfjkdk sds as jkkjkj dsd s ds kjsdjk jkj".encode('utf-8'))

m3 = MinHash(128)
m3.update("salam khubi advari dsd dsds sdsd sd sds sd sdsd sd sds dssf sdfdsf sfsfsf s".encode('utf-8'))
minhashes = [
    m1, m2, m3
]

with minhash_lsh.insertion_session() as session:
    for i, minhash in enumerate(minhashes):
        session.insert("m%d" % i, minhash)


result = list(minhash_lsh.query(m1))

print("Approximate neighbours with Jaccard similarity > 0.5", result)
# Output: Approximate neighbours with Jaccard similarity > 0.5 ['m1', 'm2', 'm3']