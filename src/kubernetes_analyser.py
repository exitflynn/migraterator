import subprocess
import yaml
import os
from src.utils.diff_utils import parse_diff

class KubernetesAnalyser:
    def __init__(self, repo_path, pr_files):
        self.repo_path = repo_path
        self.pr_files = [f for f in pr_files if f.endswith(('.yaml', '.yml'))]
        self.helm_charts = self._identify_helm_charts()
        
    def _identify_helm_charts(self):
        """Identify Helm charts in the repository"""
        helm_charts = []
        for root, dirs, files in os.walk(self.repo_path):
            if 'Chart.yaml' in files:
                helm_charts.append(os.path.relpath(root, self.repo_path))
        return helm_charts
    
    def run_kubectl_diff(self, namespace="default"):
        """Run kubectl diff on the changed Kubernetes manifests"""
        results = {}
        
        for k8s_file in self.pr_files:
            try:
                # Run kubectl diff
                result = subprocess.run(
                    ["kubectl", "diff", "-f", k8s_file, "-n", namespace],
                    cwd=self.repo_path,
                    capture_output=True,
                    text=True
                )
                
                # kubectl diff returns exit code 1 if there are differences
                # which would normally raise an exception, so we handle it manually
                results[k8s_file] = {
                    "diff_output": result.stdout,
                    "parsed_diff": self._parse_kubectl_diff(result.stdout)
                }
            except subprocess.CalledProcessError as e:
                results[k8s_file] = {
                    "error": str(e),
                    "stdout": e.stdout,
                    "stderr": e.stderr
                }
        
        return results
    
    def _parse_kubectl_diff(self, diff_output):
        """Parse the output from kubectl diff"""
        changes = {
            "added": [],
            "modified": [],
            "removed": []
        }
        
        # Simple parsing logic - can be enhanced
        for line in diff_output.split('\n'):
            line = line.strip()
            if line.startswith('+') and not line.startswith('+++'):
                changes["added"].append(line[1:].strip())
            elif line.startswith('-') and not line.startswith('---'):
                changes["removed"].append(line[1:].strip())
            elif line.startswith('~'):
                changes["modified"].append(line[1:].strip())
                
        return changes
    
    def analyse_helm_changes(self):
        """analyse changes in Helm charts"""
        results = {}
        
        for chart in self.helm_charts:
            chart_path = os.path.join(self.repo_path, chart)
            try:
                # Run helm template to see the rendered manifests
                result = subprocess.run(
                    ["helm", "template", chart_path],
                    capture_output=True,
                    text=True,
                    check=True
                )
                
                # Parse the YAML output
                templates = []
                for doc in yaml.safe_load_all(result.stdout):
                    if doc:  # Skip empty documents
                        templates.append(doc)
                
                results[chart] = {
                    "templates": templates,
                    "resource_count": len(templates)
                }
            except (subprocess.CalledProcessError, yaml.YAMLError) as e:
                results[chart] = {"error": str(e)}
        
        return results
    
    def analyse_changes(self):
        """analyse Kubernetes changes and return structured data"""
        kubectl_results = self.run_kubectl_diff()
        helm_results = self.analyse_helm_changes()
        
        # Add file-level diff analysis
        file_changes = {}
        for k8s_file in self.pr_files:
            file_changes[k8s_file] = parse_diff(k8s_file)
        
        return {
            "kubectl_results": kubectl_results,
            "helm_results": helm_results,
            "file_changes": file_changes
        } 