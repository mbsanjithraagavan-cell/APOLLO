import json
from pathlib import Path
from typing import Iterable
import psycopg
from sentence_transformers import SentenceTransformer

class PolicyService:
    def __init__(self, dsn: str, embedder_path: str, dimension: int = 384):
        self.dsn, self.embedder_path, self.dimension = dsn, embedder_path, dimension
    def ingest(self, policy_path: str) -> int:
        records=json.loads(Path(policy_path).read_text(encoding="utf-8"))
        embedder=SentenceTransformer(self.embedder_path, local_files_only=True, device="cpu")
        vectors=embedder.encode([r["content"] for r in records], normalize_embeddings=True).tolist()
        with psycopg.connect(self.dsn) as conn, conn.cursor() as cur:
            for r,v in zip(records,vectors):
                cur.execute("INSERT INTO clinic_policies(id,policy_id,revision,category,content,embedding) VALUES (gen_random_uuid(),%s,'demo-1',%s,%s,%s) ON CONFLICT(policy_id,revision) DO UPDATE SET category=EXCLUDED.category,content=EXCLUDED.content,embedding=EXCLUDED.embedding",(r["chunk_id"],r["category"],r["content"],v))
            conn.commit()
        return len(records)
    def query(self, text: str, top_k: int = 3) -> list[dict]:
        embedder=SentenceTransformer(self.embedder_path, local_files_only=True, device="cpu")
        vector=embedder.encode([text], normalize_embeddings=True).tolist()[0]
        with psycopg.connect(self.dsn) as conn, conn.cursor() as cur:
            cur.execute("SELECT policy_id,category,content,(embedding <=> %s::vector) AS distance FROM clinic_policies WHERE embedding IS NOT NULL ORDER BY embedding <=> %s::vector LIMIT %s",(vector,vector,top_k))
            return [{"chunk_id":r[0],"category":r[1],"content":r[2],"distance":float(r[3])} for r in cur.fetchall()]

