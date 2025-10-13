from pathlib import Path
import json
import sys

"""
Script for collecting recursively inside a directory all files with aspecifc extension and storing their information in a JSON file of the same name.

Extensions collected:
    * .py
    * .R
    * .ipynb
    * .qmd

Information stored:
    * name (str): file name
    * extension (str): extension, e.g ".py"
    * course (str): 
    * st_ino (int): Inode number; a unique identifier for the file within the filesystem.
    * st_dev (int): Identifier of the device on which the file resides.
    * st_nlink (int): Number of hard links pointing to the file.
    * st_uid (int): User ID of the file’s owner.
    * st_gid (int): Group ID of the file’s owner.
    * st_size (int): File size in bytes.
    * st_atime (float): Time of last file access, expressed in seconds since the epoch.
    * st_mtime (float): Time of last file content modification, expressed in seconds since the epoch.
    * st_ctime (float): On Unix, the time of the last metadata change (e.g., permissions, ownership). On Windows, the file creation time. Expressed in seconds since the epoch.
    * st_birthtime (float): File creation time in seconds since the epoch. Available only on some systems (e.g., macOS).
    * st_blocks (int): Number of 512-byte blocks allocated for the file. Value may vary by filesystem.
    * st_blksize (int): Optimal block size for efficient I/O operations on the file.

# How to use it
Run, the following command from the terminal.
'folder_path' and 'course' argument needs to be specified

Args: 
    from (str): the folder path you wish to collect the files from The folder needs to contain information from a single course only.

    course (str): the name of the course you're searching the files for.

    to (str): the path of the folder you wish to copy the JSON file in.


%python3 data_collection.py [folder_path] [course] [to]
"""


def get_information(path: Path, course: str) -> dict:
    # Read the file information and stores it in a dictionary
    info = path.stat()
    # Read the content of the file as a string
    content: str = path.read_text()
    return {
        "name": path.stem,
        "extension": path.suffix,
        "course": course,
        "st_mode": info.st_mode,
        "st_ino": info.st_ino,
        "st_dev": info.st_dev,
        "st_nlink": info.st_nlink,
        "st_uid": info.st_uid,
        "st_gid": info.st_gid,
        "st_size": info.st_size,
        "st_atime": info.st_atime,
        "st_mtime": info.st_mtime,
        "st_ctime": info.st_ctime,
        "st_birthtime": info.st_birthtime,
        "st_blocks": info.st_blocks,
        "st_blksize": info.st_blksize,
        "content": content,
    }


def to_json(obj: dict, file_name: str) -> None:
    with open(f"{file_name}", "w") as fp:
        # Write the recorded information in a JSON file.
        # Has the same name as the original file
        json.dump(obj, fp)


if __name__ == "__main__":
    # Extensions you want to capture
    extensions: list[str] = [".py", ".R", ".ipynb", ".qmd", ".Rmd"]
    # First argument of the command
    from_path: str = sys.argv[1]
    # Second argument of the command
    course: str = sys.argv[2]
    # Third argumnet of the command
    to_path: str = sys.argv[3]
    # Extensions you want to capture
    extensions = [".py", ".R", ".ipynb", ".qmd", ".Rmd"]

    from_dir = Path(from_path)
    to_dir = Path(to_path)

    if not from_dir.is_dir():
        raise AttributeError(
            "Please, make sure that the 'from' path provided is the path of a valid folder"
        )
    if not to_dir.is_dir():
        raise AttributeError(
            "Please, make sure that the 'to' path provided is the path of a valid folder"
        )

    # Recursively search and collect information for file of each extension
    for ext in extensions:
        path_list = list(
            from_dir.glob(f"**/*/*{ext}")
        )  # '**/*/' allows for a recursive search throughout the directory
        # Read the file information and stores it in a dictionary
        for path in path_list:
            records = get_information(path, course)
            file_path = f"{str(to_dir)}/{path.stem}.json"
            to_json(records, file_path)
