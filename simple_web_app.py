#!/usr/bin/env python3

from flask import Flask, render_template, request, jsonify
import os
from datetime import datetime
from simple_rag import SimpleRAGSystem


app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')

# Global RAG processor instance
rag_processor = None

def initialize_rag():
    """Initialize the Simple RAG processor"""
    global rag_processor
    try:
        json_path = "/Users/user/Documents/runbook-bot/devops_runbooks.json"
        rag_processor = SimpleRAGSystem(json_path)
        return True
    except Exception as e:
        print(f"❌ Error initializing RAG processor: {e}")
        return False


@app.route('/')
def index():
    """Main page with query interface"""
    global rag_processor
    
    # Initialize RAG processor if not done
    if rag_processor is None:
        init_success = initialize_rag()
        if not init_success:
            return render_template('error.html', 
                                 error="RAG system not initialized. Please ensure runbooks data is available.")
    
    # Get stats
    stats = rag_processor.get_stats() if rag_processor else {}
    
    return render_template('index.html', stats=stats)

@app.route('/query', methods=['POST'])
def query():
    """Handle query requests"""
    global rag_processor
    
    if not rag_processor:
        return jsonify({'error': 'RAG system not initialized'}), 500
    
    data = request.get_json()
    user_query = data.get('query', '').strip()
    create_runbook = data.get('create_runbook', False)
    
    if not user_query:
        return jsonify({'error': 'Please provide a query'}), 400
    
    # Process the query
    result = rag_processor.process_query(user_query, create_if_missing=create_runbook)
    
    # Ensure all expected fields are present
    response_data = {
        "query": result.get("query", user_query),
        "chunks_found": result.get("chunks_found", 0),
        "answer": result.get("answer"),
        "generated_runbook": result.get("generated_runbook"),
        "runbook_created": result.get("runbook_created", False),
        "suggest_creation": result.get("suggest_creation", False),
        "can_create_runbook": result.get("can_create_runbook", False),
        "sources": result.get("sources", []),
        "processing_time": result.get("processing_time", 0),
        "issue_analysis": result.get("issue_analysis"),
        "analysis_success": result.get("analysis_success", False)
    }
    
    return jsonify(response_data)

@app.route('/stats')
def stats():
    """Get system statistics"""
    global rag_processor
    
    if not rag_processor:
        return jsonify({'error': 'RAG system not initialized'}), 500
    
    stats = rag_processor.get_stats()
    return jsonify(stats)

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'rag_initialized': rag_processor is not None
    })

def create_templates():
    """Create HTML templates for the web interface"""
    
    # Main index template
    index_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Meesho Runbook Assistant</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        
        .container {
            background: white;
            border-radius: 15px;
            box-shadow: 0 20px 40px rgba(0,0,0,0.1);
            max-width: 800px;
            width: 100%;
            overflow: hidden;
        }
        
        .header {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            text-align: center;
        }
        
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
            font-weight: 300;
        }
        
        .header p {
            opacity: 0.9;
            font-size: 1.1em;
        }
        
        .stats {
            background: rgba(255,255,255,0.1);
            margin: 20px 0;
            padding: 15px;
            border-radius: 10px;
            display: flex;
            justify-content: space-around;
            text-align: center;
        }
        
        .stat-item {
            flex: 1;
        }
        
        .stat-number {
            font-size: 1.8em;
            font-weight: bold;
            display: block;
        }
        
        .stat-label {
            font-size: 0.9em;
            opacity: 0.8;
        }
        
        .main-content {
            padding: 40px;
        }
        
        .query-section {
            margin-bottom: 30px;
        }
        
        .query-input {
            width: 100%;
            padding: 15px;
            border: 2px solid #e1e8ed;
            border-radius: 10px;
            font-size: 1.1em;
            transition: border-color 0.3s;
            resize: vertical;
            min-height: 60px;
        }
        
        .query-input:focus {
            outline: none;
            border-color: #667eea;
        }
        
        .query-button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 15px 30px;
            border-radius: 10px;
            font-size: 1.1em;
            cursor: pointer;
            margin-top: 15px;
            transition: transform 0.2s;
            width: 100%;
        }
        
        .query-button:hover {
            transform: translateY(-2px);
        }
        
        .query-button:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }
        
        .results-section {
            margin-top: 30px;
            display: none;
        }
        
        .answer-box {
            background: #f8f9fa;
            border-left: 4px solid #667eea;
            padding: 20px;
            border-radius: 0 10px 10px 0;
            margin-bottom: 20px;
            white-space: pre-line;
        }
        
        .answer-text {
            line-height: 1.6;
            color: #333;
        }
        
        .sources-section {
            margin-top: 20px;
        }
        
        .sources-title {
            font-weight: bold;
            color: #667eea;
            margin-bottom: 10px;
        }
        
        .source-item {
            background: white;
            border: 1px solid #e1e8ed;
            border-radius: 8px;
            padding: 15px;
            margin-bottom: 10px;
            transition: box-shadow 0.2s;
        }
        
        .source-item:hover {
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        }
        
        .source-title {
            font-weight: bold;
            color: #333;
            margin-bottom: 5px;
        }
        
        .source-url {
            color: #667eea;
            text-decoration: none;
            font-size: 0.9em;
        }
        
        .source-url:hover {
            text-decoration: underline;
        }
        
        .relevance-score {
            background: #e3f2fd;
            color: #1976d2;
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 0.8em;
            float: right;
        }
        
        .loading {
            text-align: center;
            padding: 20px;
            color: #666;
        }
        
        .spinner {
            border: 3px solid #f3f3f3;
            border-top: 3px solid #667eea;
            border-radius: 50%;
            width: 30px;
            height: 30px;
            animation: spin 1s linear infinite;
            margin: 0 auto 10px;
        }
        
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        
        .error-message {
            background: #ffebee;
            color: #c62828;
            padding: 15px;
            border-radius: 8px;
            margin-top: 15px;
        }
        
        .example-queries {
            margin-top: 20px;
            padding: 20px; 
            background: #f8f9fa;
            border-radius: 10px;
        }
        
        .example-title {
            font-weight: bold;
            color: #333;
            margin-bottom: 10px;
        }
        
        .example-query {
            background: white;
            border: 1px solid #dee2e6;
            padding: 8px 12px;
            margin: 5px;
            border-radius: 6px;
            display: inline-block;
            cursor: pointer;
            transition: background-color 0.2s;
            font-size: 0.9em;
        }
        
        .example-query:hover {
            background: #e9ecef;
        }
        
        .system-badge {
            background: #fff3cd;
            color: #856404;
            padding: 8px 12px;
            border-radius: 6px;
            font-size: 0.9em;
            margin-top: 10px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤖 Intelligent Runbook Assistant</h1>
            <p>Ask questions about Meesho's runbooks and get instant answers - now with AI-powered runbook creation!</p>
            
            {% if stats %}
            <div class="stats">
                <div class="stat-item">
                    <span class="stat-number">{{ stats.total_runbooks}}</span>
                    <span class="stat-label">Runbooks</span>
                </div>
                <div class="stat-item">
                    <span class="stat-number">{{ stats.total_chunks }}</span>
                    <span class="stat-label">Knowledge Chunks</span>
                </div>
                <div class="stat-item">
                    <span class="stat-number">🔍</span>
                    <span class="stat-label">Text Search</span>
                </div>
            </div>
            {% endif %}
        </div>
        
        <div class="main-content">
            <div class="system-badge">
                💡 Using lightweight text-based search - fast and memory efficient!
            </div>
            
            <div class="query-section">
                <textarea 
                    id="queryInput" 
                    class="query-input" 
                    placeholder="Ask me anything about the runbooks... e.g., 'How to fix Jenkins pipeline failures?' or 'What to do when nodes are faulty?'"
                    rows="3"
                ></textarea>
                <button id="queryButton" class="query-button" onclick="submitQuery()">
                    Ask Question
                </button>
            </div>
            
            <div class="example-queries">
                <div class="example-title">💡 Example questions:</div>
                <span class="example-query" onclick="setQuery(this.textContent)">Jenkins pipeline failures</span>
                <span class="example-query" onclick="setQuery(this.textContent)">faulty nodes troubleshooting</span>
                <span class="example-query" onclick="setQuery(this.textContent)">incident response</span>
                <span class="example-query" onclick="setQuery(this.textContent)">deployment steps</span>
                <span class="example-query" onclick="setQuery(this.textContent)">onboarding partners</span>
                <span class="example-query" onclick="setQuery(this.textContent)">rollback procedure</span>
            </div>
            
            <div id="resultsSection" class="results-section">
                <div id="loadingIndicator" class="loading" style="display: none;">
                    <div class="spinner"></div>
                    Searching through runbooks...
                </div>
                
                                 <div id="answerSection" style="display: none;">
                     <div class="answer-box">
                         <div id="answerText" class="answer-text"></div>
                         <div id="createRunbookSection" style="display: none; margin-top: 15px;">
                             <button id="createRunbookBtn" class="query-button" onclick="createRunbook()" style="width: auto; margin-top: 0;">
                                 🤖 Create Intelligent Runbook Draft
                             </button>
                         </div>
                     </div>
                     
                     <div id="sourcesSection" class="sources-section" style="display: none;">
                         <div class="sources-title">📚 Sources:</div>
                         <div id="sourcesList"></div>
                     </div>
                 </div>
                
                <div id="errorSection" class="error-message" style="display: none;"></div>
            </div>
        </div>
    </div>

    <script>
        let currentQuery = '';
        
        function setQuery(query) {
            document.getElementById('queryInput').value = query;
        }
        
        function submitQuery(createRunbook = false) {
            const query = document.getElementById('queryInput').value.trim();
            currentQuery = query;
            
            if (!query) {
                alert('Please enter a question');
                return;
            }
            
            // Show loading
            document.getElementById('resultsSection').style.display = 'block';
            document.getElementById('loadingIndicator').style.display = 'block';
            document.getElementById('answerSection').style.display = 'none';
            document.getElementById('errorSection').style.display = 'none';
            document.getElementById('createRunbookSection').style.display = 'none';
            
            // Disable button
            const button = document.getElementById('queryButton');
            button.disabled = true;
            button.textContent = createRunbook ? '🤖 Creating Intelligent Runbook...' : 'Processing...';
            
            // Submit query
            fetch('/query', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ 
                    query: query,
                    create_runbook: createRunbook
                })
            })
            .then(response => response.json())
            .then(data => {
                // Hide loading
                document.getElementById('loadingIndicator').style.display = 'none';
                
                if (data.error) {
                    // Show error
                    document.getElementById('errorSection').textContent = data.error;
                    document.getElementById('errorSection').style.display = 'block';
                } else {
                    // Show answer
                    document.getElementById('answerText').textContent = data.answer;
                    document.getElementById('answerSection').style.display = 'block';
                    
                    // Check if we should show create runbook button
                    if (data.suggest_creation && data.can_create_runbook && !createRunbook) {
                        document.getElementById('createRunbookSection').style.display = 'block';
                    }
                    
                    // Show special styling for created runbooks
                    if (data.runbook_created) {
                        const answerBox = document.querySelector('.answer-box');
                        answerBox.style.backgroundColor = '#d4edda';
                        answerBox.style.borderColor = '#28a745';
                    } else {
                        const answerBox = document.querySelector('.answer-box');
                        answerBox.style.backgroundColor = '#f8f9fa';
                        answerBox.style.borderColor = '#667eea';
                    }
                    
                    // Show sources if available
                    if (data.sources && data.sources.length > 0) {
                        const sourcesList = document.getElementById('sourcesList');
                        sourcesList.innerHTML = '';
                        
                        data.sources.forEach(source => {
                            const sourceItem = document.createElement('div');
                            sourceItem.className = 'source-item';
                            
                            // Special styling for created runbooks
                            if (data.runbook_created) {
                                sourceItem.style.backgroundColor = '#d1ecf1';
                                sourceItem.style.borderColor = '#17a2b8';
                            }
                            
                            sourceItem.innerHTML = `
                                <div class="source-title">${source.title}</div>
                                <a href="${source.url}" target="_blank" class="source-url">${source.url}</a>
                                <span class="relevance-score">Score: ${source.relevance.toFixed(1)}</span>
                            `;
                            sourcesList.appendChild(sourceItem);
                        });
                        
                        document.getElementById('sourcesSection').style.display = 'block';
                    }
                }
            })
            .catch(error => {
                // Hide loading and show error
                document.getElementById('loadingIndicator').style.display = 'none';
                document.getElementById('errorSection').textContent = 'Error: ' + error.message;
                document.getElementById('errorSection').style.display = 'block';
            })
            .finally(() => {
                // Re-enable button
                button.disabled = false;
                button.textContent = 'Ask Question';
            });
        }
        
        function createRunbook() {
            if (!currentQuery) {
                alert('No query to create runbook for');
                return;
            }
            
            // Disable the create button
            const createBtn = document.getElementById('createRunbookBtn');
            createBtn.disabled = true;
            createBtn.textContent = '🤖 Creating Intelligent Content...';
            
            // Submit the query with create flag
            submitQuery(true);
        }
        
        // Allow Enter key to submit
        document.getElementById('queryInput').addEventListener('keypress', function(e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                submitQuery();
            }
        });
    </script>
</body>
</html>"""
    
    # Error template
    error_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Error - Runbook Assistant</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background: #f5f5f5;
            display: flex;
            align-items: center;
            justify-content: center;
            min-height: 100vh;
            margin: 0;
        }
        
        .error-container {
            background: white;
            border-radius: 10px;
            padding: 40px;
            text-align: center;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            max-width: 500px;
        }
        
        .error-icon {
            font-size: 4em;
            margin-bottom: 20px;
        }
        
        .error-title {
            color: #333;
            font-size: 1.5em;
            margin-bottom: 15px;
        }
        
        .error-message {
            color: #666;
            line-height: 1.5;
            margin-bottom: 20px;
        }
        
        .error-solution {
            background: #e3f2fd;
            padding: 15px;
            border-radius: 8px;
            margin-top: 20px;
            text-align: left;
        }
    </style>
</head>
<body>
    <div class="error-container">
        <div class="error-icon">⚠️</div>
        <h1 class="error-title">System Not Ready</h1>
        <p class="error-message">{{ error }}</p>
        
        <div class="error-solution">
            <strong>To fix this:</strong><br>
            1. Ensure runbook data is available<br>
            2. Check if devops_runbooks.json file exists<br>
            3. Restart the application
        </div>
    </div>
</body>
</html>"""
    
    # Write templates to files
    with open('templates/index.html', 'w', encoding='utf-8') as f:
        f.write(index_html)
    
    with open('templates/error.html', 'w', encoding='utf-8') as f:
        f.write(error_html)

if __name__ == '__main__':
    # Create templates directory and files if they don't exist
    os.makedirs('templates', exist_ok=True)
    
    # Create the HTML templates
    create_templates()
    
    print("🌐 Starting Simple Runbook RAG Web Application...")
    print("🔗 Open http://localhost:5003 in your browser")
    
    app.run(debug=True, host='0.0.0.0', port=5003) 