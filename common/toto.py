from pathlib import Path


def truncate_path_to_parent(path, parent_name):
    # Create a Path object
    full_path = Path(path)

    # Iterate through the parents to find the desired parent directory
    for parent in full_path.parents:
        if parent.name == parent_name:
            return parent

    # If the parent directory is not found, return the original path
    return full_path


# Example usage
path = "/home/user/documents/project/file.txt"
parent_name = "user"

truncated_path = truncate_path_to_parent(path, parent_name)
print(f"Truncated path: {truncated_path}")
