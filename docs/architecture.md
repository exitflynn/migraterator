# Migraterator Architecture

This document outlines the architecture of Migraterator, explaining how the different components work together to analyse infrastructure changes and provide migration guidance.

## System Overview

Migraterator is designed as a modular system with several key components that work together to analyse infrastructure changes in pull requests. The system is triggered by GitHub Actions when changes to infrastructure files are detected.

![Architecture Diagram](./architecture-diagram.png)

## Core Components

### 1. analysers

#### Terraform analyser (`src/terraform_analyser.py`)
- Parses Terraform files and executes `terraform plan`
- Extracts resource changes (creations, updates, deletions)
- Identifies specific attribute changes in resources

#### Kubernetes analyser (`src/kubernetes_analyser.py`)
- analyses Kubernetes YAML files and Helm charts
- Executes `kubectl diff` to identify changes
- Detects changes in deployments, services, and other Kubernetes resources
- Identifies Helm chart changes and their impact

### 2. Risk Assessor (`src/risk_assessor.py`)
- Evaluates potential downtime risks from infrastructure changes
- Assesses cost impacts of resource changes
- Identifies security risks in the proposed changes
- Suggests appropriate rollback strategies

### 3. Report Generator (`src/report_generator.py`)
- Compiles analysis results into a structured format
- Uses LLM to enhance technical details with human-readable explanations
- Formats the final report as Markdown for GitHub PR comments

### 4. Utilities

#### GitHub Utilities (`src/utils/github_utils.py`)
- Interacts with GitHub API to fetch PR details
- Posts comments on PRs with analysis results

#### LLM Client (`src/utils/llm_client.py`)
- Provides an abstraction layer for LLM services
- Supports multiple providers (OpenAI, Google Gemini)
- Formats prompts and parses responses

#### Diff Utilities (`src/utils/diff_utils.py`)
- Parses git diffs to identify file changes
- Extracts added, modified, and removed lines

## Data Flow

1. **Trigger**: A PR is created or updated with changes to infrastructure files
2. **File Analysis**: Changed files are identified and categorized
3. **Infrastructure Analysis**: Terraform and Kubernetes analysers process the changes
4. **Risk Assessment**: The risk assessor evaluates potential impacts
5. **Report Generation**: Analysis results are compiled into a comprehensive report
6. **Feedback**: The report is posted as a comment on the PR

## Extension Points

Migraterator is designed to be extensible in several ways:

1. **Additional analysers**: New analysers can be added for other infrastructure tools
2. **Custom Risk Rules**: The risk assessment engine can be extended with domain-specific rules
3. **LLM Providers**: The LLM client supports multiple providers and can be extended to support more
4. **Report Formats**: The report generator can be modified to produce different output formats

## Configuration

Migraterator is configured through environment variables:

- `GITHUB_TOKEN`: GitHub token for API access
- `PR_NUMBER`: PR number to analyse
- `REPO_NAME`: Repository name in format "owner/repo"
- `LLM_API_KEY`: API key for the LLM service
- `LLM_PROVIDER`: LLM provider to use ('openai' or 'gemini')
- `LLM_MODEL`: Model to use for the selected provider

## Future Enhancements

1. **Compliance Checking**: Add checks for compliance with security standards
2. **Cost Estimation**: Integrate with cloud provider pricing APIs
3. **Performance Impact Analysis**: analyse changes that might affect application performance
4. **Dependency Analysis**: Check if changes to one resource might affect dependent resources
5. **Historical Context**: Compare changes against previous incidents or issues 