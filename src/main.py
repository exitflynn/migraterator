import os
import json
import sys
from terraform_analyser import Terraformanalyser
from kubernetes_analyser import Kubernetesanalyser
from risk_assessor import RiskAssessor
from report_generator import ReportGenerator
from utils.github_utils import get_pr_files

def main():
    # Get environment variables
    repo_name = os.environ.get("REPO_NAME")
    pr_number = os.environ.get("PR_NUMBER")
    github_token = os.environ.get("GITHUB_TOKEN")
    
    if not all([repo_name, pr_number, github_token]):
        print("Missing required environment variables")
        sys.exit(1)
    
    # Get the list of files changed in the PR
    pr_files = get_pr_files(repo_name, pr_number, github_token)
    
    # Initialize analysers
    repo_path = os.environ.get("GITHUB_WORKSPACE", ".")
    
    terraform_analyser = None
    kubernetes_analyser = None
    
    # Check if there are Terraform files in the PR
    if any(f.endswith('.tf') for f in pr_files):
        print("analysing Terraform changes...")
        terraform_analyser = Terraformanalyser(repo_path, pr_files)
        terraform_analysis = terraform_analyser.analyse_changes()
    else:
        terraform_analysis = None
    
    # Check if there are Kubernetes files in the PR
    if any(f.endswith(('.yaml', '.yml')) for f in pr_files):
        print("analysing Kubernetes changes...")
        kubernetes_analyser = Kubernetesanalyser(repo_path, pr_files)
        kubernetes_analysis = kubernetes_analyser.analyse_changes()
    else:
        kubernetes_analysis = None
    
    # Perform risk assessment
    print("Performing risk assessment...")
    risk_assessor = RiskAssessor(terraform_analysis, kubernetes_analysis)
    risk_assessment = risk_assessor.generate_assessment()
    
    # Generate report
    print("Generating migration report...")
    report_generator = ReportGenerator(terraform_analysis, kubernetes_analysis, risk_assessment)
    report_markdown = report_generator.generate_markdown_report()
    
    # Save the report to a file (will be used by the GitHub Action to comment on the PR)
    with open('migration_report.md', 'w') as f:
        f.write(report_markdown)
    
    print("Migration report generated successfully")
    return 0

if __name__ == "__main__":
    sys.exit(main()) 