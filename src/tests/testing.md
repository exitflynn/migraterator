
## Taking Migraterator for a Spin

Having unit and integration tests here are a [TODO] but to test Migraterator locally with a sample infrastructure repository:

1. **Set up a test repository with Terraform or Kubernetes files**:
   ```bash
   mkdir test-repo
   cd test-repo
   git init
   ```

2. **Create some sample Terraform files**:
   ```bash
   mkdir terraform
   cd terraform
   ```

   Create a file named `main.tf`:
   ```hcl
   provider "aws" {
     region = "us-west-2"
   }

   resource "aws_instance" "example" {
     ami           = "ami-0c55b159cbfafe1f0"
     instance_type = "t2.micro"
     tags = {
       Name = "example-instance"
     }
   }
   ```

   Commit this file:
   ```bash
   git add main.tf
   git commit -m "Initial Terraform configuration"
   ```

3. **Create a branch and make changes**:
   ```bash
   git checkout -b update-instance
   ```

   Edit `main.tf` to change the instance type:
   ```hcl
   resource "aws_instance" "example" {
     ami           = "ami-0c55b159cbfafe1f0"
     instance_type = "t2.medium"  # Changed from t2.micro
     tags = {
       Name = "example-instance"
       Environment = "production"  # Added tag
     }
   }
   ```

   Commit the changes:
   ```bash
   git add main.tf
   git commit -m "Update instance type and add tags"
   ```

4. **Clone your Migraterator repository and set it up**:
   ```bash
   cd /path/to/migraterator
   ```

5. **Set the environment variables**:
   ```bash
   export GITHUB_TOKEN=your_github_token
   export PR_NUMBER=1  # This won't be used in local testing
   export REPO_NAME=your_github_username/test-repo
   export LLM_API_KEY=your_openai_api_key
   export GITHUB_WORKSPACE=/path/to/test-repo
   ```

6. **Modify the main.py file for local testing**:
   Create a file called `local_test.py` with the following content:


7. **Run the local test**:
   ```bash
   python local_test.py
   ```

8. **Review the output**:
   The script will generate a `migration_report.md` file and also print the report to the console. This report will show the analysis of your Terraform changes, including the instance type change and the added tag.

## Notes for Real-World Usage

For real-world usage with GitHub Actions:

1. **Create a new repository** for your Migraterator project
2. **Push all the code** we've developed
3. **Set up the GitHub Action** in a repository with Terraform or Kubernetes files
4. **Add the OpenAI/Gemini API key** to your repository secrets
5. **Create a PR** with changes to Terraform or Kubernetes files to trigger the action

The GitHub Action will run automatically when a PR is created or updated that includes changes to Terraform or Kubernetes files. It will analyse the changes and post a comment on the PR with the migration report.
