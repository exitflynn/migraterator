import os
import sys
from src.terraform_analyser import Terraformanalyser
from src.kubernetes_analyser import Kubernetesanalyser
from src.risk_assessor import RiskAssessor
from src.report_generator import ReportGenerator

def main():
    # Get the repository path
    repo_path = os.environ.get("GITHUB_WORKSPACE", ".")
    
    # For local testing, we'll manually specify the files
    pr_files = []
    for root, dirs, files in os.walk(repo_path):
        for file in files:
            if file.endswith('.tf') or file.endswith('.yaml') or file.endswith('.yml'):
                pr_files.append(os.path.join(root, file))
    
    terraform_analyser = None
    kubernetes_analyser = None
    
    # Check if there are Terraform files
    if any(f.endswith('.tf') for f in pr_files):
        print("analysing Terraform changes...")
        terraform_analyser = Terraformanalyser(repo_path, pr_files)
        terraform_analysis = terraform_analyser.analyse_changes()
    else:
        terraform_analysis = None
    
    # Check if there are Kubernetes files
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
    
    # Save the report to a file
    with open('migration_report.md', 'w') as f:
        f.write(report_markdown)
    
    # Also print the report to the console
    print("\n\n" + "="*80)
    print("MIGRATION REPORT")
    print("="*80)
    print(report_markdown)
    
    print("\nMigration report generated successfully")
    return 0

if __name__ == "__main__":
    sys.exit(main())