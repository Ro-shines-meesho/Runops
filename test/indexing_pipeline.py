#!/usr/bin/env python3

import json
import os
import re
from datetime import datetime
from typing import List, Dict, Any
import chromadb
from sentence_transformers import SentenceTransformer
import numpy as np
from pathlib import Path

class RunbookIndexer:
    def __init__(self, embedding_model_name: str = "all-MiniLM-L6-v2"):
        """Initialize the runbook indexer with embedding model and vector database"""
        
        print("🚀 Initializing Runbook Indexer...")
        
        # Initialize embedding model
        print(f"📊 Loading embedding model: {embedding_model_name}")
        self.embedding_model = SentenceTransformer(embedding_model_name)
        
        # Initialize ChromaDB
        print("💾 Setting up ChromaDB...")
        self.chroma_client = chromadb.PersistentClient(path="./runbook_vectordb")
        
        # Create or get collection
        self.collection_name = "runbook_chunks"
        try:
            self.collection = self.chroma_client.create_collection(
                name=self.collection_name,
                metadata={"description": "Meesho runbook chunks for RAG"}
            )
            print(f"✅ Created new collection: {self.collection_name}")
        except:
            self.collection = self.chroma_client.get_collection(name=self.collection_name)
            print(f"✅ Using existing collection: {self.collection_name}")
    
    def clean_text(self, text: str) -> str:
        """Clean and normalize text content"""
        if not text:
            return ""
        
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters but keep basic punctuation
        text = re.sub(r'[^\w\s\.\!\?\,\:\;\-\(\)]', ' ', text)
        
        return text.strip()
    
    def chunk_text(self, text: str, chunk_size: int = 400, overlap: int = 50) -> List[str]:
        """Split text into overlapping chunks"""
        if not text:
            return []
        
        words = text.split()
        if len(words) <= chunk_size:
            return [text]
        
        chunks = []
        start = 0
        
        while start < len(words):
            end = min(start + chunk_size, len(words))
            chunk = ' '.join(words[start:end])
            chunks.append(chunk)
            
            # Move start position with overlap
            start = end - overlap
            if start >= len(words):
                break
        
        return chunks
    
    def process_runbook(self, runbook: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Process a single runbook into chunks with metadata"""
        title = runbook.get('title', 'Unknown Runbook')
        content = runbook.get('content', {})
        
        # Extract text content
        if isinstance(content, dict):
            text_content = content.get('body', '')
        else:
            text_content = str(content)
        
        # Clean the text
        cleaned_text = self.clean_text(text_content)
        
        if not cleaned_text or len(cleaned_text) < 50:
            print(f"⚠️  Skipping runbook '{title}' - insufficient content")
            return []
        
        # Create chunks
        chunks = self.chunk_text(cleaned_text)
        
        processed_chunks = []
        for i, chunk in enumerate(chunks):
            chunk_data = {
                'id': f"{runbook.get('id', 'unknown')}_{i}",
                'text': chunk,
                'metadata': {
                    'runbook_id': runbook.get('id', ''),
                    'runbook_title': title,
                    'runbook_url': runbook.get('url', ''),
                    'chunk_index': i,
                    'total_chunks': len(chunks),
                    'word_count': len(chunk.split()),
                    'space': runbook.get('space', {}).get('key', 'DEVOPS') if isinstance(runbook.get('space'), dict) else 'DEVOPS'
                }
            }
            processed_chunks.append(chunk_data)
        
        return processed_chunks
    
    def generate_embeddings(self, texts: List[str]) -> np.ndarray:
        """Generate embeddings for a list of texts"""
        print(f"🧮 Generating embeddings for {len(texts)} text chunks...")
        embeddings = self.embedding_model.encode(texts, show_progress_bar=True)
        return embeddings
    
    def index_runbooks(self, json_file_path: str):
        """Main method to index all runbooks from JSON file"""
        
        print(f"📖 Loading runbooks from {json_file_path}")
        
        # Load the runbooks data
        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        runbooks = data.get('runbooks', [])
        print(f"📚 Found {len(runbooks)} runbooks to process")
        
        # Process all runbooks into chunks
        all_chunks = []
        runbook_stats = {}
        
        for i, runbook in enumerate(runbooks, 1):
            title = runbook.get('title', f'Runbook {i}')
            print(f"📄 Processing {i}/{len(runbooks)}: {title}")
            
            chunks = self.process_runbook(runbook)
            all_chunks.extend(chunks)
            
            runbook_stats[title] = {
                'chunks_created': len(chunks),
                'total_words': sum(chunk['metadata']['word_count'] for chunk in chunks)
            }
        
        print(f"\n📊 Processing Summary:")
        print(f"   Total runbooks: {len(runbooks)}")
        print(f"   Total chunks created: {len(all_chunks)}")
        print(f"   Average chunks per runbook: {len(all_chunks) / len(runbooks):.1f}")
        
        if not all_chunks:
            print("❌ No chunks created. Exiting.")
            return
        
        # Generate embeddings
        texts = [chunk['text'] for chunk in all_chunks]
        embeddings = self.generate_embeddings(texts)
        
        # Prepare data for ChromaDB
        ids = [chunk['id'] for chunk in all_chunks]
        metadatas = [chunk['metadata'] for chunk in all_chunks]
        documents = texts
        
        print(f"💾 Storing {len(all_chunks)} chunks in vector database...")
        
        # Clear existing data in collection
        try:
            self.collection.delete()
            print("🗑️  Cleared existing data")
        except:
            pass
        
        # Add new data in batches (ChromaDB has limits)
        batch_size = 1000
        for i in range(0, len(ids), batch_size):
            end_idx = min(i + batch_size, len(ids))
            
            batch_ids = ids[i:end_idx]
            batch_embeddings = embeddings[i:end_idx].tolist()
            batch_metadatas = metadatas[i:end_idx]
            batch_documents = documents[i:end_idx]
            
            self.collection.add(
                ids=batch_ids,
                embeddings=batch_embeddings,
                metadatas=batch_metadatas,
                documents=batch_documents
            )
            
            print(f"   📦 Stored batch {i//batch_size + 1}: {len(batch_ids)} chunks")
        
        # Save indexing metadata
        index_metadata = {
            'indexed_at': datetime.now().isoformat(),
            'total_runbooks': len(runbooks),
            'total_chunks': len(all_chunks),
            'embedding_model': self.embedding_model.get_sentence_embedding_dimension(),
            'model_name': "all-MiniLM-L6-v2",
            'runbook_stats': runbook_stats
        }
        
        with open('indexing_metadata.json', 'w', encoding='utf-8') as f:
            json.dump(index_metadata, f, indent=2, ensure_ascii=False)
        
        print(f"\n✅ INDEXING COMPLETE!")
        print(f"   📊 Indexed {len(runbooks)} runbooks into {len(all_chunks)} chunks")
        print(f"   💾 Vector database ready for queries")
        print(f"   📋 Metadata saved to indexing_metadata.json")
        
        # Show top runbooks by chunk count
        print(f"\n📈 Top runbooks by content (chunks):")
        sorted_stats = sorted(runbook_stats.items(), key=lambda x: x[1]['chunks_created'], reverse=True)
        for title, stats in sorted_stats[:10]:
            print(f"   • {title}: {stats['chunks_created']} chunks ({stats['total_words']} words)")
    
    def query_test(self, query: str, top_k: int = 3):
        """Test query to verify the indexing worked"""
        print(f"\n🔍 Testing query: '{query}'")
        
        # Generate query embedding
        query_embedding = self.embedding_model.encode([query])
        
        # Search in vector database
        results = self.collection.query(
            query_embeddings=query_embedding.tolist(),
            n_results=top_k
        )
        
        print(f"📊 Found {len(results['documents'][0])} relevant chunks:")
        
        for i, (doc, metadata, distance) in enumerate(zip(
            results['documents'][0], 
            results['metadatas'][0],
            results['distances'][0]
        )):
            print(f"\n{i+1}. Runbook: {metadata['runbook_title']}")
            print(f"   Relevance: {1-distance:.3f}")
            print(f"   URL: {metadata['runbook_url']}")
            print(f"   Content: {doc[:200]}...")

def main():
    """Main function to run the indexing pipeline"""
    
    # Find the most recent runbooks JSON file
    json_files = list(Path('.').glob('devops_runbooks.json'))
    
    if not json_files:
        print("❌ No runbooks JSON file found. Please run fetch_runbooks.py first.")
        return
    
    # Use the most recent file
    latest_file = max(json_files, key=os.path.getctime)
    print(f"📁 Using runbooks file: {latest_file}")
    
    # Initialize indexer and process runbooks
    indexer = RunbookIndexer()
    indexer.index_runbooks(str(latest_file))
    
    # Test with a sample query
    indexer.query_test("How to deploy jenkins pipeline?")
    indexer.query_test("What to do when nodes are faulty?")

if __name__ == "__main__":
    main() 