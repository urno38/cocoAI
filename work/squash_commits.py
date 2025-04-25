import os
import subprocess
import sys


def run_command(command, capture_output=False):
    """Run a shell command and return its output."""
    try:
        if capture_output:
            result = subprocess.run(
                command, shell=True, check=True, text=True, capture_output=True
            )
            return result.stdout.strip()
        else:
            subprocess.run(command, shell=True, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error: {e}")
        sys.exit(1)


def validate_commit_exists(commit_hash):
    """Check if a commit exists in the repository."""
    try:
        run_command(f"git cat-file -t {commit_hash}", capture_output=True)
    except SystemExit:
        print(f"Commit {commit_hash} does not exist.")
        sys.exit(1)


def auto_squash_commits(start_commit, end_commit):
    """Automatically squash all commits between start_commit and end_commit."""
    validate_commit_exists(start_commit)
    validate_commit_exists(end_commit)

    print(f"Starting interactive rebase from {start_commit} to {end_commit}...")

    # Start an interactive rebase
    run_command(f"git rebase -i {start_commit}^", capture_output=True)

    # Locate the Git rebase todo file
    git_dir = run_command("git rev-parse --git-dir", capture_output=True)
    rebase_todo_path = os.path.join(git_dir, "rebase-merge", "git-rebase-todo")

    if not os.path.exists(rebase_todo_path):
        print("Error: Rebase todo file not found. Exiting.")
        sys.exit(1)

    # Read and modify the rebase todo file
    with open(rebase_todo_path, "r") as file:
        lines = file.readlines()

    # Keep the first commit as 'pick', change the rest to 'squash'
    new_lines = [lines[0]] + ["squash" + line[4:] for line in lines[1:]]

    with open(rebase_todo_path, "w") as file:
        file.writelines(new_lines)

    print("Modified rebase todo file to squash commits automatically.")

    # Continue the rebase automatically
    run_command("GIT_COMMITTER_DATE='now' git rebase --continue")

    print("Rebase completed successfully.")

    # Force push the updated history
    print("Force pushing changes to remote...")
    run_command("git push origin --force")

    print("✔ Successfully squashed commits and updated the repository!")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python auto_squash.py <start_commit> <end_commit>")
        sys.exit(1)

    start_commit = sys.argv[1]
    end_commit = sys.argv[2]

    auto_squash_commits(start_commit, end_commit)
    auto_squash_commits(start_commit, end_commit)
