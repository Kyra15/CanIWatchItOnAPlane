import time
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2", device="mps")

sentences = ["This is a test sentence."] * 10

# First run (cold)
t0 = time.time()
model.encode(sentences)
print("Cold run:", time.time() - t0)

# Second run (warm)
t0 = time.time()
model.encode(sentences)
print("Warm run:", time.time() - t0)
