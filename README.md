# runops
=======
# 🤖 Meesho Runbook RAG System

A Retrieval-Augmented Generation (RAG) system that allows you to query Meesho's runbooks using natural language and get intelligent answers with source references.

## 🏗️ System Overview

This system consists of two main phases:

### Phase 1: Indexing (Preparing Runbooks)
1. **Fetch runbooks** from Confluence API
2. **Chunk content** into semantic pieces  
3. **Generate embeddings** using sentence transformers
4. **Store in vector database** (ChromaDB) for fast retrieval

### Phase 2: Querying (Answering Questions)
1. **Receive user query** via web interface
2. **Convert query to embedding** using same model
3. **Search vector database** for relevant chunks
4. **Generate answer** using retrieved context
5. **Return answer with source URLs**

## 🚀 Quick Start

### 1. Install Dependencies

```bash
# Activate your virtual environment
source venv/bin/activate  # Linux/Mac
# or venv\Scripts\activate  # Windows

# Install all required packages
pip install -r requirements.txt
```

### 2. Index Your Runbooks

First, make sure you have runbook data (you should already have `runbooks_data_*.json` from running `fetch_runbooks.py`):

```bash
python indexing_pipeline.py
```

This will:
- ✅ Process 50+ runbooks into chunks
- ✅ Generate embeddings for all content
- ✅ Store in vector database (`./runbook_vectordb/`)
- ✅ Create indexing metadata

### 3. Start the Web Application

```bash
python web_app.py
```

Then open your browser to: **http://localhost:5000**

## 📊 What You'll See

### System Stats
- **50 Runbooks** indexed from DEVOPS space
- **~200+ Knowledge Chunks** for precise retrieval
- **🔧 Basic Mode** (or ✅ AI Enhanced with OpenAI)

### Example Queries
- "How to fix Jenkins pipeline failures?"
- "What to do when nodes are faulty?"
- "Steps for incident response"
- "How to onboard new partners?"

## 🎯 Features

### Smart Search
- **Vector similarity** search finds relevant content even with different wording
- **Semantic understanding** - finds related concepts, not just keyword matches
- **Ranked results** by relevance score

### Intelligent Answers
- **Context-aware responses** using retrieved runbook chunks
- **Source attribution** with direct links to original runbooks
- **Confidence scoring** shows how relevant each source is

### Beautiful Interface
- **Modern web UI** with responsive design
- **Real-time search** with loading indicators
- **Source links** for diving deeper into runbooks
- **Example queries** to get started quickly

## 🔧 Advanced Configuration

### Adding OpenAI Integration

For enhanced answer generation, you can add OpenAI support:

1. Get an OpenAI API key from https://platform.openai.com/
2. Set the environment variable:
   ```bash
   export OPENAI_API_KEY="your-api-key-here"
   ```
3. Modify `web_app.py` line 18:
   ```python
   rag_processor = RAGProcessor(use_openai=True)
   ```

### Customizing Chunk Size

Edit `indexing_pipeline.py` line 67:
```python
def chunk_text(self, text: str, chunk_size: int = 400, overlap: int = 50):
```

- **chunk_size**: Words per chunk (default: 400)
- **overlap**: Overlapping words between chunks (default: 50)

### Changing Embedding Model

Edit both `indexing_pipeline.py` and `rag_processor.py`:
```python
embedding_model_name: str = "all-MiniLM-L6-v2"  # Default
# or try: "BAAI/bge-base-en-v1.5" for better quality
```

## 📁 File Structure

```
runbook-bot/
├── fetch_runbooks.py          # Fetch runbooks from Confluence
├── indexing_pipeline.py       # Process and index runbooks  
├── rag_processor.py           # RAG query processing
├── web_app.py                 # Flask web application
├── requirements.txt           # Python dependencies
├── config.py                  # Confluence API configuration
├── runbooks_data_*.json       # Fetched runbook data
├── indexing_metadata.json     # Indexing statistics
├── runbook_vectordb/          # ChromaDB vector database
└── templates/                 # HTML templates
    ├── index.html            # Main web interface
    └── error.html            # Error page
```

## 🔄 Updating Runbooks

To refresh the system with latest runbooks:

1. **Fetch latest data**:
   ```bash
   python specific.py
   ```

2. **Re-index content**:
   ```bash
   python indexing_pipeline.py
   ```

3. **Restart web app**:
   ```bash
   python simple_web_app.py
   ```

## 🧪 Testing

### Test the Indexing Pipeline
```bash
python indexing_pipeline.py
```
Look for output like:
```
✅ INDEXING COMPLETE!
📊 Indexed 20+ runbooks into 200+ chunks
💾 Vector database ready for queries
```

### Test the RAG Processor
```bash
python rag_processor.py
```
This will run sample queries and show results.


## 🔍 Troubleshooting

### "RAG system not initialized"
- **Solution**: Run `python indexing_pipeline.py` first

### "No runbooks JSON file found"
- **Solution**: Run `python fetch_runbooks.py` first

### Slow embedding generation
- **Normal**: First run downloads the model (~90MB)
- **Future runs**: Much faster as model is cached

### Low relevance scores
- **Try**: More specific queries
- **Check**: If topic exists in your runbooks
- **Adjust**: Increase `top_k` parameter in queries

## 📈 Performance Stats

- **Indexing time**: ~2-3 minutes for 50 runbooks
- **Query response**: <2 seconds average
- **Memory usage**: ~500MB with embeddings loaded
- **Storage**: ~50MB for vector database

## 🎯 Next Steps

1. **Add more runbooks**: Expand to other Confluence spaces
2. **Enhance UI**: Add filters, search history, bookmarks
3. **Integrate Slack**: Build the Slack bot interface
4. **Add analytics**: Track popular queries and answers
5. **Improve chunking**: Smart paragraph/section-based splitting

## ❓ Common Queries

### How does it work?
The system converts both runbooks and your questions into numerical vectors (embeddings). It then finds runbook chunks with similar vectors to your question and uses that context to generate an answer.

### How accurate are the answers?
Answers are generated from your actual runbook content, so accuracy depends on:
- How well your question matches runbook content
- Quality of the original runbooks
- Relevance of the retrieved chunks

### Can I add my own runbooks?
Yes! Add them to your Confluence space and re-run the indexing pipeline.

---

## 🎉 Ready to Go!

Your Runbook RAG system is now ready! Start by running:

```bash
python specific.py           #manually fetch runbooks from confluence
python indexing_pipeline.py  # Index your runbooks
python simple_rag.py         #test rag
python rag_processory.py     #test rag
python web_app.py           # Start the web interface
```
curl to query an issue
```
curl -X POST -H "Content-Type: application/json" -d '{"query": "how to fix Redis connection issues"}' http://localhost:5003/query
```
Then visit **http://localhost:5000** and start asking questions! 🚀 

