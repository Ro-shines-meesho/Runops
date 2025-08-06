
import json
from collections import defaultdict
from simple_rag import SimpleRAGSystem

# Load all categories and subcategories
categories = {
    "5xx": {
        "description": "5xx related issues and discussion",
        "subcategories": [
            "503 and 504 Errors \u2013 Thread contains references to 503 and 504 errors, indicating a 5xx error",
            "EKS Infrastructure Issues \u2013 Thread mentions eks infra dashboard showing pod going unavailable, indicating EKS infrastructure issues",
            "GCP Hardware Error \u2013 Thread specifies that the issue is caused by a host error from GCP's hardware",
            "Production Impacting \u2013 Thread mentions production impacting, indicating that the 5xx error had an impact on production services",
            "503 Unavailable Service \u2013 Service unavailable error in Prism APIs",
            "Prism API Error \u2013 Invalid response from Prism SDK backend",
            "Retries Not Working \u2013 3 retries with backoff not resolving the issue"
        ]
    },
    "Akamai/Security": {
        "description": "Akamai/Security related issues and discussion",
        "subcategories": [
            "Bucket Access Control \u2013 Checking public accessibility of files in a Google Cloud Storage bucket.",
            "DNS Configuration \u2013 Verifying DNS settings for accessing files publicly.",
            "DevOps POCs \u2013 Connecting with DevOps POCs to resolve the issue.",
            "ER Integration with Meesho \u2013 Initial message regarding ER integration with Meesho and whitelisting IPs for data ingestion",
            "IP Whitelisting Request \u2013 Request to whitelist specific IPs for data ingestion from the gateway service",
            "Security Review Ticket SECREV-2906 \u2013 Reference to a security ticket and confirmation of all open points related to security review",
            "Confirmation of IP Whitelisting \u2013 Verification if the IPs were whitelisted successfully",
            "Planned Deployment and Confirmation \u2013 Request for confirmation before a planned deployment, ensuring that the task was completed",
            "Existing List for ER \u2013 Discussion about leveraging an existing list or creating a new one for ER integration",
            "Custom Rule Implementation \u2013 Creation of a custom rule for specific paths and confirmation of its implementation",
            "Cloud CDN Purge Request \u2013 Request to purge a URL from Cloud Content Delivery Network (CDN)",
            "Asset Manifest Caching \u2013 Discussion around caching an asset manifest file in Cloud CDN",
            "API mapping updates \u2013 Request to update API mapping at Akamai level for meesho-pow-service hosted at a specific URL",
            "DNS resolution issues \u2013 Discussion on DNS resolution issues and its impact on origin on Akamai",
            "Onboarding new APIs \u2013 Request to onboard new APIs to directly hit through a specific URL",
            "Edge proxy configuration \u2013 Discussion on configuring edge proxy for sales environment",
            "Meeting coordination \u2013 Scheduling a meeting to discuss and resolve the API mapping issue",
            "Akamai Onboarding \u2013 Plan to onboard this service to Akamai for security and WAF validation",
            "OAuth Login Configuration \u2013 Configuring Google login with no domain restriction for public accessibility",
            "Certificate Creation \u2013 Creating a certificate for secure deployment",
            "Audience Feature Review \u2013 Reviewing the audience feature to set the desired users who can use OAuth for SSO",
            "Access Blocked \u2013 FortiGuard Intrusion Prevention - Access Blocked",
            "403 Error \u2013 Your Access to this Webpage Link is Restricted",
            "Invalid Request \u2013 Web Page Blocked due to Internet usage policy violation",
            "Network Connectivity Issue \u2013 Unpredictable response from terminal and incorrect response in Postman",
            "URL Whitelisting Required \u2013 Need to whitelist URLs <http://api.meesholink.com|api.meesholink.com> and <http://stg-api.meesholink.com|stg-api.meesholink.com>",
            "Endpoint Whitelisting Request \u2013 Request to expose a specific endpoint publicly",
            "Path Whitelisting Query \u2013 Inquiry about which path needs to be whitelisted for public accessibility",
            "EP Sharing Request \u2013 Request to share the endpoint URL for whitelisting",
            "Testing and Validation \u2013 Discussion about testing and validating changes before deployment"
        ]
    },
    "App Stability": {
        "description": "App Stability related issues and discussion",
        "subcategories": [
            "Redis Connectivity Issue \u2013 Resolved issue related to Redis connection dropping due to lack of whitelisting in supply CIDR",
            "Production Issue Resolution \u2013 Issue resolved with help from team members and community engagement",
            "CPU usage issues \u2013 Thread mentions high CPU usage and autoscaling not adding more pods",
            "Autoscaling configuration \u2013 Thread discusses setting CPU autoscaling to 70%",
            "Infra buddy app tracking \u2013 Thread mentions using the infra buddy app to track issues",
            "Incomplete information \u2013 Thread suggests that information is not clear and complete",
            "Off-line team member \u2013 Thread mentions one team member being OOO and unable to fill the form",
            "No production impact \u2013 Thread confirms that decreased CPU autoscaling did not break prod",
            "P0 Service Alert \u2013 Indicates a high-priority service issue that requires immediate attention",
            "Canary Failure Request \u2013 Request to investigate and resolve an issue affecting a critical service (canary deployment)",
            "Fast Track Request for P0 Issue \u2013 Request to expedite ticket resolution due to the high severity of the issue",
            "Cache Management \u2013 Requesting cache clearance for a specific API path",
            "Stale Data Resolution \u2013 Stale data present in the CDN cache, requiring clearance",
            "Node Performance Issue \u2013 Latency spike observed on a specific node",
            "Grafana Visualization Requested \u2013 User requested visualization of performance data via Grafana link",
            "Node Identification Requested \u2013 User asked for identification of the affected node (gke-k8s-supply-prd-a-np-supl-xsupl-su-ae59c9ba-m6kj)",
            "Instance CPU Utilization Inconsistencies \u2013 Discussion about discrepancies between Observability window and htop/I/O wait metrics, highlighting potential issues with GCP's CPU utilization calculation",
            "IO-Bound Performance Bottlenecks \u2013 Explanation of I/O-bound system behavior and its impact on perceived CPU utilization",
            "GCP Console CPU Utilization Limitations \u2013 Clarification that GCP's CPU utilization metrics only consider user + system time, excluding I/O wait",
            "Ops-Agent Solution for Accurate Metrics \u2013 Recommendation to enable ops-agent for accurate CPU utilization metrics, similar to `top`, `htop`, or `node-exporter`",
            "Long-Term Performance Concerns \u2013 Warning that hypervisor overhead might affect performance in the long term if not addressed",
            "Deployment Failure \u2013 Main instance not processing further requests, requires urgent attention",
            "Argo Supply Chain Issue \u2013 Prd-agent-support-aggregator resource unavailable or failed to deploy",
            "Monitoring Error \u2013 Ringmaster.meeshogcp.in application status link not updating correctly",
            "Pager Alerts \u2013 Discussed pager alerts for `/api/1.0/affiliate/product/third-party/` API path",
            "Service Exclusion \u2013 Request to exclude an API path from pager alerts without impacting the service",
            "No Impact Selection \u2013 Discussion around selecting 'No Services Impacted' option in the bot",
            "Alert Sharing \u2013 Request to share the alert for `/api/1.0/affiliate/product/third-party/` API path",
            "VM Disk Space Issues \u2013 Monitoring disk space and alerting on full disks",
            "Alerting on VM Status \u2013 Receiving alerts for specific VMs or instance status changes"
        ]
    },
    "CI/CD": {
        "description": "CI/CD related issues and discussion",
        "subcategories": [
            "Merge Request Failure \u2013 The thread mentions a GitHub pull request that is failing, indicating a CI/CD issue",
            "Stg Environment Check \u2013 Checks are failing on the staging environment, preventing PR from being merged",
            "Revised PR Attempt \u2013 Attempted to resolve issues by opening a new PR, but still facing failures",
            "Staging deployment issues \u2013 Discusses a failed staging deployment and urgency to deploy",
            "PR conversion to draft \u2013 Describes converting pull request to draft as a workaround",
            "Validation failures in checks \u2013 Mentions validation failures occurring after certain duration, indicating potential retry issues",
            "SonarQube Analysis Failure \u2013 Failed SonarScanner analysis due to server error (503)",
            "Maven Build Failure \u2013 Discussion around a failing Maven build",
            "PR Stuck in Checks \u2013 PR stuck in stage checks, preventing deployment",
            "CI/CD Pipeline Issue \u2013 Issue with CI/CD pipeline causing PR to be stuck",
            "GitHub Pull Request Failure \u2013 Error in building Docker image or code review",
            "Merge Request Issues \u2013 Thread mentions a specific merge request and its related issues",
            "Deployment Environments \u2013 Discussion around deployment environments, such as pre-prod and stg",
            "Status Links \u2013 Sharing of CI/CD status links for specific repositories or applications",
            "Bypassing Deployments \u2013 Request to bypass deployments or deployment stages for specific services or environments",
            "Manual Deployment Issues \u2013 Discussion around manually deploying services and the issues that arise",
            "Failed Check on PR \u2013 Discussion about a failing check on a pull request",
            "Staging Deployment Confirmation \u2013 Verification of staging deployment status",
            "Jenkins Link Provided \u2013 Link to Jenkins job for further investigation",
            "PR Merging Requested \u2013 Request to merge the pull request with failed check",
            "Pull Request Failing Quality Gate \u2013 Quality gate issues for a specific pull request",
            "GitHub Link Present with Failure \u2013 The thread contains a GitHub link and mentions failure, indicating a CI/CD issue.",
            "Staging Deployment Failure \u2013 Deployment blocked due to staging deployment failure",
            "Multiple Attempts Required \u2013 Needed to retry marking PR draft and review multiple times",
            "GitHub Merging Issues \u2013 Thread mentions GitHub link and refers to merging a pull request, indicating CI/CD pipeline failure",
            "Check Failure Analysis \u2013 Discussion around the nature of the check failure and its potential impact on merging",
            "Repository Configuration Issues \u2013 Mention of config taml being in the wrong path, indicating a configuration-related issue",
            "Service Owner Collaboration \u2013 Request to connect with the Service Owner (Devesh Agnihotri) for further clarification and resolution",
            "Approval Workaround \u2013 Mention of being able to get one approval and merge the PR, indicating a temporary workaround",
            "GitHub PR Review Request \u2013 Request to review a specific pull request"
        ]
    },
    "Canary": {
        "description": "Canary related issues and discussion",
        "subcategories": [
            "Redis Connectivity Issues \u2013 Failure to connect to Redis instance during canary deployment",
            "Pod Failure \u2013 Canary pod failed due to Redis connection issues or other reasons",
            "Deployment Scaled to Zero \u2013 Canary analysis failed, resulting in deployment being scaled down to zero",
            "Whitelisting CIDR Ranges \u2013 Need to whitelist specific CIDR ranges for Redis connectivity",
            "New Code Issues \u2013 New code deployed during canary causing unexpected issues",
            "Serving Pod Connectivity \u2013 Connectivity issues affecting serving pods in production environment",
            "Error Analysis \u2013 Analyzing errors and exceptions occurring during canary deployment",
            "Invalid error message \u2013 Error message indicating issue with canary deployment",
            "Rollout-service errors \u2013 Errors occurring during the rollout of the canary deployment",
            "Namespace issues \u2013 Problems with namespace or naming conventions in the canary deployment",
            "Canary Deployment Failure \u2013 Deployment of new build to osm-supply-read cluster failed due to promotion issues",
            "5xx Error During Canary Rollout \u2013 Canary pods experienced 5xx errors during rollout, causing rollback",
            "Config Changes Verification \u2013 Verification of config changes made to prevent similar issues in the future",
            "Node Unavailability Impact \u2013 Newly deployed pods not coming up due to node unavailability",
            "Taxonomy CICD Job Failure \u2013 Jenkins job failure for taxonomy-cicd, likely causing canary deployment issues",
            "Retriggering Canary \u2013 Canary retriggered to resolve deployment issue",
            "Monitoring and Verification \u2013 Monitoring and verifying the canary deployment to ensure successful rollout",
            "Canary Pod Restarted \u2013 Discussion about a specific canary pod that became unavailable and restarted",
            "Canary Analysis Failed \u2013 Canary analysis failed, indicating issues with the canary deployment",
            "Aborted Canary Deployment \u2013 The canary deployment was aborted due to failures in the canary",
            "Troubleshooting Canary Pod Issues \u2013 Investigation into why a specific canary pod became unavailable and restarted",
            "Request for Canopy Retry \u2013 Request to retry the deployment once the issues are resolved",
            "Delayed Processing \u2013 PR taking long time for staging checks to complete",
            "Input Availability Issue \u2013 Canary not progressing even with input provided",
            "Replicaset Update \u2013 New primary replicaset seen after canary completion",
            "Canary Analysis Request Rollback \u2013 The thread starts with a request to roll back the start canary analysis request, indicating an issue with the canary deployment.",
            "Unresolved Pod Issue \u2013 A pod is still active in the canary environment after rolling back the analysis request, requiring investigation and resolution.",
            "Application-Side Error \u2013 The new code is encountering an error, which needs to be checked from the application side.",
            "Log Investigation \u2013 Checking pod logs was suggested as a possible solution to resolve the issue, but the investigation didn't yield any results.",
            "Different Thread Logs \u2013 Logs shared by someone in this thread are not relevant for this specific canary deployment."
        ]
    },
    "Cleanup": {
        "description": "Cleanup related issues and discussion",
        "subcategories": [
            "Remove Unused Alerts \u2013 Thread discusses deleting unnecessary and mandatory alerts for a service.",
            "Service Deletion Request \u2013 Request to delete a service's duplicate alert",
            "Alert Threshold Adjustment \u2013 User suggests increasing threshold to ignore non-serving traffic for a short period.",
            "Service Status Inquiry \u2013 Users ask about the status of the service and when it will be deleted.",
            "Unused Service Removal \u2013 Identifying and removing unused services to optimize resource utilization",
            "Service IP Cleanup in Supply Cluster \u2013 Cleaning up service IPs in the supply cluster to ensure efficient resource allocation",
            "Removing Databridge Services \u2013 Identifying and removing unnecessary databridge services, including `data-bridge-consumer`, `data-bridge-primary`, and `data-bridge-secondary`",
            "Unused Repository Cleanup \u2013 Cleaning up unused repositories to declutter the development environment",
            "Logistics Data Viz Removal \u2013 Removing unnecessary services, including `logistics-data-viz`, to optimize resource utilization and reduce complexity",
            "Delete Unused Jobs \u2013 Request to delete old jobs from a cron",
            "Urgent Request \u2013 Cron is running on multiple pods and stressing downstream services",
            "Job List Request \u2013 Need list of jobs that need to be deleted for cleanup",
            "Long-Standing Issue \u2013 P2 issue was missed due to prioritization, now being addressed",
            "Job Age Investigation \u2013 Older than 6 months, oom killed; investigating reason for not being raised earlier",
            "App Recreate Request \u2013 Number of jobs too many to be deleted from UI; request to recreate app instead",
            "Unused Service Removal Request \u2013 Request to remove alerts for an unused service",
            "Service Decommissioning \u2013 Decommissioning of a previously used service",
            "Alert Management \u2013 Managing and removing unnecessary alerts",
            "JFrog directory deletion \u2013 Request to delete JFrog directories and corresponding instance",
            "Ticket creation \u2013 Creation of a ticket for deletion details submission",
            "Poc identification \u2013 Identification of the correct point of contact for deletion request",
            "Approval process \u2013 Getting approval from manager on the deletion ticket",
            "Unused Deployables \u2013 Request to delete or remove unused services",
            "Service Removal Requests \u2013 Thread initiated by team for service removal",
            "JIRA Ticket Creation \u2013 Manager's approval required for ticket creation",
            "DevOps POC Outreach \u2013 Non-prod issue requires DevOps POC involvement",
            "Unused Argo Deployables \u2013 Request to delete unused Argo deployable from pre-prod environment.",
            "Ticket Creation \u2013 Request to create a ticket for approval to delete the Argo deployable in both prod and pre-prod environments.",
            "Manager Approval \u2013 Need manager approval to proceed with deleting the unused Argo deployable.",
            "Infra Buddy Bot Reply \u2013 Request to reply to infra buddy bot once the ticket is created and approved."
        ]
    },
    "Deployment": {
        "description": "Deployment related issues and discussion",
        "subcategories": [
            "FMS Deployment Failure \u2013 Deployment of fms-web and cron services failed due to image pull and unpack error",
            "Cron Job Failure \u2013 Specific cron job in the deployment failed and needs to be re-deployed",
            "Docker Build Aborted \u2013 Docker build was aborted before copying to GCR, causing artifact not found error",
            "FMS Service Degraded Health \u2013 Service health is degraded due to deployment failure",
            "Argo Rollback Issues \u2013 Thread is about resolving issues with rollback feature on Argo, indicating a deployment failure.",
            "Application Rollback Failure \u2013 Specifically mentioned 'roll back' in the context of argocd-demand-prd application",
            "Deployment Tool Errors \u2013 Thread is related to deployment tool (Argo) and its functionality, indicating errors during deployment",
            "Argo deployment issues \u2013 Issues with deploying pods using Argo",
            "Ringmaster deployment confirmation \u2013 Confirmation of successful deployment from Ringmaster",
            "New pod creation failure \u2013 Failure to create new pods despite successful deployment",
            "Pod Crashing \u2013 Pod is crashing despite resolution of previous issue and addition of a module",
            "Disk Pressure Alerts \u2013 High disk usage warnings indicating potential performance issues or data corruption.",
            "Service Experiment Failure \u2013 Experiment-related service failure affecting model inference and overall application performance.",
            "Canary Promotion Failure \u2013 Deployment issue triggered by canary promotion failure",
            "Pod Distribution Skew Issue \u2013 Enabling `podDistributionSkew` led to deployment issues and 503 errors",
            "Incorrect Deployment Assumptions \u2013 Deployment was not a pod going down issue, but rather canary promotion failure",
            "Liveliness, Readiness, and Slow Start Changes \u2013 Changes made to liveliness, readiness, and slow start settings may have contributed to deployment issues",
            "Manual Deployment Error \u2013 Error during manual deployment of prd-taxonomy-indexer",
            "Sync Failure \u2013 Failure of application sync process",
            "Version Confirmation \u2013 Verification of desired version (v7.100.0) for deployment",
            "Triggered Sync \u2013 Successful triggering of sync process to deploy new pods",
            "VM Host Error \u2013 Discussion about GCP host error and its impact on VMs",
            "VM Restart and Impact on Production \u2013 Explanation of why restart caused issues in production",
            "GCP Ticket Raised for Host Error \u2013 Sharing of GCP ticket raised for the host error issue",
            "Moving VMs to New Host without Downtime \u2013 Requesting information on how GCP plans to move existing VMs to new host without downtime",
            "Identifying Scenarios where Multiple VMs are Affected \u2013 Exploration of ways to identify scenarios where multiple VMs are affected at the same time",
            "App Sync Failure \u2013 Failure to sync applications between environments",
            "Readiness Probe Failure \u2013 Failing readiness probes for application deployment",
            "Int Storefront Primary Deployment Issues \u2013 Deployment issues specific to int-storefront-primary application",
            "Prod Deployment App Sync Failure \u2013 Failure to sync applications in production environment"
        ]
    },
    "Github Merging": {
        "description": "Github Merging related issues and discussion",
        "subcategories": [
            "Pull Request Merge Successful \u2013 Successful merge of a pull request with no issues reported",
            "Pull Request Merge Requested \u2013 Request to merge a pull request sent to the team for review and approval",
            "Merge Request Handling \u2013 Thread related to merging or updating code in a repository",
            "Successful Merge \u2013 Pull request merged successfully, no issues reported",
            "Merge Request Failure Reasons \u2013 Reasons for merge request failures, including errors and timeouts",
            "Git Fetch Errors \u2013 Errors encountered while fetching code from Git repositories",
            "Repository Resource Initialization Issues \u2013 Problems initializing repository resources, such as RPC errors",
            "Manifest Generation Failures \u2013 Failures in generating manifests for source code",
            "Sync Errors During Merging \u2013 Errors encountered while syncing code during merging",
            "Timeouts During Git Operations \u2013 Timeouts experienced during Git operations, such as fetching or pulling",
            "Merge Failure Reasons \u2013 Subcategory for understanding the reasons behind failed merges",
            "PR Deployment Verification \u2013 Verifying if a PR is deployed successfully despite ringmaster-deployment-status failure",
            "Merge Request Issues \u2013 Merging PRs with approved but failing checks, requiring assistance",
            "Failing Check Identification \u2013 Team members are asking for help in identifying the failing condition in the merge request",
            "Pull Request Approval \u2013 Request for approval of a pull request",
            "Merge Request \u2013 Request for merging a specific pull request with a given number or identifier",
            "Pull Request Feedback \u2013 Request for help with reviewing or merging a pull request",
            "Multiple Pull Requests \u2013 Merging multiple pull requests in a single thread, indicating that there are multiple sets of changes to be applied.",
            "Pull Request Merge Requests \u2013 Requests to merge pull requests from GitHub",
            "Merge Confirmation \u2013 Confirmation of pull request merge",
            "Merge Blocker Investigation \u2013 Thread indicates a merge request and investigation into potential blockers",
            "PR Merge Failure Diagnosis \u2013 Thread suggests a failed merge request, requiring diagnosis",
            "Request to merge pull request \u2013 Thread initiates a request to merge a specific pull request",
            "PR merging confirmation \u2013 Confirmation of PR merge by a team member",
            "Additional instructions for merge \u2013 Request for additional actions before merging, such as syncing mrouter for prod and pre-prod environments",
            "Merge Request Created \u2013 Initial request to create a new merge request",
            "Request for Review and Merge \u2013 User explicitly asking for review and merge of the PR",
            "Pull Request Merges \u2013 Requests for merging pull requests into the main codebase",
            "Merge Requests \u2013 Thread contains a request to merge a pull request",
            "Merge Request Feedback \u2013 Request for merging a pull request with comments or questions"
        ]
    },
    "Jenkins": {
        "description": "Jenkins related issues and discussion",
        "subcategories": [
            "Failed Job \u2013 Thread started with a failed Jenkins job link",
            "Dockerfile Issue \u2013 Discussion about Dockerfile version compatibility issue",
            "Config File Update Required \u2013 Specific update required in config.yaml file for go-1.21 support",
            "Reference Requested \u2013 Thread contains a reference request to another GitHub repository",
            "Form Fill Request \u2013 End of the thread with a form fill request",
            "Failed Deployments \u2013 Deployment job failed with no further details",
            "Pipeline Issues \u2013 Points to potential problems in the Jenkins pipeline configuration",
            "Error Analysis \u2013 Replies in the thread are focused on troubleshooting and resolving the login failure error",
            "Deployment Verification \u2013 Verification of successful deployment required",
            "Input Selection \u2013 Selecting input for deployment is necessary",
            "Retries Required \u2013 Error occurred multiple times, retries are needed to resolve the issue",
            "ETCD3 Client Issues \u2013 Troubleshooting issues with ETCD3 client in Jenkins",
            "GRPCD Installation Failure \u2013 Failure to install grpcd==1.44.0 via wheel during Jenkins build process",
            "Jenkins Plugin Issues \u2013 Problems with Jenkins plugins related to ETCD3 client or GRPCD installation",
            "Build Link Sharing \u2013 Sharing the build link in the thread for further troubleshooting and investigation",
            "Maven dependencies resolution failure \u2013 Error in collecting dependencies for a project",
            "Artifact descriptor read failure \u2013 Failed to read artifact descriptor for a specific Maven package",
            "Blocked mirror for repositories \u2013 Maven repository mirroring issues preventing artifact resolution",
            "Jenkins job failed due to maven error \u2013 Job failure caused by Maven dependencies resolution issue",
            "Job Failure: Recommendation Engine CICD \u2013 Failed Jenkins job with recommendation engine CICD build stuck since 20 minutes",
            "Console Log Analysis Required \u2013 Need to analyze Jenkins console log for insights on the issue",
            "Build Restart Attempted \u2013 Re-starting the build attempt to resolve the deployment issue",
            "Job Failure \u2013 The build is failing",
            "Console Log Analysis \u2013 Provides a link to the console log for further troubleshooting and analysis",
            "Trigger Abort \u2013 Previous build triggered but was aborted due to potential issue with ringmaster trigger",
            "Throttling Due to High Deployment Volume \u2013 Error may be caused by high deployment volume and Argo's request throttling mechanism",
            "Build Stuck \u2013 The build is stuck at a specific step, possibly due to errors or network issues.",
            "Cloning Issues \u2013 The job is experiencing difficulties cloning the necessary code repositories for the build process.",
            "DevOps Helm Charts \u2013 The issue may be related to the usage of devops-helm-charts in the Jenkins job.",
            "Failed Build \u2013 Sonar run is failing in the build, indicating a job failure"
        ]
    },
    "Jira": {
        "description": "Jira related issues and discussion",
        "subcategories": [
            "Ticket Assistance \u2013 Request for assistance with a specific ticket",
            "Jenkins Link Provided \u2013 Thread contains a Jenkins link to the ticket"
        ]
    },
    "Logging/Alerting": {
        "description": "Logging/Alerting related issues and discussion",
        "subcategories": [
            "Invalid Prometheus Expression \u2013 Error parsing configuration file due to invalid Prometheus expression syntax",
            "Incorrect Alert Query \u2013 Syntax error in the alert query causing errors in vmalert pods",
            "Failed to Parse Configuration File \u2013 Error occurred while trying to parse configuration file for vmalert",
            "Unparsed Data \u2013 Unexpected token encountered during parsing, likely due to incorrect syntax or formatting",
            "Validation Error \u2013 Error messages indicating validation failures for environments prd, review, and sections",
            "Required Field Missing \u2013 Specific error indicating a required field is missing in data fetch for presto catalogs and suppliers",
            "Schema Validation Failure \u2013 Validation failed against schema application-schema.yml for sections review, review-admin, and review-consumer",
            "PagerDuty Incident \u2013 Incident reported in PagerDuty with a link",
            "Grafana Monitoring Dashboard \u2013 Link to Grafana dashboard for monitoring and analysis",
            "Memory Threshold Alert \u2013 Alert triggered due to pod memory crossing threshold",
            "Service Memory Limitation \u2013 Discussion around low memory limit for a particular service",
            "PR Request for Memory Increase \u2013 Request to increase memory limits with a link to the PR",
            "Namespace and Cluster Monitoring \u2013 Monitoring of namespace, cluster, and node-level metrics",
            "Alert Threshold Configuration \u2013 Discussion around adjusting 4xx threshold for pulse alerts",
            "Threshold Breach Notification \u2013 Investigating why no alerts were received despite threshold breach",
            "Test Alerts and Threshold Clarification \u2013 Determining if test alerts are causing false positives or misconfigurations",
            "Alert Types and Availability \u2013 Verifying functionality of different alert types (latency, 5xx, pods) for a specific service",
            "Alert Timing and Notification \u2013 Requesting information about the timing of threshold breaches and corresponding alerts",
            "Log Export Issues \u2013 Issues with exporting logs to GCS bucket",
            "GCS Bucket Troubleshooting \u2013 Troubleshooting issues related to GCS bucket",
            "Elastic Search Verification \u2013 Verifying if logs are flowing into Elastic search after restarting log collector",
            "Log Collector Restart \u2013 Restarting the log collector to fix issues with log export",
            "Metrics not visible in Grafana \u2013 Thread discusses issues with metric visibility in Grafana dashboard",
            "Digestlogger publishing issue \u2013 Discussion around digestlogger's role in publishing metrics and potential debugging required",
            "Metric duration capture inquiry \u2013 Inquiry about the duration for which a metric is captured",
            "API usage and metric emission \u2013 Thread touches on API usage and its relation to metric emission",
            "SonarQube Setup Issues \u2013 Error setting up SonarQube, requires assistance to resolve",
            "Jenkins Deployment Errors \u2013 Error in Jenkins deployment, file not found error",
            "Missing Branches in Sonarqube \u2013 Error due to missing branch in SonarQube",
            "Pulse Alert Settings \u2013 Discussion around setting up alerts for pre-prod service"
        ]
    },
    "Onboarding": {
        "description": "Onboarding related issues and discussion",
        "subcategories": [
            "GCS Configuration \u2013 Request to update experimentsData.json file in GCS bucket",
            "Cloud Storage Update \u2013 Need to update a specific JSON file in Cloud Storage",
            "JSON File Update Request \u2013 Request to update a JSON file in the specified path",
            "New Request \u2013 Initial request for assistance with a ticket",
            "Ticket Reference \u2013 Reference to an existing ticket or issue tracking ID",
            "Pagerduty Invite Sent \u2013 Invitation sent via Pagerduty for further action",
            "Merge Request Feedback \u2013 Request for assistance with merge requests",
            "Form Filling Assistance \u2013 Assistance needed to fill a form related to DEVOPS-19628",
            "New PR Support \u2013 Support for new pull requests and reviews",
            "Alert Configuration \u2013 Request to configure alerts in different Policy Directories (PDs) for the Trust-orch-layer service",
            "Namespace Management \u2013 Management of namespaces and their resources (e.g. stopping consumers)",
            "Consumer Maintenance \u2013 Temporary or permanent maintenance activities on a consumer",
            "Request for rollback \u2013 Rolling back develop branch to its second last commit",
            "Need assistance with branching \u2013 Seeking help from devops-oncall",
            "App support request \u2013 Requiring app-support-team's attention",
            "Service Onboarding Requested \u2013 Initial request to onboard a new service, including silence of alerts and full onboarding before the deadline.",
            "Alert Silencing for New Service \u2013 Request to silence alerts for a newly onboarded service until it is fully configured.",
            "Full Onboarding Required \u2013 Emphasis on completing the onboarding process to avoid false alerts and ensure proper service functioning.",
            "Service Retirements \u2013 Request to delete/remove unused services",
            "Old Service Deletion \u2013 Deleting old service files and configurations for onboarding new services",
            "Repo Maintenance \u2013 Maintaining repository structure and removing unnecessary files",
            "Access Request \u2013 Request for access to a bucket or service account",
            "Ticket Submission \u2013 Guidance on submitting a ticket for service request or issue",
            "Follow-up Request \u2013 Further clarification requested on the purpose of IP retrieval",
            "Unresolved Ticket \u2013 Ticket not resolved and requires further attention.",
            "New Employee Request \u2013 Initial onboarding request for new employee",
            "Jira Ticket Creation Required \u2013 Approval process requires creation of Jira ticket before granting access",
            "Deployment Query \u2013 Request to investigate deployment origin",
            "GitHub Commit Link \u2013 Provided GitHub commit link for context",
            "Request for Help \u2013 Request for assistance from team member"
        ]
    },
    "Other": {
        "description": "Other related issues and discussion",
        "subcategories": [
            "Trial Message Test \u2013 Initial test message without any specific context or links",
            "Prod Issue Reporting \u2013 Reporting a production issue requiring attention from team members",
            "Availability Alert \u2013 Notifying the team of availability for a production issue",
            "Issue Clarification Request \u2013 Requesting clarification on the nature of the production issue",
            "Slack Integration Issues \u2013 Thread related to Slack channel configuration and invite requests",
            "Channel Settings \u2013 Discussion about setting up a Slack channel for a service",
            "Invite Requests \u2013 Request to invite users to a Slack channel",
            "Estimation Issues \u2013 Inaccurate or unclear message estimates causing confusion",
            "Unrelated Messages \u2013 A thread with no apparent connection to any specific DevOps topic",
            "Deployment Status Query \u2013 Query about deployment status without any specific failure or error reported",
            "Merge Request Tracking \u2013 Tracking a merge request's progress with no specific issue reported",
            "Logo Request \u2013 Request for adding a specific logo to a URL",
            "Link Enhancement \u2013 Adding additional information or context to a link",
            "Audio Uploading Issue \u2013 Thread about uploading audio to GCS bucket",
            "GCS Bucket Configuration \u2013 Discussion around storing audio files in Google Cloud Storage (GCS) buckets",
            "Form Filling Request \u2013 Request to fill out a form, likely for some specific purpose or permission",
            "Link Sharing \u2013 Sharing of links and resources related to the issue",
            "Multimedia Storage \u2013 Discussion around storing multimedia files such as audio in GCS buckets",
            "Miscellaneous Queries \u2013 Thread discusses querying data points and retrieving information",
            "Service Status Inquiries \u2013 Requests for status updates on specific services or applications",
            "Service Stoppages \u2013 Notifications about services being stopped or unavailable",
            "Team Notifications \u2013 Notifications intended for specific teams or subteams",
            "Off-Topic Conversations \u2013 Discussions that are not related to DevOps, CI/CD, or technical topics",
            "General Requests \u2013 Thread contains requests for uploading a file, checking status of upload",
            "File Upload \u2013 Request to upload the 'experimentsData.json' file to Google Cloud Storage",
            "Status Updates \u2013 Replies provide status updates on resolution (Checking, Changes made)",
            "Server Cost Increase Analysis Request \u2013 Request to investigate an increase in server cost on a specific day, likely related to infrastructure or resource utilization.",
            "Superset Dashboard Link \u2013 Presence of a Superset dashboard link, potentially indicating a monitoring or analytics issue.",
            "Multiple Users Cc'd \u2013 The thread involves multiple users being cc'd, likely indicating a collaborative effort to resolve the issue.",
            "No Clear Error or Failure \u2013 The thread does not indicate a specific error or failure, making it difficult to categorize under more precise topics like Jenkins or CI/CD."
        ]
    },
    "Security": {
        "description": "Security related issues and discussion",
        "subcategories": [
            "API Whitelisting \u2013 Request to whitelist an API path to avoid 400 pager alerts",
            "Pulse Alert Management \u2013 Discussion about managing 400 alerts on Pulse for the affiliate-web service",
            "Service Exclusion \u2013 Request to exclude an API path from monitoring and alerting",
            "GitHub Fork Request \u2013 Request to raise a security check ticket for a forked external repo",
            "Repo Verification \u2013 Verification of the forked GitHub repository",
            "JIRA Ticket Creation \u2013 Creation of a JIRA ticket in SECREV project to track security check",
            "Snyk Security Issue Detection \u2013 Thread mentions Snyk security issue detection on PR and requests help",
            "PR Merging Approval \u2013 Reply suggests the PR can be merged, indicating a security issue is not blocking deployment",
            "Snyk POC Ignoring False Positives \u2013 Thread mentions doing a Proof of Concept (POC) with Snyk and asking to ignore false positives",
            "Firewall Blockage \u2013 Discussion about a blocked IP address due to FortiGuard Intrusion Prevention",
            "IT Team Involvement \u2013 Request to check with the IT team regarding the firewall blockage",
            "Webhook URL Commits \u2013 Discusses committing a Slack webhook URL",
            "TruffleHog Errors \u2013 Error occurred during TruffleHog execution, detected secrets found",
            "Security Team Involvement \u2013 Security team is responsible for managing the hook and resolving issues",
            "GitHub PR Files \u2013 Discussion about a specific GitHub pull request (127535) and its files",
            "Hardcoded Webhook Concerns \u2013 Concerns raised about hardcoded webhooks in the repository",
            "Resolution Confirmation \u2013 The issue was resolved, confirmed by participants",
            "PermissionDenied \u2013 Error message indicating permission denied for a resource",
            "IAM Permission Denied \u2013 Specifically, an IAM permission denied error occurred",
            "Service Account Access Issue \u2013 Access issue with a service account, possibly due to permissions or authentication issues",
            "Databricks Usage \u2013 Error occurred while running a script from Databricks environment",
            "Bucket Public Access Request \u2013 Request for making a bucket public for file access",
            "Authentication Discussion \u2013 Discussion on adding authentication to the file access",
            "Security Team Approval \u2013 Approval required from the Security team to make the bucket public",
            "File Content and Sensitivity \u2013 Questions about the content of the file, its sensitivity, and reasons for making it public",
            "Authentication Methodology \u2013 Discussion on how to add authentication to the file access",
            "GCS Bucket Access Issues \u2013 Discussion around Google Cloud Storage bucket access permissions",
            "Storage Objects List Permission Denied \u2013 Error message indicating lack of storage.objects.list permission",
            "Google Cloud Storage Object Creation Error \u2013 Error message indicating denied storage.objects.create permission",
            "Forbidden Access Errors \u2013 General discussion around forbidden access errors in Google Cloud Storage"
        ]
    }
}

categories.keys()


# Initialize RAG system
rag = SimpleRAGSystem()

# Load messages and replies
with open("dev-ops-buddy.Messages_replies.json") as f:
    messages_data = json.load(f)

# Flatten subcategory-to-category mapping
subcategory_to_category = {}
for cat, details in categories.items():
    for subcat in details['subcategories']:
        subcategory_to_category[subcat] = cat

# Stats tracking
category_stats = defaultdict(lambda: {
    "present": set(),
    "missing": set(),
    "messages": defaultdict(list)
})

# Matching function using simple_rag

def subcategory_has_rag_hit(subcategory):
    result = rag.process_query(subcategory)
    return result['chunks_found'] > 0

# Analyze all messages
for entry in messages_data:
    text_parts = [entry.get("parent_msg", "")]
    for reply in entry.get("replies", []):
        text_parts.append(reply.get("msg", ""))
    combined_text = " ".join(text_parts).strip().lower()

    for subcat in subcategory_to_category:
        if subcat.lower() in combined_text:
            if subcategory_has_rag_hit(subcat):
                cat = subcategory_to_category[subcat]
                category_stats[cat]["present"].add(subcat)
                category_stats[cat]["messages"][subcat].append(combined_text)

# Compute missing subcategories
for cat, details in categories.items():
    all_subcats = set(details["subcategories"])
    found = category_stats[cat]["present"]
    category_stats[cat]["missing"] = all_subcats - found

# Prepare final output
final_summary = {}
for cat, stats in category_stats.items():
    final_summary[cat] = {
        "description": categories[cat]["description"],
        "subcategories_with_runbooks": len(stats["present"]),
        "subcategories_missing_runbooks": len(stats["missing"]),
        "missing_subcategories": sorted(list(stats["missing"])),
        "matched_messages": stats["messages"]
    }

# Save summary
with open("runbook_coverage_summary.json", "w") as f:
    json.dump(final_summary, f, indent=2)

print("✅ Summary saved to 'runbook_coverage_summary.json'")