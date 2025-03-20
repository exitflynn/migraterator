import os
import sys
import argparse
from pathlib import Path

# Add parent directory to path so we can import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from terraform_analyser import TerraformAnalyser
from kubernetes_analyser import KubernetesAnalyser
from risk_assessor import RiskAssessor
from report_generator import ReportGenerator

def find_files(repo_path, extensions):
    """Find files with specific extensions in the repository."""
    files = []
    for ext in extensions:
        for file_path in Path(repo_path).glob(f'**/*{ext}'):
            files.append(str(file_path))
    return files

def main():
    parser = argparse.ArgumentParser(description='Analyze infrastructure changes locally')
    parser.add_argument('--repo-path', default='.', help='Path to the repository')
    parser.add_argument('--output', default='migration_report.md', help='Output file for the report')
    args = parser.parse_args()
    
    repo_path = args.repo_path
    
    tf_files = find_files(repo_path, ['.tf'])
    k8s_files = find_files(repo_path, ['.yaml', '.yml'])
    
    terraform_analysis = None
    kubernetes_analysis = None
    
    if tf_files:
        print(f"Found {len(tf_files)} Terraform files. Analyzing...")
        terraform_analyser = TerraformAnalyser(repo_path, tf_files)
        terraform_analysis = terraform_analyser.analyse_changes()
    
    if k8s_files:
        print(f"Found {len(k8s_files)} Kubernetes files. Analyzing...")
        kubernetes_analyser = KubernetesAnalyser(repo_path, k8s_files)
        kubernetes_analysis = kubernetes_analyser.analyse_changes()
    
    print("Performing risk assessment...")
    risk_assessor = RiskAssessor(terraform_analysis, kubernetes_analysis)
    risk_assessment = risk_assessor.generate_assessment()
    
    print("Generating migration report...")
    report_generator = ReportGenerator(terraform_analysis, kubernetes_analysis, risk_assessment)
    report_markdown = report_generator.generate_markdown_report()
    
    with open(args.output, 'w') as f:
        f.write(report_markdown)
    
    print(f"Migration report generated successfully: {args.output}")
    return 0

if __name__ == "__main__":
    sys.exit(main())