#!/usr/bin/env python3

import requests
import json
import re
from datetime import datetime
from typing import Dict, List, Any
from requests.auth import HTTPBasicAuth
from config import CONFLUENCE_BASE_URL, EMAIL, API_TOKEN, SPACE_KEY

class IntelligentRunbookCreator:
    def __init__(self, rag_system=None):
        """Initialize the intelligent runbook creator"""
        self.base_url = CONFLUENCE_BASE_URL
        self.email = EMAIL
        self.api_token = API_TOKEN
        self.space_key = SPACE_KEY or "DEVOPS"
        self.auth = HTTPBasicAuth(self.email, self.api_token)
        self.rag_system = rag_system  # Reference to RAG system for context
        
        # Common patterns and solutions
        self.patterns = {
            'jenkins': {
                'keywords': ['jenkins', 'pipeline', 'build', 'ci/cd', 'deployment'],
                'common_issues': ['pipeline failure', 'build error', 'deployment stuck'],
                'typical_steps': [
                    'Check Jenkins console output for error messages',
                    'Verify pipeline configuration and syntax',
                    'Check resource availability (disk space, memory)',
                    'Restart Jenkins service if needed',
                    'Review recent changes to pipeline scripts'
                ]
            },
            'kubernetes': {
                'keywords': ['kubernetes', 'k8s', 'pod', 'node', 'cluster', 'kubectl'],
                'common_issues': ['pod stuck', 'node not ready', 'service unreachable'],
                'typical_steps': [
                    'kubectl get pods -n <namespace> to check pod status',
                    'kubectl describe pod <pod-name> for detailed information',
                    'kubectl logs <pod-name> to check application logs',
                    'Check node resources: kubectl top nodes',
                    'Verify service and ingress configurations'
                ]
            },
            'database': {
                'keywords': ['database', 'db', 'mysql', 'postgres', 'mongodb', 'sql'],
                'common_issues': ['connection timeout', 'slow queries', 'lock issues'],
                'typical_steps': [
                    'Check database connectivity and credentials',
                    'Monitor database performance metrics',
                    'Review slow query logs',
                    'Check for blocking processes or locks',
                    'Verify database configuration and resources'
                ]
            },
            'service': {
                'keywords': ['service', 'microservice', 'api', 'endpoint', 'server'],
                'common_issues': ['service down', 'high latency', 'error rate'],
                'typical_steps': [
                    'Check service health endpoints',
                    'Review application logs for errors',
                    'Monitor CPU, memory, and network usage',
                    'Verify dependencies and external services',
                    'Check load balancer and traffic routing'
                ]
            },
            'deployment': {
                'keywords': ['deploy', 'deployment', 'release', 'rollout'],
                'common_issues': ['deployment failed', 'rollback needed', 'environment issues'],
                'typical_steps': [
                    'Verify deployment pipeline status',
                    'Check environment-specific configurations',
                    'Validate resource availability in target environment',
                    'Review deployment logs and error messages',
                    'Perform rollback if necessary'
                ]
            }
        }
    
    def analyze_query(self, query: str) -> Dict[str, Any]:
        """Analyze the query to determine the type of issue and generate relevant content"""
        query_lower = query.lower()
        
        # Determine the primary category
        primary_category = None
        matched_keywords = []
        
        for category, info in self.patterns.items():
            for keyword in info['keywords']:
                if keyword in query_lower:
                    matched_keywords.append(keyword)
                    if not primary_category:
                        primary_category = category
        
        # Determine the type of action/issue
        action_type = 'troubleshooting'  # default
        if any(word in query_lower for word in ['how to', 'steps to', 'procedure', 'guide']):
            action_type = 'procedure'
        elif any(word in query_lower for word in ['fix', 'resolve', 'troubleshoot', 'debug']):
            action_type = 'troubleshooting'
        elif any(word in query_lower for word in ['deploy', 'install', 'setup', 'configure']):
            action_type = 'setup'
        elif any(word in query_lower for word in ['monitor', 'check', 'verify', 'validate']):
            action_type = 'monitoring'
        
        return {
            'primary_category': primary_category or 'general',
            'action_type': action_type,
            'matched_keywords': matched_keywords,
            'query_intent': self.extract_intent(query)
        }
    
    def extract_intent(self, query: str) -> str:
        """Extract the main intent/problem from the query"""
        # Remove common question words and extract the core issue
        query_clean = re.sub(r'(how to|what to do|steps to|procedure for|guide for|troubleshoot|fix|resolve)', '', query.lower())
        query_clean = re.sub(r'[^\w\s]', '', query_clean).strip()
        
        return query_clean
    
    def generate_intelligent_content(self, query: str, analysis: Dict[str, Any]) -> str:
        """Generate intelligent content based on query analysis"""
        
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        category = analysis['primary_category']
        action_type = analysis['action_type']
        intent = analysis['query_intent']
        
        # Get relevant patterns
        pattern_info = self.patterns.get(category, self.patterns['service'])
        
        # Generate specific content based on analysis
        purpose_content = self.generate_purpose(query, analysis)
        prerequisites_content = self.generate_prerequisites(category, analysis)
        quick_solution_content = self.generate_quick_solution(query, analysis)
        detailed_steps_content = self.generate_detailed_steps(category, analysis)
        troubleshooting_content = self.generate_troubleshooting(category, analysis)
        escalation_content = self.generate_escalation(category)
        related_docs_content = self.generate_related_docs(category, analysis)
        
        template = f"""<h1>🔧 {query}</h1>

<div class="confluence-information-macro confluence-information-macro-note">
<div class="confluence-information-macro-body">
<p><strong>📝 Status:</strong> <span style="color: rgb(255,86,48);"><strong>DRAFT - AUTO-GENERATED</strong></span></p>
<p><strong>📅 Created:</strong> {current_time}</p>
<p><strong>👤 Requested by:</strong> User via Runbook Assistant</p>
<p><strong>🔍 Original Query:</strong> {query}</p>
<p><strong>🏷️ Category:</strong> {category.title()}</p>
<p><strong>🎯 Type:</strong> {action_type.title()}</p>
</div>
</div>

<h2>📋 Overview</h2>
<p>This runbook provides guidance for: <strong>{intent}</strong></p>
<p>This runbook was automatically generated based on the query "{query}" and includes intelligent suggestions based on common patterns and best practices.</p>

<h2>🎯 Purpose</h2>
{purpose_content}

<h2>📚 Prerequisites</h2>
{prerequisites_content}

<h2>⚡ Quick Solution</h2>
{quick_solution_content}

<h2>🔧 Detailed Steps</h2>
{detailed_steps_content}

<h2>✅ Verification</h2>
<p>To verify the solution worked:</p>
<ul>
<li>Test the functionality that was originally failing</li>
<li>Monitor relevant metrics and logs for a period</li>
<li>Confirm no related error messages appear</li>
<li>Validate that dependent services are functioning normally</li>
</ul>

<h2>🚨 Troubleshooting</h2>
{troubleshooting_content}

<h2>📞 Escalation</h2>
{escalation_content}

<h2>🔗 Related Documentation</h2>
{related_docs_content}

<div class="confluence-information-macro confluence-information-macro-warning">
<div class="confluence-information-macro-body">
<p><strong>⚠️ Action Required - DEVOPS Team:</strong></p>
<ul>
<li>📝 Review and validate the auto-generated content above</li>
<li>✏️ Add specific details, commands, and environment-specific information</li>
<li>🔍 Verify all steps are accurate for your infrastructure</li>
<li>✅ Remove this warning when runbook is reviewed and complete</li>
<li>🏷️ Add appropriate labels for discoverability</li>
<li>🔄 Update the Runbook Assistant index after completion</li>
</ul>
</div>
</div>

<hr/>
<p><em>Auto-generated by Meesho Runbook Assistant on {current_time}</em></p>
<p><em>Content generated using intelligent analysis of query: "{query}"</em></p>"""

        return template
    
    def generate_purpose(self, query: str, analysis: Dict[str, Any]) -> str:
        """Generate purpose section based on query analysis"""
        category = analysis['primary_category']
        action_type = analysis['action_type']
        
        if action_type == 'troubleshooting':
            return f"""<p>This runbook helps you diagnose and resolve issues related to: <strong>{analysis['query_intent']}</strong></p>
<p>Use this runbook when you encounter problems with {category} systems that match the described scenario.</p>"""
        
        elif action_type == 'procedure':
            return f"""<p>This runbook provides step-by-step procedures for: <strong>{analysis['query_intent']}</strong></p>
<p>Follow this runbook when you need to perform {category}-related tasks or operations.</p>"""
        
        elif action_type == 'setup':
            return f"""<p>This runbook guides you through setting up or configuring: <strong>{analysis['query_intent']}</strong></p>
<p>Use this runbook for initial setup, configuration changes, or deployment tasks.</p>"""
        
        else:
            return f"""<p>This runbook covers procedures and troubleshooting for: <strong>{analysis['query_intent']}</strong></p>
<p>Reference this runbook for both preventive actions and reactive problem-solving.</p>"""
    
    def generate_prerequisites(self, category: str, analysis: Dict[str, Any]) -> str:
        """Generate prerequisites based on category"""
        common_prereqs = {
            'jenkins': [
                'Access to Jenkins dashboard with appropriate permissions',
                'Understanding of your CI/CD pipeline configuration',
                'Access to relevant Git repositories',
                'Knowledge of your deployment environments'
            ],
            'kubernetes': [
                'kubectl configured with cluster access',
                'Appropriate RBAC permissions for the namespace',
                'Understanding of your cluster architecture',
                'Access to monitoring dashboards (Grafana, etc.)'
            ],
            'database': [
                'Database connection credentials',
                'Appropriate database permissions',
                'Access to database monitoring tools',
                'Understanding of your database schema'
            ],
            'service': [
                'Access to service monitoring dashboards',
                'Understanding of service architecture',
                'Access to application logs',
                'Knowledge of service dependencies'
            ],
            'deployment': [
                'Access to deployment pipelines',
                'Understanding of environment configurations',
                'Appropriate permissions for target environments',
                'Access to rollback procedures'
            ]
        }
        
        prereqs = common_prereqs.get(category, [
            'Appropriate system access and permissions',
            'Understanding of the system architecture',
            'Access to relevant monitoring and logging tools'
        ])
        
        html = "<ul>\n"
        for prereq in prereqs:
            html += f"<li>{prereq}</li>\n"
        html += "</ul>"
        
        return html
    
    def generate_quick_solution(self, query: str, analysis: Dict[str, Any]) -> str:
        """Generate quick solution based on common patterns"""
        category = analysis['primary_category']
        
        quick_solutions = {
            'jenkins': "Check the Jenkins console output for the failed job, look for obvious errors like missing dependencies or configuration issues, and restart the job if it's a transient failure.",
            
            'kubernetes': "Use `kubectl get pods` to check pod status, then `kubectl describe pod <pod-name>` to get detailed information about any issues.",
            
            'database': "Verify database connectivity with a simple connection test, check for any obvious resource constraints (CPU, memory, disk), and review recent error logs.",
            
            'service': "Check the service health endpoint if available, review recent application logs for errors, and verify that all dependencies are healthy.",
            
            'deployment': "Check the deployment pipeline status, verify that all prerequisites are met, and ensure the target environment has sufficient resources."
        }
        
        solution = quick_solutions.get(category, "Identify the immediate symptoms, check relevant logs and monitoring dashboards, and verify that all dependencies are functioning properly.")
        
        return f"<p>{solution}</p>"
    
    def generate_detailed_steps(self, category: str, analysis: Dict[str, Any]) -> str:
        """Generate detailed steps based on category and patterns"""
        pattern_info = self.patterns.get(category, self.patterns['service'])
        steps = pattern_info['typical_steps']
        
        html = "<ol>\n"
        for i, step in enumerate(steps, 1):
            html += f"""<li><strong>Step {i}:</strong> {step}
<ul>
<li><em>Expected result:</em> [DEVOPS: Please add expected outcome]</li>
<li><em>If this fails:</em> [DEVOPS: Please add troubleshooting for this step]</li>
</ul>
</li>\n"""
        
        html += """<li><strong>Additional Steps:</strong> [DEVOPS: Please add any environment-specific steps]
<ul>
<li><em>Commands to run:</em> [Add specific commands]</li>
<li><em>Configuration files to check:</em> [Add file paths]</li>
</ul>
</li>\n"""
        html += "</ol>"
        
        return html
    
    def generate_troubleshooting(self, category: str, analysis: Dict[str, Any]) -> str:
        """Generate troubleshooting table based on common issues"""
        pattern_info = self.patterns.get(category, self.patterns['service'])
        common_issues = pattern_info['common_issues']
        
        html = """<table class="wrapped">
<colgroup>
<col/>
<col/>
<col/>
</colgroup>
<tbody>
<tr>
<th>Problem</th>
<th>Possible Causes</th>
<th>Solution</th>
</tr>\n"""
        
        # Add common issues for this category
        issue_solutions = {
            'jenkins': [
                ('Pipeline fails to start', 'Missing permissions, locked resources', 'Check Jenkins agent availability and permissions'),
                ('Build timeouts', 'Insufficient resources, network issues', 'Increase timeout values, check resource allocation'),
                ('Artifact upload fails', 'Storage space, network connectivity', 'Verify artifact repository accessibility')
            ],
            'kubernetes': [
                ('Pod stuck in Pending', 'Resource constraints, scheduling issues', 'Check node resources and pod requirements'),
                ('Pod CrashLoopBackOff', 'Application errors, configuration issues', 'Review pod logs and configuration'),
                ('Service unreachable', 'Network policies, DNS issues', 'Verify service configuration and network connectivity')
            ],
            'database': [
                ('Connection timeout', 'Network issues, database overload', 'Check network connectivity and database performance'),
                ('Slow queries', 'Missing indexes, resource constraints', 'Analyze query execution plans and optimize'),
                ('Lock conflicts', 'Long-running transactions', 'Identify blocking processes and optimize transactions')
            ]
        }
        
        category_issues = issue_solutions.get(category, [
            ('Service unavailable', 'Multiple possible causes', 'Follow systematic diagnosis steps'),
            ('Performance degradation', 'Resource constraints or configuration', 'Monitor metrics and adjust configuration'),
            ('Configuration errors', 'Recent changes or environment drift', 'Review recent changes and validate configuration')
        ])
        
        for problem, cause, solution in category_issues:
            html += f"""<tr>
<td>{problem}</td>
<td>{cause}</td>
<td>{solution}</td>
</tr>\n"""
        
        html += """<tr>
<td><em>[DEVOPS: Add specific issues]</em></td>
<td><em>[Add root causes]</em></td>
<td><em>[Add specific solutions]</em></td>
</tr>
</tbody>
</table>"""
        
        return html
    
    def generate_escalation(self, category: str) -> str:
        """Generate escalation information based on category"""
        escalation_map = {
            'jenkins': ('DevOps Team', '#devops-support', 'CI/CD Pipeline Team'),
            'kubernetes': ('Platform Team', '#k8s-support', 'Infrastructure Team'),
            'database': ('Database Team', '#db-support', 'Data Platform Team'),
            'service': ('Service Owner Team', '#service-support', 'Application Team'),
            'deployment': ('Release Team', '#release-support', 'DevOps Team')
        }
        
        primary, channel, secondary = escalation_map.get(category, ('Platform Team', '#general-support', 'DevOps Team'))
        
        return f"""<ul>
<li><strong>Primary Contact:</strong> {primary}</li>
<li><strong>Secondary Contact:</strong> {secondary}</li>
<li><strong>Slack Channel:</strong> {channel}</li>
<li><strong>Emergency Escalation:</strong> [DEVOPS: Add emergency contact procedures]</li>
</ul>"""
    
    def generate_related_docs(self, category: str, analysis: Dict[str, Any]) -> str:
        """Generate related documentation links"""
        # This would ideally search existing runbooks for related content
        return f"""<ul>
<li><em>[DEVOPS: Add links to related {category} runbooks]</em></li>
<li><em>[Add links to system documentation]</em></li>
<li><em>[Add links to monitoring dashboards]</em></li>
<li><em>[Add links to configuration management]</em></li>
</ul>

<p><strong>Auto-suggested related topics:</strong></p>
<ul>
<li>{category.title()} troubleshooting guides</li>
<li>General system health monitoring</li>
<li>Emergency response procedures</li>
</ul>"""
    
    def create_intelligent_runbook(self, query: str, user_context: str = None) -> dict:
        """Create an intelligent runbook with generated content"""
        
        print(f"📝 Creating intelligent runbook for query: '{query}'")
        
        # Analyze the query
        analysis = self.analyze_query(query)
        print(f"🔍 Analysis: {analysis}")
        
        # Generate page title
        page_title = f"Runbook: {query}"
        if len(page_title) > 100:
            page_title = f"Runbook: {query[:80]}..."
        
        # Generate intelligent content
        page_content = self.generate_intelligent_content(query, analysis)
        
        # Prepare the page data
        page_data = {
            "type": "page",
            "title": page_title,
            "space": {
                "key": self.space_key
            },
            "body": {
                "storage": {
                    "value": page_content,
                    "representation": "storage"
                }
            },
            "metadata": {
                "labels": [
                    {"name": "runbook"},
                    {"name": "auto-generated"},
                    {"name": "intelligent-content"},
                    {"name": f"category-{analysis['primary_category']}"},
                    {"name": f"type-{analysis['action_type']}"},
                    {"name": "needs-review"}
                ]
            }
        }
        
        # Create the page
        create_url = f"{self.base_url}/wiki/rest/api/content"
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.post(
                create_url,
                auth=self.auth,
                headers=headers,
                data=json.dumps(page_data),
                timeout=30
            )
            
            if response.status_code == 200:
                created_page = response.json()
                page_id = created_page.get("id")
                page_url = f"{self.base_url}/wiki/spaces/{self.space_key}/pages/{page_id}"
                
                print(f"✅ Successfully created intelligent runbook: {page_id}")
                
                return {
                    "success": True,
                    "page_id": page_id,
                    "page_url": page_url,
                    "page_title": page_title,
                    "message": f"Created intelligent runbook with auto-generated content: {page_title}",
                    "analysis": analysis,
                    "generated_runbook": page_content   # <-- Add this key here
                }
            
            else:
                print(f"❌ Failed to create page: {response.status_code}")
                return {
                    "success": False,
                    "error": f"Failed to create page: {response.status_code}",
                    "message": "Could not create runbook page in Confluence"
                }
                
        except requests.exceptions.RequestException as e:
            print(f"❌ Error creating page: {e}")
            return {
                "success": False,
                "error": str(e),
                "message": "Network error while creating runbook page"
            }

def main():
    """Test the intelligent runbook creator"""
    creator = IntelligentRunbookCreator()
    
    # Test with different types of queries
    test_queries = [
        "How to fix Jenkins pipeline failures in production",
        "What to do when Kubernetes pods are stuck in pending state",
        "Steps to troubleshoot database connection timeouts",
        "How to resolve high memory usage in microservices"
    ]
    
    for query in test_queries:
        print(f"\n{'='*80}")
        print(f"Testing query: {query}")
        analysis = creator.analyze_query(query)
        print(f"Analysis: {analysis}")
        
        # Uncomment to actually create the runbooks
        # result = creator.create_intelligent_runbook(query)
        # print(f"Result: {result}")

if __name__ == "__main__":
    main() 