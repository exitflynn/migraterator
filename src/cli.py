#!/usr/bin/env python3
import os
import sys
import click
from src.main import run_migraterator

@click.group()
def cli():
    """Migraterator: Analyze infrastructure changes in PRs and provide migration guidance."""
    pass

@cli.command()
@click.option('--repo-path', default='.', help='Path to the repository')
@click.option('--pr-number', required=True, help='PR number to analyze')
@click.option('--repo-name', required=True, help='Repository name in format "owner/repo"')
@click.option('--github-token', envvar='GITHUB_TOKEN', help='GitHub token for API access')
@click.option('--llm-api-key', envvar='LLM_API_KEY', help='API key for the LLM service')
@click.option('--llm-provider', default='openai', help='LLM provider to use (openai or gemini)')
@click.option('--llm-model', default='', help='Model to use for the selected provider')
@click.option('--output', default='migration_report.md', help='Output file for the report')
def analyze(repo_path, pr_number, repo_name, github_token, llm_api_key, llm_provider, llm_model, output):
    """Analyze infrastructure changes in a PR and generate a migration report."""
    # Set environment variables
    os.environ['GITHUB_WORKSPACE'] = repo_path
    os.environ['PR_NUMBER'] = pr_number
    os.environ['REPO_NAME'] = repo_name
    
    if github_token:
        os.environ['GITHUB_TOKEN'] = github_token
    
    if llm_api_key:
        os.environ['LLM_API_KEY'] = llm_api_key
    
    os.environ['LLM_PROVIDER'] = llm_provider
    os.environ['LLM_MODEL'] = llm_model
    
    # Run the main function
    exit_code = run_migraterator()
    
    # Print success message
    if exit_code == 0:
        click.echo(f"Migration report generated successfully: {output}")
        with open(output, 'r') as f:
            click.echo("\nReport Preview:")
            click.echo("==============")
            click.echo(f.read()[:500] + "...\n")
    
    sys.exit(exit_code)

@cli.command()
@click.option('--repo-path', default='.', help='Path to the repository')
def local(repo_path):
    """Run a local analysis without GitHub API integration."""
    # Import the local test module
    sys.path.append(os.path.join(os.path.dirname(__file__), 'tests'))
    from local_test import main as run_local_test
    
    # Set environment variables
    os.environ['GITHUB_WORKSPACE'] = repo_path
    
    # Run the local test
    exit_code = run_local_test()
    sys.exit(exit_code)

if __name__ == '__main__':
    cli() 