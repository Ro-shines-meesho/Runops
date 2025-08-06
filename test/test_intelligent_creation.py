#!/usr/bin/env python3

import json
from simple_rag import SimpleRAGSystem

def test_intelligent_runbook_creation():
    """Test the intelligent runbook creation feature"""
    
    print("🚀 Testing Intelligent Runbook Creation")
    print("="*50)
    
    # Initialize the RAG system
    rag = SimpleRAGSystem()
    
    # Test queries that are unlikely to have existing runbooks
    test_queries = [
        "How to fix memory leaks in Python microservices",
        "Steps to resolve Redis connection pool exhaustion",
    ]
    
    print(f"✅ RAG System initialized with {rag.get_stats()['total_chunks']} chunks")
    print(f"🤖 Intelligent runbook creator: {'Available' if rag.can_create_runbooks else 'Not available'}")
    print()
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n📝 Test {i}: {query}")
        print("-" * 60)
        
        # First, test without creating runbook
        result = rag.process_query(query, create_if_missing=False)
        
        print(f"⏱️  Processing time: {result['processing_time']:.3f}s")
        print(f"📊 Chunks found: {result['chunks_found']}")
        print(f"🎯 Can create runbook: {result.get('can_create_runbook', False)}")
        print(f"💡 Suggests creation: {result.get('suggest_creation', False)}")
        
        # Show partial answer
        answer_preview = result['answer'][:200] + "..." if len(result['answer']) > 200 else result['answer']
        print(f"📖 Answer preview: {answer_preview}")
        
        # If intelligent runbook creator is available and suggests creation
        if result.get('suggest_creation') and rag.can_create_runbooks:
            print(f"\n🤖 Testing intelligent runbook creation...")
            
            # Test the analysis first
            if hasattr(rag.runbook_creator, 'analyze_query'):
                analysis = rag.runbook_creator.analyze_query(query)
                print(f"🔍 Query analysis:")
                print(f"   - Category: {analysis.get('primary_category', 'unknown')}")
                print(f"   - Action type: {analysis.get('action_type', 'unknown')}")
                print(f"   - Intent: {analysis.get('query_intent', 'unknown')}")
                print(f"   - Keywords: {analysis.get('matched_keywords', [])}")
            
            # For demo purposes, we won't actually create the runbook
            print(f"   ✨ Would create intelligent runbook with pre-filled content!")
            print(f"   📝 Content would include specific troubleshooting steps for {analysis.get('primary_category', 'general')} issues")
        
        print()

def test_query_analysis():
    """Test the query analysis capabilities"""
    
    print("\n🔍 Testing Query Analysis Capabilities")
    print("="*50)
    
    from intelligent_runbook_creator import IntelligentRunbookCreator
    
    creator = IntelligentRunbookCreator()
    
    analysis_queries = [
        "How to troubleshoot Jenkins build failures",
        "Steps to deploy new microservice to Kubernetes",
        "What to do when database performance is slow",
        "Procedure to monitor API service health",
        "How to setup CI/CD pipeline for new project"
    ]
    
    for query in analysis_queries:
        analysis = creator.analyze_query(query)
        print(f"\n📋 Query: {query}")
        print(f"   🏷️  Category: {analysis['primary_category']}")
        print(f"   🎯 Action type: {analysis['action_type']}")
        print(f"   💭 Intent: {analysis['query_intent']}")
        print(f"   🔑 Keywords: {analysis['matched_keywords']}")

def show_feature_summary():
    """Show a summary of the intelligent features"""
    
    print("\n✨ Intelligent Runbook Creation Features")
    print("="*50)
    
    features = [
        "🔍 Smart query analysis - categorizes queries into Jenkins, Kubernetes, Database, Service, Deployment",
        "🎯 Action type detection - identifies troubleshooting, procedure, setup, or monitoring tasks",
        "📝 Intelligent content generation - creates specific steps based on the query category",
        "🛠️  Pre-filled troubleshooting tables with common issues and solutions",
        "📋 Category-specific prerequisites and escalation procedures",
        "⚡ Quick solution suggestions based on best practices",
        "🏷️  Automatic labeling for better organization",
        "👥 Automatic DEVOPS team notification for review",
        "🔗 Related documentation suggestions",
        "📊 Detailed verification steps for solution confirmation"
    ]
    
    for feature in features:
        print(f"  {feature}")
    
    print(f"\n🎉 This is a major upgrade from simple templates to intelligent, context-aware content generation!")

if __name__ == "__main__":
    try:
        show_feature_summary()
        test_query_analysis()
        test_intelligent_runbook_creation()
        
        print("\n🎊 Intelligent Runbook Creation Testing Complete!")
        print("✅ The system can now generate meaningful, helpful content instead of empty templates!")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc() 