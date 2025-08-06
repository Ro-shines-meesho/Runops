#!/usr/bin/env python3

import os
import json
import re
from pathlib import Path
import gc
from typing import List, Dict, Any

import chromadb
from sentence_transformers import SentenceTransformer

# Set threading/env vars to reduce oversubscription (keep for safety)
os.environ["TOKENIZERS_PARALLELISM"] = "false"
os.environ["OMP_NUM_THREADS"] = "1"
os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["MKL_NUM_THREADS"] = "1"
os.environ["VECLIB_MAXIMUM_THREADS"] = "1"
os.environ["NUMEXPR_NUM_THREADS"] = "1"

class EfficientRunbookIndexer:
    def __init__(self, embedding_model_name: str = "all-MiniLM-L6-v2", chunk_size: int = 400, overlap: int = 50):
        print("🚀 Initializing Efficient Runbook Indexer...")
        self.embedding_model = SentenceTransformer(embedding_model_name, device='cpu')
        self.chunk_size = chunk_size
        self.overlap = overlap

        self.chroma_client = chromadb.PersistentClient(path="./runbook_vectordb")
        self.collection_name = "runbook_chunks"

        # Try to get existing collection, or create it if missing
        try:
            self.collection = self.chroma_client.get_collection(name=self.collection_name)
            print(f"📂 Loaded existing collection: {self.collection_name}")
        except Exception:
            self.collection = self.chroma_client.create_collection(
                name=self.collection_name,
                metadata={"description": "Meesho runbook chunks for RAG"}
            )
            print(f"✅ Created new collection: {self.collection_name}")

    def clean_text(self, text: str) -> str:
        # Clean HTML tags and reduce whitespace once
        text = re.sub(r'<[^>]+>', '', text)
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'[^\w\s\.\!\?\,\:\;\-\(\)]', ' ', text)
        return text.strip()

    def chunk_text(self, text: str) -> List[str]:
        # Chunk text by words with overlap
        words = text.split()
        if len(words) <= self.chunk_size:
            return [text]

        chunks = []
        start = 0
        while start < len(words):
            end = min(start + self.chunk_size, len(words))
            chunk = ' '.join(words[start:end])
            chunks.append(chunk)
            if end == len(words):
                break
            start = end - self.overlap
        return chunks

    def process_runbook(self, runbook: Dict[str, Any], idx: int) -> List[Dict[str, Any]]:
        title = runbook.get('title', f'Runbook {idx}')
        content = runbook.get('content', {})
        text_content = content.get('body', '') if isinstance(content, dict) else str(content)
        cleaned = self.clean_text(text_content)

        if len(cleaned) < 50:
            print(f"⚠️ Skipping Runbook {idx} (too short)")
            return []

        chunks = self.chunk_text(cleaned)
        chunk_datas = []
        space_key = 'DEVOPS'
        if isinstance(runbook.get('space'), dict):
            space_key = runbook['space'].get('key', 'DEVOPS')

        for i, chunk in enumerate(chunks):
            chunk_datas.append({
                'id': f"{runbook.get('id', f'unknown_{idx}')}_{i}",
                'text': chunk,
                'metadata': {
                    'runbook_id': runbook.get('id', ''),
                    'runbook_title': title,
                    'runbook_url': runbook.get('url', ''),
                    'chunk_index': i,
                    'total_chunks': len(chunks),
                    'word_count': len(chunk.split()),
                    'space': space_key
                }
            })
        print(f"✅ Processed runbook {idx} '{title[:50]}': {len(chunks)} chunks")
        return chunk_datas

    def embed_and_store(self, chunk_datas: List[Dict[str, Any]]):
        if not chunk_datas:
            return

        texts = [c['text'] for c in chunk_datas]
        ids = [c['id'] for c in chunk_datas]
        metadatas = [c['metadata'] for c in chunk_datas]

        print(f"🧮 Embedding {len(texts)} chunks in batch...")
        embeddings = self.embedding_model.encode(texts, batch_size=16, show_progress_bar=True)
        
        print(f"💾 Adding to ChromaDB collection...")
        self.collection.add(
            ids=ids,
            embeddings=embeddings.tolist(),
            metadatas=metadatas,
            documents=texts
        )
        del embeddings, texts, ids, metadatas
        gc.collect()

    def index_runbooks(self, json_file: str, batch_size: int = 10):
        print(f"📂 Loading runbooks from {json_file}...")
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        runbooks = data.get('runbooks', [])
        print(f"📚 {len(runbooks)} runbooks loaded")

        total_chunks = 0
        for batch_start in range(0, len(runbooks), batch_size):
            batch = runbooks[batch_start:batch_start + batch_size]
            print(f"\n📦 Processing batch {batch_start // batch_size + 1} (runbooks {batch_start+1}-{batch_start+len(batch)})")
            
            all_chunk_datas = []
            for i, runbook in enumerate(batch, start=batch_start + 1):
                chunks = self.process_runbook(runbook, i)
                all_chunk_datas.extend(chunks)

            self.embed_and_store(all_chunk_datas)
            total_chunks += len(all_chunk_datas)

            print(f"📊 Indexed {batch_start + len(batch)} / {len(runbooks)} runbooks, total chunks: {total_chunks}")
            gc.collect()

        print(f"\n🎉 INDEXING COMPLETE: {len(runbooks)} runbooks, {total_chunks} chunks indexed.")

def main():
    json_files = list(Path('.').glob('devops_runbooks.json'))
    if not json_files:
        print("❌ No runbooks JSON file found!")
        return

    latest_file = max(json_files, key=os.path.getctime)
    print(f"📁 Using latest runbooks file: {latest_file}")
    indexer = EfficientRunbookIndexer()
    indexer.index_runbooks(str(latest_file))

if __name__ == "__main__":
    main()
