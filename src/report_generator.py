from utils.llm_client import LLMClient

class ReportGenerator:
    def __init__(self, terraform_analysis=None, kubernetes_analysis=None, risk_assessment=None):
        self.terraform_analysis = terraform_analysis
        self.kubernetes_analysis = kubernetes_analysis
        self.risk_assessment = risk_assessment
        self.llm_client = LLMClient()
    
    def generate_summary(self):
        """Generate a human-readable summary of the changes"""
        summary = {
            "title": "Infrastructure Change Analysis",
            "sections": []
        }

        if self.terraform_analysis:
            plan_results = self.terraform_analysis.get("plan_results", {})
            
            terraform_summary = {
                "title": "Terraform Changes",
                "content": []
            }
            
            create_count = len(plan_results.get("create", []))
            update_count = len(plan_results.get("update", []))
            delete_count = len(plan_results.get("delete", []))
            
            if create_count + update_count + delete_count > 0:
                terraform_summary["content"].append(
                    f"This PR will create {create_count}, update {update_count}, and delete {delete_count} resources."
                )
            
                if create_count > 0:
                    terraform_summary["content"].append("**Resources to be created:**")
                    for resource in plan_results.get("create", []):
                        terraform_summary["content"].append(
                            f"- {resource.get('type')}.{resource.get('name')}"
                        )
                
                if update_count > 0:
                    terraform_summary["content"].append("**Resources to be updated:**")
                    for resource in plan_results.get("update", []):
                        details_str = ""
                        for key, change in resource.get("details", {}).items():
                            details_str += f"\n  - {key}: {change.get('before')} → {change.get('after')}"
                        
                        terraform_summary["content"].append(
                            f"- {resource.get('type')}.{resource.get('name')}{details_str}"
                        )
                
                if delete_count > 0:
                    terraform_summary["content"].append("**Resources to be deleted:**")
                    for resource in plan_results.get("delete", []):
                        terraform_summary["content"].append(
                            f"- {resource.get('type')}.{resource.get('name')}"
                        )
            else:
                terraform_summary["content"].append("No Terraform resource changes detected.")
            
            summary["sections"].append(terraform_summary)
        
        if self.kubernetes_analysis:
            kubectl_results = self.kubernetes_analysis.get("kubectl_results", {})
            helm_results = self.kubernetes_analysis.get("helm_results", {})
            
            kubernetes_summary = {
                "title": "Kubernetes Changes",
                "content": []
            }
            
            if kubectl_results:
                kubernetes_summary["content"].append("**Kubernetes Resource Changes:**")
                
                for file_path, result in kubectl_results.items():
                    parsed_diff = result.get("parsed_diff", {})
                    
                    added = len(parsed_diff.get("added", []))
                    modified = len(parsed_diff.get("modified", []))
                    removed = len(parsed_diff.get("removed", []))
                    
                    kubernetes_summary["content"].append(
                        f"- {file_path}: {added} additions, {modified} modifications, {removed} removals"
                    )
            
            if helm_results:
                kubernetes_summary["content"].append("**Helm Chart Changes:**")
                
                for chart_path, result in helm_results.items():
                    if "error" in result:
                        kubernetes_summary["content"].append(
                            f"- {chart_path}: Error analysing chart - {result['error']}"
                        )
                    else:
                        kubernetes_summary["content"].append(
                            f"- {chart_path}: {result.get('resource_count', 0)} resources in template"
                        )
            
            summary["sections"].append(kubernetes_summary)
            
        if self.risk_assessment:
            risk_summary = {
                "title": "Risk Assessment",
                "content": []
            }
            
            overall_risk = self.risk_assessment.get("overall_risk", "unknown")
            risk_summary["content"].append(f"**Overall Risk Level: {overall_risk.upper()}**")
            
            downtime_risks = self.risk_assessment.get("downtime_risks", [])
            if downtime_risks:
                risk_summary["content"].append("**Potential Downtime Risks:**")
                for risk in downtime_risks:
                    risk_summary["content"].append(
                        f"- [{risk.get('severity', 'unknown').upper()}] {risk.get('description')}"
                    )
                    risk_summary["content"].append(
                        f"  - Mitigation: {risk.get('mitigation', 'No mitigation provided')}"
                    )
            
            cost_impacts = self.risk_assessment.get("cost_impacts", [])
            if cost_impacts:
                risk_summary["content"].append("**Potential Cost Impacts:**")
                for impact in cost_impacts:
                    risk_summary["content"].append(
                        f"- [{impact.get('severity', 'unknown').upper()}] {impact.get('description')}"
                    )
                    risk_summary["content"].append(
                        f"  - Recommendation: {impact.get('recommendation', 'No recommendation provided')}"
                    )
            
            security_risks = self.risk_assessment.get("security_risks", [])
            if security_risks:
                risk_summary["content"].append("**Potential Security Risks:**")
                for risk in security_risks:
                    risk_summary["content"].append(
                        f"- [{risk.get('severity', 'unknown').upper()}] {risk.get('description')}"
                    )
                    risk_summary["content"].append(
                        f"  - Recommendation: {risk.get('recommendation', 'No recommendation provided')}"
                    )
            
            summary["sections"].append(risk_summary)

        if self.risk_assessment and self.risk_assessment.get("rollback_strategies"):
            rollback_summary = {
                "title": "Rollback Strategies",
                "content": []
            }
            
            for strategy in self.risk_assessment.get("rollback_strategies", []):
                rollback_summary["content"].append(f"**{strategy.get('tool')} Rollback:**")
                for step in strategy.get("steps", []):
                    rollback_summary["content"].append(f"- {step}")
            
            summary["sections"].append(rollback_summary)
        
        return summary
    
    def generate_llm_enhanced_summary(self):
        """Generate an LLM-enhanced summary of the changes"""
        standard_summary = self.generate_summary()
        summary_text = f"# {standard_summary['title']}\n\n"
        
        for section in standard_summary["sections"]:
            summary_text += f"## {section['title']}\n\n"
            for content in section["content"]:
                summary_text += f"{content}\n\n"
        
        prompt = f"""
        You are an expert DevOps engineer reviewing infrastructure changes in a pull request.
        Below is a technical summary of the changes:
        
        {summary_text}
        
        Please provide:
        1. A concise, plain-English summary of these changes for non-technical stakeholders
        2. Highlight the most important risks or concerns
        3. Suggest any additional testing or verification steps that should be performed
        4. Any best practices or improvements that could be made to these changes
        
        Format your response in Markdown.
        """
        
        enhanced_summary = self.llm_client.generate_text(prompt)
        
        return enhanced_summary
    
    def generate_markdown_report(self):
        """Generate a markdown report for the PR comment"""
        try:
            return self.generate_llm_enhanced_summary()
        except Exception as e:
            # fall back to standard summary if LLM fails
            print(f"Error generating LLM summary: {e}")
            standard_summary = self.generate_summary()
            
            markdown = f"# {standard_summary['title']}\n\n"
            
            for section in standard_summary["sections"]:
                markdown += f"## {section['title']}\n\n"
                for content in section["content"]:
                    markdown += f"{content}\n\n"
            
            return markdown 