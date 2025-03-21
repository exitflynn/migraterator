# Migraterator

> *"Behold, Perry the Platypus! My latest invention: the Migraterator!"*

Migraterator is a GitHub Action that wraps over existing LLM offerings which is tailored to analysing infrastructure changes in a PR in an automated fashion, predicting their impact, helping DevOps teams understand the potential consequences of Terraform and Kubernetes changes before they're deployed especially since Infrastructure-as-Code (IaC) changes in Terraform or Kubernetes can cause unintended downtime, cost increases, or security risks. Migraterator helps by:

- Detecting changes in Terraform (.tf), Kubernetes YAML, or Helm charts
- Analysing resource modifications, additions, and deletions
- Suggesting rollback strategies and pre-migration steps
- Warning about potential downtime, cost spikes, or security risks

## How It Works

The GitHub Action triggers when a PR contains Terraform/Kubernetes files and performs the following:

### 1️. Terraform Plan Analysis

- Runs `terraform plan` to detect changes, extracts key updates (e.g., aws_instance type, eks_cluster settings, networking changes) and uses an LLM to summarize changes in plain impact-focused language.

### 2. Kubernetes Diff Analysis

- Runs `kubectl diff` to check modifications in Deployments, Services, ConfigMaps, etc. and highlights breaking changes, such as deleted volumes or changed environment variables

### 3️. Risk Assessment & Migration Recommendations

- Identifies downtime risks (e.g., deleting resources without replacements), warns about cost changes from new cloud resources, suggests rollback strategies (like terraform destroy, kubectl rollback, or helm rollback).

### 4️. PR Comment with Migration Plan

- Generates a summary of changes and their impact, provides recommendations for testing and rollback, highlights potential compliance or security issues

## Installation

### GitHub Action Setup

1. Add the following to your repository's `.github/workflows/migraterator.yml`:

```yaml
name: Migraterator

on:
  pull_request:
    paths:
      - '**.tf'
      - '**.yaml'
      - '**.yml'
      - '**/Chart.yaml'
      - '**/values.yaml'

jobs:
  analyse-infrastructure-changes:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v3
        with:
          fetch-depth: 0  # fetching all history for proper diff analysis
      
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.10'
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
      
      - name: Set up Terraform
        uses: hashicorp/setup-terraform@v2
        with:
          terraform_version: '1.0.0'
      
      - name: Set up kubectl
        uses: azure/setup-kubectl@v3
        with:
          version: 'latest'
      
      - name: Set up Helm
        uses: azure/setup-helm@v3
        with:
          version: 'latest'
      
      - name: Run Migraterator
        id: migraterator
        run: python src/main.py
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          PR_NUMBER: ${{ github.event.pull_request.number }}
          REPO_NAME: ${{ github.repository }}
          LLM_API_KEY: ${{ secrets.LLM_API_KEY }}
      
      - name: Comment on PR
        uses: actions/github-script@v6
        with:
          github-token: ${{ secrets.GITHUB_TOKEN }}
          script: |
            const fs = require('fs');
            const reportPath = 'migration_report.md';
            
            if (fs.existsSync(reportPath)) {
              const reportContent = fs.readFileSync(reportPath, 'utf8');
              
              github.rest.issues.createComment({
                issue_number: context.issue.number,
                owner: context.repo.owner,
                repo: context.repo.repo,
                body: reportContent
              });
            } else {
              console.error('Migration report file not found');
            }
```

2. Add your LLM API key (OpenAI by default but Gemini also supported) to your repository secrets as `LLM_API_KEY`

## Usage

### Command Line Interface

After installation, you can use Migraterator from the command line:

```bash
# Analyze a PR
migraterator analyze --pr-number=123 --repo-name=yourusername/repo

# Run a local analysis without GitHub API
migraterator local --repo-path=/path/to/repo
```

### Using Docker

```bash
# Build the Docker image
docker build -t migraterator .

# Run Migraterator in a container
docker run -it --rm \
  -e GITHUB_TOKEN=your_github_token \
  -e LLM_API_KEY=your_llm_api_key \
  -v $(pwd):/app \
  migraterator analyze --pr-number=123 --repo-name=yourusername/repo
```

### Using Make

```bash
# Install the package
make install

# Run a local analysis
make local

# Run tests
make test

# Run linting
make lint
```

## Local Development

### Prerequisites

- Python 3.10+
- Terraform CLI
- kubectl
- Helm

### Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/migraterator.git
cd migraterator
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables:
```bash
export GITHUB_TOKEN=your_github_token
export PR_NUMBER=your_pr_number
export REPO_NAME=your_repo_name
export LLM_API_KEY=your_openai_api_key
```

4. Run the tool:
```bash
python src/main.py
```

## Contributing

Contributions are welcome! Feel free to suggest any changes via the issue tracker or submitting a PR or just let me know what you think about the project or any experience using in prod.

## License

This project is licensed under the BSD 3-Clause License - see the [LICENSE](LICENSE) file for details.
