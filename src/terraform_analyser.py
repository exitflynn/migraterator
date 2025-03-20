import json
import subprocess
from src.utils.diff_utils import parse_diff

class TerraformAnalyser:
    def __init__(self, repo_path, pr_files):
        self.repo_path = repo_path
        self.pr_files = [f for f in pr_files if f.endswith('.tf')]
        
    def run_terraform_plan(self):
        """Run terraform plan and capture the output"""
        try:
            subprocess.run(["terraform", "init"], cwd=self.repo_path, check=True)
            result = subprocess.run(
                ["terraform", "plan", "-json"],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            
            return self._parse_plan_output(result.stdout)
        except subprocess.CalledProcessError as e:
            return {"error": str(e), "stdout": e.stdout, "stderr": e.stderr}
    
    def _parse_plan_output(self, plan_output):
        """Parse the JSON output from terraform plan"""
        changes = {
            "create": [],
            "update": [],
            "delete": []
        }
        
        # Split the output by newlines and parse each line as JSON
        for line in plan_output.strip().split('\n'):
            try:
                plan_item = json.loads(line)
                if "change" in plan_item:
                    action = plan_item["change"]["actions"][0]
                    if action in ["create", "update", "delete"]:
                        resource_type = plan_item.get("type", "unknown")
                        resource_name = plan_item.get("name", "unknown")
                        
                        # Extract the changes for updates
                        change_details = {}
                        if action == "update" and "change" in plan_item:
                            before = plan_item["change"].get("before", {})
                            after = plan_item["change"].get("after", {})
                            
                            # Compare before and after to find what changed
                            for key in set(list(before.keys()) + list(after.keys())):
                                if key in before and key in after and before[key] != after[key]:
                                    change_details[key] = {
                                        "before": before[key],
                                        "after": after[key]
                                    }
                        
                        changes[action].append({
                            "type": resource_type,
                            "name": resource_name,
                            "details": change_details
                        })
            except json.JSONDecodeError:
                continue
        
        return changes
    
    def analyse_changes(self):
        """analyse terraform changes and return structured data"""
        plan_results = self.run_terraform_plan()
        file_changes = {}
        for tf_file in self.pr_files:
            file_changes[tf_file] = parse_diff(tf_file)
        
        return {
            "plan_results": plan_results,
            "file_changes": file_changes
        } 