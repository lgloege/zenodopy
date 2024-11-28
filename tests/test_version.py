import os
import time
import json
from pathlib import Path
import argparse
import zenodopy

def parse_metadata_from_json(json_file_path: Path) -> zenodopy.ZenodoMetadata:
    """Parse metadata from a JSON file into a ZenodoMetadata object."""
    json_file_path = json_file_path.expanduser()
    if not json_file_path.exists():
        raise ValueError(
            f"{json_file_path} does not exist. Please check you entered the correct path."
        )
    
    with json_file_path.open("r") as json_file:
        data = json.load(json_file)
    
    metadata_dict = data.get("metadata", {})
    return zenodopy.ZenodoMetadata(**metadata_dict)


def main():
    # Set up argument parsing
    parser = argparse.ArgumentParser(description='Update Zenodo deposition with new version and files.')
    parser.add_argument('--version_tag', required=True, help='The version tag for the new release.')
    parser.add_argument('--zenodo_token', required=True, help='The Zenodo API token.')
    parser.add_argument('--dep_id', required=True, type=int, help='The Zenodo deposition ID.')
    parser.add_argument('--base_dir', required=True, help='The base directory path.')
    parser.add_argument('--metadata_file', required=True, help='The metadata JSON file path.')
    parser.add_argument('--upload_dir', required=True, help='The directory containing files to upload.')

    args = parser.parse_args()

    version_tag = args.version_tag
    zenodo_token = args.zenodo_token
    dep_id = args.dep_id
    base_dir = Path(args.base_dir)
    zenodo_metadata_file = Path(args.metadata_file)
    upload_dir = Path(args.upload_dir)

    print("Version Tag:", version_tag)
    
    # Parse and update metadata with new version tag
    metadata = parse_metadata_from_json(zenodo_metadata_file)
    metadata.version = version_tag
    
    max_retries = 5

    for attempt in range(1, max_retries + 1):
        try:
            zeno = zenodopy.Client(
                sandbox=True,
                token=zenodo_token,
            )

            zeno.set_project(dep_id=dep_id)

            zeno.update(
                source=str(upload_dir),
                publish=True,
                metadata=metadata,
            )
            print("Update succeeded.")
            break

        except Exception as e:
            print(f"Attempt {attempt} failed with error: {e}")

            time.sleep(2)  # Optional: Wait before retrying

            zeno._delete_project(dep_id=dep_id)

            if attempt == max_retries:
                print("Max retries reached. Exiting.")
                raise
            else:
                time.sleep(2)

if __name__ == "__main__":
    main()
