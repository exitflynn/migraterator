import subprocess
import os

def parse_diff(file_path):
    """
    Parse the git diff for a specific file
    
    Args:
        file_path: Path to the file to analyse
        
    Returns:
        Dictionary with parsed diff information
    """
    try:
        result = subprocess.run(
            ["git", "diff", "HEAD^", "--", file_path],
            capture_output=True,
            text=True,
            check=True
        )
        
        diff_output = result.stdout
        
        # Parse the diff output
        changes = {
            "added_lines": [],
            "removed_lines": [],
            "changed_blocks": []
        }
        
        current_block = None
        
        for line in diff_output.split('\n'):
            if line.startswith('@@'):
                # This is a diff hunk header
                if current_block:
                    changes["changed_blocks"].append(current_block)
                current_block = {
                    "header": line,
                    "lines": []
                }
            elif current_block is not None:
                current_block["lines"].append(line)
                
                if line.startswith('+') and not line.startswith('+++'):
                    changes["added_lines"].append(line[1:])
                elif line.startswith('-') and not line.startswith('---'):
                    changes["removed_lines"].append(line[1:])
        
        # Add the last block if it exists
        if current_block:
            changes["changed_blocks"].append(current_block)
            
        return changes
    except subprocess.CalledProcessError as e:
        # File might be new or there might be no changes
        if "fatal: bad object" in e.stderr:
            # This might be a new file
            if os.path.exists(file_path):
                return {
                    "added_lines": open(file_path, 'r').readlines(),
                    "removed_lines": [],
                    "changed_blocks": [{
                        "header": "@@ -0,0 +1,{} @@".format(len(open(file_path, 'r').readlines())),
                        "lines": ['+' + line.rstrip() for line in open(file_path, 'r').readlines()]
                    }],
                    "is_new_file": True
                }
        
        return {
            "error": str(e),
            "stdout": e.stdout,
            "stderr": e.stderr
        } 