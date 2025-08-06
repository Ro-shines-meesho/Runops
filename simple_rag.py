#!/usr/bin/env python3

import json
import re
from datetime import datetime
from typing import List, Dict, Any
from pathlib import Path
import os
from intelligent_runbook_creator import IntelligentRunbookCreator
import requests

try:
    from sentence_transformers import SentenceTransformer
    import chromadb
    from chromadb.utils import embedding_functions
    CHROMA_AVAILABLE = True
except ImportError as e:
    print(f"❌ Required Chroma/SentenceTransformers missing: {e}")
    CHROMA_AVAILABLE = False

try:
    import openai
    from dotenv import load_dotenv
    load_dotenv()
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    if OPENAI_API_KEY:
        openai.api_key = OPENAI_API_KEY
        OPENAI_AVAILABLE = True
    else:
        OPENAI_AVAILABLE = False
except ImportError:
    OPENAI_AVAILABLE = False

# Import config for Azure OpenAI
from config import (
    AZURE_OPENAI_API_KEY, 
    AZURE_OPENAI_ENDPOINT, 
    AZURE_OPENAI_API_DEPLOYMENT_NAME, 
    AZURE_OPENAI_API_VERSION
)

class AzureOpenAIClient:
    """Azure OpenAI client for enhanced analysis"""
    
    def __init__(self):
        self.api_key = AZURE_OPENAI_API_KEY
        self.endpoint = AZURE_OPENAI_ENDPOINT
        self.deployment_name = AZURE_OPENAI_API_DEPLOYMENT_NAME
        self.api_version = AZURE_OPENAI_API_VERSION
        
    def analyze_issue(self, query: str, chunked_data: List[Dict], runbook_stats: Dict) -> Dict[str, Any]:
        """Analyze the issue using Azure OpenAI"""
        try:
            # Prepare context from chunked data
            context_chunks = []
            for chunk in chunked_data[:10]:  # Limit to top 10 chunks
                context_chunks.append(f"Runbook: {chunk.get('runbook_title', 'Unknown')}\nContent: {chunk.get('text', '')[:500]}")
            
            context_text = "\n\n".join(context_chunks)
            
            # Check if we have any relevant context
            has_relevant_context = len(context_chunks) > 0
            
            if has_relevant_context:
                # Create analysis prompt for topics with some coverage
                analysis_prompt = f"""You are an expert DevOps engineer analyzing issues and runbook coverage. 

Current Query: "{query}"

Available Runbook Knowledge Base:
- Total Runbooks: {runbook_stats.get('total_runbooks', 0)}
- Total Knowledge Chunks: {runbook_stats.get('total_chunks', 0)}
- Search Type: {runbook_stats.get('search_type', 'Unknown')}

Relevant Runbook Content:
{context_text}

Please provide a detailed analysis. Respond with a valid JSON object containing these exact keys:

{{
  "issue_analysis": "What is the user trying to solve?",
  "coverage_assessment": "How well do existing runbooks cover this issue?",
  "gaps_identified": "What specific information is missing?",
  "root_cause_analysis": "Why might this issue be occurring?",
  "recommended_actions": "What should be done to address this?",
  "runbook_creation_rationale": "Why should a new runbook be created (if applicable)?",
  "confidence_score": 0.8,
  "priority_level": "medium"
}}

Focus on practical DevOps insights and actionable recommendations. Ensure the response is valid JSON."""
            else:
                # Create analysis prompt for topics with no coverage
                analysis_prompt = f"""You are an expert DevOps engineer analyzing a topic that is not covered in existing runbooks.

Current Query: "{query}"

Available Runbook Knowledge Base:
- Total Runbooks: {runbook_stats.get('total_runbooks', 0)}
- Total Knowledge Chunks: {runbook_stats.get('total_chunks', 0)}
- Search Type: {runbook_stats.get('search_type', 'Unknown')}

This topic is NOT covered in the existing runbook documentation. Please provide a detailed analysis. Respond with a valid JSON object containing these exact keys:

{{
  "issue_analysis": "What is the user trying to learn about?",
  "coverage_assessment": "This topic is not covered in existing runbooks",
  "gaps_identified": "Complete lack of documentation for this topic",
  "root_cause_analysis": "Why this topic might be important for DevOps teams",
  "recommended_actions": "What steps should be taken to address this gap?",
  "runbook_creation_rationale": "Why a new runbook should be created for this topic",
  "confidence_score": 0.9,
  "priority_level": "high"
}}

Focus on why this topic is important and what should be documented. Ensure the response is valid JSON."""

            headers = {
                "Content-Type": "application/json",
                "api-key": self.api_key
            }
            
            data = {
                "messages": [
                    {"role": "system", "content": "You are a DevOps expert analyzing runbook coverage and issues. Always respond with valid JSON."},
                    {"role": "user", "content": analysis_prompt}
                ],
                "max_tokens": 1500,
                "temperature": 0.3
            }
            
            response = requests.post(
                self.endpoint,
                headers=headers,
                json=data,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content']
                
                # Try to parse as JSON, fallback to text
                try:
                    # Clean the response to ensure it's valid JSON
                    content = content.strip()
                    if content.startswith('```json'):
                        content = content[7:]
                    if content.endswith('```'):
                        content = content[:-3]
                    content = content.strip()
                    
                    analysis = json.loads(content)
                    return {
                        "success": True,
                        "analysis": analysis,
                        "raw_response": content
                    }
                except json.JSONDecodeError as e:
                    print(f"❌ JSON parsing error: {e}")
                    print(f"Raw response: {content}")
                    return {
                        "success": True,
                        "analysis": {
                            "issue_analysis": "The user is seeking guidance on a DevOps topic",
                            "coverage_assessment": "Analysis completed but response format was unexpected",
                            "gaps_identified": "Unable to parse detailed gaps from response",
                            "root_cause_analysis": "See raw response for details",
                            "recommended_actions": "Review the analysis manually",
                            "runbook_creation_rationale": "Manual review required",
                            "confidence_score": 0.5,
                            "priority_level": "medium"
                        },
                        "raw_response": content
                    }
            else:
                return {
                    "success": False,
                    "error": f"Azure OpenAI API error: {response.status_code} - {response.text}",
                    "analysis": None
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Analysis failed: {str(e)}",
                "analysis": None
            }

class SimpleRAGSystem:
    def __init__(self, json_path="devops_runbooks.json"):
        print("🚀 Initializing RAG system with ChromaDB backend and Azure OpenAI analysis...")
        self.json_path = json_path
        self.runbooks_data = {}
        self.chunked_data = []
        self.vector_collection = None
        self.use_vector_search = False
        self.runbook_creator = IntelligentRunbookCreator()
        self.azure_client = AzureOpenAIClient()

        self.load_runbooks()
        self.chunk_runbooks()
        self.init_chroma()

    def load_runbooks(self):
        if not os.path.exists(self.json_path):
            print(f"❌ Runbooks JSON not found at {self.json_path}")
            return
        with open(self.json_path, 'r', encoding='utf-8') as f:
            self.runbooks_data = json.load(f)
        print(f"📚 Loaded {len(self.runbooks_data.get('runbooks', []))} runbooks")

    def chunk_runbooks(self):
        self.chunked_data = []
        for runbook in self.runbooks_data.get("runbooks", []):
            content = runbook.get("content", "")
            if isinstance(content, dict):
                content_text = content.get("body", "")
            else:
                content_text = str(content)

            # Simple chunking: split content into 500 char chunks
            chunks = [content_text[i:i+500] for i in range(0, len(content_text), 500)]
            for idx, chunk in enumerate(chunks):
                self.chunked_data.append({
                    "runbook_id": runbook.get("id"),
                    "runbook_title": runbook.get("title", ""),
                    "runbook_url": runbook.get("url", ""),
                    "chunk_index": idx,
                    "text": chunk
                })
        print(f"🧩 Created {len(self.chunked_data)} chunks from runbooks.")

    def init_chroma(self):
        if not CHROMA_AVAILABLE:
            print("⚠️ ChromaDB/SentenceTransformer not available")
            return
        try:
            client = chromadb.PersistentClient(path="./runbook_vectordb")
            self.vector_collection = client.get_collection("runbook_chunks")
            self.use_vector_search = True
            print("✅ Connected to ChromaDB vector store: runbook_chunks")
        except Exception as e:
            print(f"⚠️ Could not connect to ChromaDB: {e}")
            self.vector_collection = None
            self.use_vector_search = False

    def search_chunks(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        if self.use_vector_search:
            try:
                # Using vector search with query_texts parameter
                result = self.vector_collection.query(query_texts=[query], n_results=top_k)
                results = []
                for i in range(len(result['documents'][0])):
                    results.append({
                        'text': result['documents'][0][i],
                        'runbook_id': result['metadatas'][0][i].get('runbook_id'),
                        'title': result['metadatas'][0][i].get('runbook_title', ''),
                        'url': result['metadatas'][0][i].get('runbook_url', ''),
                        'chunk_index': result['metadatas'][0][i].get('chunk_index'),
                        'relevance_score': 1.0 / (1.0 + result['distances'][0][i])  # invert distance to relevance
                    })
                return results
            except Exception as e:
                print(f"❌ Chroma query failed: {e}")

        return self._fallback_text_search(query, top_k)

    def _fallback_text_search(self, query: str, top_k: int) -> List[Dict[str, Any]]:
        print("🔍 Using fallback keyword search (no vector index)")
        runbooks = self.runbooks_data.get('runbooks', [])
        query_lower = query.lower().strip()
        results = []

        for runbook in runbooks:
            content = runbook.get('content', '')
            if isinstance(content, dict):
                text = content.get('body', '')
            else:
                text = str(content)

            # Normalize
            text_clean = re.sub(r'\s+', ' ', text.lower())
            if query_lower in text_clean:
                results.append({
                    'text': text[:500],
                    'runbook_id': runbook.get('id'),
                    'title': runbook.get('title', ''),
                    'url': runbook.get('url', ''),
                    'chunk_index': 0,
                    'relevance_score': 1.0
                })

        return results[:top_k]

    def generate_answer(self, query: str, chunks: List[Dict[str, Any]]) -> str:
        if not chunks:
            # When no chunks are found, use Azure OpenAI to generate intelligent context
            if hasattr(self, 'azure_client'):
                prompt = f"""You are a helpful DevOps assistant. The user asked about: "{query}"

This topic is not covered in the existing runbook documentation. Please provide:

1. **What this topic typically involves** in a DevOps context
2. **Common issues and challenges** related to this topic
3. **General best practices** for handling this type of issue
4. **Suggested troubleshooting steps** that would be relevant
5. **When to escalate** or seek additional help

Provide a comprehensive, helpful response that gives the user actionable guidance even without specific runbook coverage. Focus on practical DevOps insights and general troubleshooting approaches."""

                try:
                    headers = {
                        "Content-Type": "application/json",
                        "api-key": AZURE_OPENAI_API_KEY
                    }
                    
                    data = {
                        "messages": [
                            {"role": "system", "content": "You are a DevOps expert providing helpful guidance on topics not covered in runbooks."},
                            {"role": "user", "content": prompt}
                        ],
                        "max_tokens": 1000,
                        "temperature": 0.3
                    }
                    
                    response = requests.post(
                        AZURE_OPENAI_ENDPOINT,
                        headers=headers,
                        json=data,
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        return result['choices'][0]['message']['content'].strip()
                    else:
                        print(f"❌ Azure OpenAI API error: {response.status_code}")
                        # fallback below
                except Exception as e:
                    print(f"❌ Azure OpenAI API error: {e}")
                    # fallback below
                
            # Simple fallback when Azure OpenAI is not available
            return f"I don't have specific runbook information about '{query}'. This topic may not be covered in our current documentation. Consider checking other internal resources or creating a runbook for this topic."

        # If Azure OpenAI is available, generate better answer
        if hasattr(self, 'azure_client'):
            context = "\n\n".join([f"From '{c['title']}':\n{c['text']}" for c in chunks[:5]])
            prompt = f"""You are a helpful DevOps assistant answering questions about Meesho internal runbooks.

Context:
{context}

Question:
{query}

Provide a clear, actionable answer based only on the provided runbook context. If information is missing, acknowledge the gaps and suggest what additional information might be helpful."""

            try:
                headers = {
                    "Content-Type": "application/json",
                    "api-key": AZURE_OPENAI_API_KEY
                }
                
                data = {
                    "messages": [
                        {"role": "system", "content": "You answer based only on the provided runbook context."},
                        {"role": "user", "content": prompt}
                    ],
                    "max_tokens": 800,
                    "temperature": 0.2
                }
                
                response = requests.post(
                    AZURE_OPENAI_ENDPOINT,
                    headers=headers,
                    json=data,
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    return result['choices'][0]['message']['content'].strip()
                else:
                    print(f"❌ Azure OpenAI API error: {response.status_code}")
                    # fallback below
            except Exception as e:
                print(f"❌ Azure OpenAI API error: {e}")
                # fallback below

        # Simple fallback answer
        lines = ["📘 Runbook findings:\n"]
        for i, c in enumerate(chunks[:3], 1):
            lines.append(f"{i}. From '{c['title']}':")
            lines.append(f"   {c['text'][:300]}...\n")
        return '\n'.join(lines)

    def process_query(self, query: str, create_if_missing: bool = False) -> Dict[str, Any]:
        start = datetime.now()
        if not query or len(query.strip()) < 3:
            return {"answer": "Please ask a more specific question.", "query": query, "chunks_found": 0}

        results = self.search_chunks(query, top_k=5)
        
        # Get system stats for analysis
        stats = self.get_stats()
        
        # Perform issue analysis using Azure OpenAI
        analysis_result = None
        if hasattr(self, 'azure_client'):
            analysis_result = self.azure_client.analyze_issue(query, self.chunked_data, stats)

        # Check if we have meaningful results (high relevance scores)
        meaningful_results = [r for r in results if r.get('relevance_score', 0) > 0.6]
        
        if not results or len(meaningful_results) == 0:
            # Generate intelligent answer even when no meaningful runbooks are found
            answer = self.generate_answer(query, [])  # Pass empty list to trigger intelligent response
            
            if create_if_missing and self.runbook_creator:
                print("ℹ️ No meaningful results found, attempting intelligent runbook creation...")
                create_result = self.runbook_creator.create_intelligent_runbook(query)
                return {
                    "answer": answer,
                    "generated_runbook": create_result.get("generated_runbook", create_result.get("message", "No runbook created.")),
                    "query": query,
                    "chunks_found": len(results),
                    "runbook_created": create_result.get("success", False),
                    "suggest_creation": True,
                    "can_create_runbook": self.runbook_creator is not None,
                    "sources": [],
                    "processing_time": (datetime.now() - start).total_seconds(),
                    "issue_analysis": analysis_result.get("analysis") if analysis_result and analysis_result.get("success") else None,
                    "analysis_success": analysis_result.get("success") if analysis_result else False
                }
            else:
                return {
                    "answer": answer,
                    "query": query,
                    "chunks_found": len(results),
                    "suggest_creation": True,
                    "can_create_runbook": self.runbook_creator is not None,
                    "sources": [],
                    "processing_time": (datetime.now() - start).total_seconds(),
                    "issue_analysis": analysis_result.get("analysis") if analysis_result and analysis_result.get("success") else None,
                    "analysis_success": analysis_result.get("success") if analysis_result else False
                }

        # Use meaningful results for answer generation
        answer = self.generate_answer(query, meaningful_results)
        return {
            "query": query,
            "chunks_found": len(meaningful_results),
            "answer": answer,
            "sources": [
                {"title": r["title"], "url": r["url"], "relevance": r["relevance_score"]}
                for r in meaningful_results
            ],
            "processing_time": (datetime.now() - start).total_seconds(),
            "suggest_creation": False,
            "can_create_runbook": False,
            "issue_analysis": analysis_result.get("analysis") if analysis_result and analysis_result.get("success") else None,
            "analysis_success": analysis_result.get("success") if analysis_result else False
        }

    def get_stats(self) -> Dict[str, Any]:
        return {
            "total_runbooks": len(self.runbooks_data.get('runbooks', [])) if self.runbooks_data else 0,
            "total_chunks": len(self.chunked_data),
            "search_type": "vector (chroma)" if self.use_vector_search else "text fallback"
        }


def main():
    rag = SimpleRAGSystem()
    queries = [
        "How to fix Jenkins build failure?",
        "What to do when node is not ready?",
        "High memory usage in pods"
    ]
    for q in queries:
        print("\n==============================")
        result = rag.process_query(q)
        print(f"Query: {q}")
        print(f"Answer:\n{result['answer']}")
        print("Sources:")
        for src in result.get("sources", []):
            print(f" - {src['title']} ({src['relevance']:.2f})")


if __name__ == "__main__":
    main()
