#!/usr/bin/env python3

import os
import json
import chromadb
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Any, Optional
from datetime import datetime
import openai
from dotenv import load_dotenv


# Load environment variables
load_dotenv()

class RAGProcessor:
    def __init__(self, 
                 embedding_model_name: str = "all-MiniLM-L6-v2",
                 openai_api_key: Optional[str] = None,
                 use_openai: bool = True):
        """Initialize the RAG processor"""
        
        print("🤖 Initializing RAG Processor...")
        
        # Initialize embedding model (same as used for indexing)
        print(f"📊 Loading embedding model: {embedding_model_name}")
        self.embedding_model = SentenceTransformer(embedding_model_name)
        
        # Initialize ChromaDB client
        print("💾 Connecting to vector database...")
        self.chroma_client = chromadb.PersistentClient(path="./runbook_vectordb")
        
        try:
            self.collection = self.chroma_client.get_collection(name="runbook_chunks")
            print("✅ Connected to runbook chunks collection")
        except Exception as e:
            print(f"❌ Error connecting to vector database: {e}")
            print("💡 Please run indexing_pipeline.py first to create the vector database")
            raise
        
        # Initialize OpenAI (if API key provided)
        self.use_openai = use_openai
        if use_openai:
            api_key = openai_api_key or os.getenv('OPENAI_API_KEY')
            if api_key:
                openai.api_key = api_key
                self.openai_client = openai.OpenAI(api_key=api_key)
                print("✅ OpenAI client initialized")
            else:
                print("⚠️  No OpenAI API key found. Will use simple concatenation for answers.")
                self.use_openai = False
        
        # Load indexing metadata
        try:
            with open('indexing_metadata.json', 'r') as f:
                self.metadata = json.load(f)
                print(f"📋 Loaded metadata: {self.metadata['total_chunks']} chunks from {self.metadata['total_runbooks']} runbooks")
        except FileNotFoundError:
            print("⚠️  No indexing metadata found")
            self.metadata = {}
    
    def search_relevant_chunks(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Search for relevant chunks using vector similarity"""
        
        print(f"🔍 Searching for relevant chunks: '{query[:50]}...'")
        
        # Generate query embedding
        query_embedding = self.embedding_model.encode([query])
        
        # Search in vector database
        results = self.collection.query(
            query_embeddings=query_embedding.tolist(),
            n_results=top_k
        )
        
        # Format results
        relevant_chunks = []
        for i, (document, metadata, distance) in enumerate(zip(
            results['documents'][0],
            results['metadatas'][0], 
            results['distances'][0]
        )):
            chunk_info = {
                'content': document,
                'metadata': metadata,
                'relevance_score': 1 - distance,  # Convert distance to similarity score
                'rank': i + 1
            }
            relevant_chunks.append(chunk_info)
        
        print(f"📊 Found {len(relevant_chunks)} relevant chunks")
        return relevant_chunks
    
    def format_context_for_llm(self, chunks: List[Dict[str, Any]]) -> str:
        """Format retrieved chunks into context for LLM"""
        
        context_parts = []
        seen_runbooks = set()
        
        for chunk in chunks:
            metadata = chunk['metadata']
            runbook_title = metadata['runbook_title']
            runbook_url = metadata['runbook_url']
            content = chunk['content']
            
            # Add runbook info (only once per runbook)
            runbook_id = metadata['runbook_id']
            if runbook_id not in seen_runbooks:
                context_parts.append(f"\n--- {runbook_title} ---")
                context_parts.append(f"Source: {runbook_url}")
                seen_runbooks.add(runbook_id)
            
            # Add chunk content
            context_parts.append(f"\n{content}")
        
        return "\n".join(context_parts)
    
    def generate_answer_openai(self, query: str, context: str) -> str:
        """Generate answer using OpenAI GPT"""
        
        prompt = f"""Based on the following excerpts from Meesho's internal runbooks, please answer the user's question. 

RUNBOOK EXCERPTS:
{context}

USER QUESTION: {query}

INSTRUCTIONS:
- Provide a clear, actionable answer based ONLY on the information in the runbook excerpts above
- If the question cannot be answered from the provided excerpts, say "I cannot find specific information about this in the available runbooks"
- Include relevant details like steps, commands, or procedures when available
- Be concise but comprehensive
- If multiple runbooks contain relevant information, synthesize the information appropriately

ANSWER:"""

        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that answers questions about technical runbooks and procedures. Always base your answers strictly on the provided runbook content."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.1
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            print(f"❌ Error generating answer with OpenAI: {e}")
            return self.generate_answer_simple(query, context)
    
    def generate_answer_simple(self, query: str, context: str) -> str:
        """Generate simple answer by concatenating relevant chunks"""
        
        # Simple approach: return the most relevant chunks with some formatting
        lines = context.split('\n')
        filtered_lines = [line.strip() for line in lines if line.strip() and not line.startswith('---')]
        
        if not filtered_lines:
            return "I couldn't find relevant information in the runbooks for your query."
        
        # Take first few lines as answer
        answer_lines = filtered_lines[:10]  # First 10 non-empty lines
        answer = '\n'.join(answer_lines)
        
        return f"Based on the runbooks, here's what I found:\n\n{answer}"
    
    def extract_source_urls(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, str]]:
        """Extract unique source runbook URLs and titles"""
        
        sources = {}
        for chunk in chunks:
            metadata = chunk['metadata']
            runbook_id = metadata['runbook_id']
            
            if runbook_id not in sources:
                sources[runbook_id] = {
                    'title': metadata['runbook_title'],
                    'url': metadata['runbook_url'],
                    'relevance': chunk['relevance_score']
                }
        
        # Sort by relevance
        sorted_sources = sorted(sources.values(), key=lambda x: x['relevance'], reverse=True)
        return sorted_sources
    
    def process_query(self, query: str, top_k: int = 5) -> Dict[str, Any]:
        """Main method to process a user query and return answer with sources"""
        
        start_time = datetime.now()
        
        if not query or len(query.strip()) < 3:
            return {
                'answer': "Please provide a more specific question.",
                'sources': [],
                'query': query,
                'processing_time': 0,
                'chunks_found': 0
            }
        
        try:
            # Step 1: Search for relevant chunks
            relevant_chunks = self.search_relevant_chunks(query, top_k)
            
            if not relevant_chunks:
                return {
                    'answer': "I couldn't find any relevant information in the runbooks for your query. Please try rephrasing your question or check if the topic is covered in our runbooks.",
                    'sources': [],
                    'query': query,
                    'processing_time': (datetime.now() - start_time).total_seconds(),
                    'chunks_found': 0
                }
            
            # Step 2: Format context for LLM
            context = self.format_context_for_llm(relevant_chunks)
            
            # Step 3: Generate answer
            if self.use_openai:
                answer = self.generate_answer_openai(query, context)
            else:
                answer = self.generate_answer_simple(query, context)
            
            # Step 4: Extract source URLs
            sources = self.extract_source_urls(relevant_chunks)
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            return {
                'answer': answer,
                'sources': sources,
                'query': query,
                'processing_time': processing_time,
                'chunks_found': len(relevant_chunks),
                'chunks_used': relevant_chunks  # For debugging
            }
            
        except Exception as e:
            print(f"❌ Error processing query: {e}")
            return {
                'answer': f"Sorry, I encountered an error while processing your query: {str(e)}",
                'sources': [],
                'query': query,
                'processing_time': (datetime.now() - start_time).total_seconds(),
                'chunks_found': 0
            }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get statistics about the indexed runbooks"""
        
        try:
            collection_count = self.collection.count()
            return {
                'total_chunks': collection_count,
                'total_runbooks': self.metadata.get('total_runbooks', 'Unknown'),
                'indexed_at': self.metadata.get('indexed_at', 'Unknown'),
                'embedding_model': self.metadata.get('model_name', 'all-MiniLM-L6-v2'),
                'openai_enabled': self.use_openai
            }
        except Exception as e:
            return {'error': str(e)}

def main():
    """Test the RAG processor"""
    
    # Initialize processor
    processor = RAGProcessor()
    
    # Test queries
    test_queries = [
        "How to fix Jenkins pipeline failures?",
        "What should I do when nodes are faulty?", 
        "How to deploy to production?",
        "Steps for incident response"
    ]
    
    print("\n🧪 Testing RAG Processor...")
    
    for query in test_queries:
        print(f"\n" + "="*60)
        result = processor.process_query(query)
        
        print(f"Query: {result['query']}")
        print(f"Processing time: {result['processing_time']:.2f}s")
        print(f"Chunks found: {result['chunks_found']}")
        print(f"\nAnswer:\n{result['answer']}")
        
        if result['sources']:
            print(f"\nSources:")
            for i, source in enumerate(result['sources'], 1):
                print(f"{i}. {source['title']}")
                print(f"   URL: {source['url']}")
                print(f"   Relevance: {source['relevance']:.3f}")

if __name__ == "__main__":
    main() 