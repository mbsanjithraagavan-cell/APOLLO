-- PostgreSQL 16 + pgvector. Dimension measured from the existing embedder.
CREATE EXTENSION IF NOT EXISTS vector;
CREATE TABLE IF NOT EXISTS policy_chunks (
    chunk_id uuid PRIMARY KEY,
    policy_id text NOT NULL,
    revision text NOT NULL,
    content text NOT NULL,
    embedding vector(384) NOT NULL,
    UNIQUE (policy_id, revision, chunk_id)
);
