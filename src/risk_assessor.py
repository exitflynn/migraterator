class RiskAssessor:
    def __init__(self, terraform_analysis=None, kubernetes_analysis=None):
        self.terraform_analysis = terraform_analysis
        self.kubernetes_analysis = kubernetes_analysis
        
    def assess_downtime_risks(self):
        """Assess potential downtime risks from the changes"""
        risks = []
        
        # Check Terraform changes for downtime risks
        if self.terraform_analysis:
            plan_results = self.terraform_analysis.get("plan_results", {})
            
            # Check for deletions of critical resources
            for deletion in plan_results.get("delete", []):
                resource_type = deletion.get("type", "")
                
                # Examples of critical resources that might cause downtime
                if resource_type in [
                    "aws_instance", "aws_db_instance", "aws_eks_cluster",
                    "aws_lambda_function", "aws_api_gateway_rest_api",
                    "google_compute_instance", "google_sql_database_instance",
                    "azurerm_virtual_machine", "azurerm_sql_server"
                ]:
                    risks.append({
                        "severity": "high",
                        "description": f"Deletion of {resource_type} '{deletion.get('name')}' may cause service downtime",
                        "mitigation": "Consider blue-green deployment or scheduled maintenance window"
                    })
            
            # Check for updates to critical resources
            for update in plan_results.get("update", []):
                resource_type = update.get("type", "")
                details = update.get("details", {})
                
                # Check for specific risky changes
                if resource_type == "aws_instance" and "instance_type" in details:
                    risks.append({
                        "severity": "medium",
                        "description": f"Changing instance type from {details['instance_type']['before']} to {details['instance_type']['after']} requires instance restart",
                        "mitigation": "Ensure you have multiple instances or a maintenance window"
                    })
        
        # Check Kubernetes changes for downtime risks
        if self.kubernetes_analysis:
            kubectl_results = self.kubernetes_analysis.get("kubectl_results", {})
            
            for file_path, result in kubectl_results.items():
                parsed_diff = result.get("parsed_diff", {})
                
                # Check for removal of volumes or environment variables
                for removed in parsed_diff.get("removed", []):
                    if "volumeMounts:" in removed or "volumes:" in removed:
                        risks.append({
                            "severity": "high",
                            "description": f"Removal of volume mounts in {file_path} may cause data loss or application failure",
                            "mitigation": "Ensure data is backed up and application can handle volume changes"
                        })
                    elif "env:" in removed:
                        risks.append({
                            "severity": "medium",
                            "description": f"Removal of environment variables in {file_path} may cause application configuration issues",
                            "mitigation": "Verify application can handle missing environment variables"
                        })
        
        return risks
    
    def assess_cost_impacts(self):
        """Assess potential cost impacts from the changes"""
        impacts = []
        
        # Check Terraform changes for cost impacts
        if self.terraform_analysis:
            plan_results = self.terraform_analysis.get("plan_results", {})
            
            # Check for new resources that might increase costs
            for creation in plan_results.get("create", []):
                resource_type = creation.get("type", "")
                
                # Examples of potentially costly resources
                if resource_type in [
                    "aws_instance", "aws_db_instance", "aws_eks_cluster",
                    "aws_elasticache_cluster", "aws_redshift_cluster",
                    "google_compute_instance", "google_sql_database_instance",
                    "azurerm_virtual_machine", "azurerm_sql_server"
                ]:
                    impacts.append({
                        "severity": "medium",
                        "description": f"Creation of {resource_type} '{creation.get('name')}' will increase cloud costs",
                        "recommendation": "Verify the resource size and configuration are appropriate for your needs"
                    })
            
            # Check for updates that might increase costs
            for update in plan_results.get("update", []):
                resource_type = update.get("type", "")
                details = update.get("details", {})
                
                # Check for specific changes that might increase costs
                if resource_type == "aws_instance" and "instance_type" in details:
                    before = details["instance_type"]["before"]
                    after = details["instance_type"]["after"]
                    
                    # Simple heuristic - check if the instance type is getting larger
                    # This could be improved with actual pricing data
                    if (before.startswith("t2.") and after.startswith("t3.")) or \
                       (before.startswith("t3.") and after.startswith("m5.")) or \
                       (before.endswith(".small") and after.endswith(".medium")) or \
                       (before.endswith(".medium") and after.endswith(".large")) or \
                       (before.endswith(".large") and after.endswith(".xlarge")):
                        impacts.append({
                            "severity": "medium",
                            "description": f"Upgrading instance type from {before} to {after} will increase costs",
                            "recommendation": "Verify the larger instance type is necessary for your workload"
                        })
        
        return impacts
    
    def assess_security_risks(self):
        """Assess potential security risks from the changes"""
        risks = []
        
        # Check Terraform changes for security risks
        if self.terraform_analysis:
            plan_results = self.terraform_analysis.get("plan_results", {})
            file_changes = self.terraform_analysis.get("file_changes", {})
            
            # Check for security group changes
            for update in plan_results.get("update", []):
                resource_type = update.get("type", "")
                
                if resource_type == "aws_security_group" or resource_type == "aws_security_group_rule":
                    risks.append({
                        "severity": "high",
                        "description": f"Changes to security group '{update.get('name')}' may impact network security",
                        "recommendation": "Verify that no unnecessary ports are being opened"
                    })
            
            # Check for IAM policy changes
            for file_path, changes in file_changes.items():
                if "iam" in file_path.lower():
                    risks.append({
                        "severity": "high",
                        "description": f"Changes to IAM policies in {file_path} may impact security",
                        "recommendation": "Review IAM changes carefully to ensure principle of least privilege"
                    })
        
        # Check Kubernetes changes for security risks
        if self.kubernetes_analysis:
            kubectl_results = self.kubernetes_analysis.get("kubectl_results", {})
            
            for file_path, result in kubectl_results.items():
                parsed_diff = result.get("parsed_diff", {})
                
                # Check for security-related changes
                for added in parsed_diff.get("added", []):
                    if "privileged: true" in added:
                        risks.append({
                            "severity": "critical",
                            "description": f"Container running in privileged mode in {file_path} poses security risk",
                            "recommendation": "Avoid privileged containers unless absolutely necessary"
                        })
                    elif "hostNetwork: true" in added:
                        risks.append({
                            "severity": "high",
                            "description": f"Container using host network in {file_path} poses security risk",
                            "recommendation": "Avoid host network unless absolutely necessary"
                        })
        
        return risks
    
    def suggest_rollback_strategy(self):
        """Suggest rollback strategies based on the changes"""
        strategies = []
        
        # Terraform rollback strategies
        if self.terraform_analysis:
            strategies.append({
                "tool": "Terraform",
                "steps": [
                    "Keep a copy of the current state file before applying changes",
                    "Use `terraform plan -out=tfplan` to create a plan file",
                    "If issues occur, use `terraform apply -target=RESOURCE_TYPE.RESOURCE_NAME` to selectively apply fixes",
                    "For full rollback, revert the PR and run `terraform apply`"
                ]
            })
        
        # Kubernetes rollback strategies
        if self.kubernetes_analysis:
            strategies.append({
                "tool": "Kubernetes",
                "steps": [
                    "For Deployments, use `kubectl rollout undo deployment/DEPLOYMENT_NAME`",
                    "For StatefulSets, use `kubectl rollout undo statefulset/STATEFULSET_NAME`",
                    "For other resources, revert the YAML files and reapply with `kubectl apply`"
                ]
            })
            
            # Helm rollback strategies
            if self.kubernetes_analysis.get("helm_results"):
                strategies.append({
                    "tool": "Helm",
                    "steps": [
                        "Use `helm history RELEASE_NAME` to see revision history",
                        "Use `helm rollback RELEASE_NAME REVISION_NUMBER` to rollback to a previous version"
                    ]
                })
        
        return strategies
    
    def generate_assessment(self):
        """Generate a comprehensive risk assessment"""
        assessment = {
            "downtime_risks": self.assess_downtime_risks(),
            "cost_impacts": self.assess_cost_impacts(),
            "security_risks": self.assess_security_risks(),
            "rollback_strategies": self.suggest_rollback_strategy()
        }
        
        # Calculate overall risk level
        risk_levels = {
            "critical": 0,
            "high": 0,
            "medium": 0,
            "low": 0
        }
        
        for risk in assessment["downtime_risks"] + assessment["security_risks"]:
            severity = risk.get("severity", "low")
            risk_levels[severity] += 1
        
        if risk_levels["critical"] > 0:
            assessment["overall_risk"] = "critical"
        elif risk_levels["high"] > 0:
            assessment["overall_risk"] = "high"
        elif risk_levels["medium"] > 0:
            assessment["overall_risk"] = "medium"
        else:
            assessment["overall_risk"] = "low"
        
        return assessment 