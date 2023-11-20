"""Created on Tue Aug  8 15:42:28 2023

@author: agarc

"""
import logging
import os


# =============================================================================
# PathExplorer
# =============================================================================
class PathExplorer:
    """This class handles path and file/extension list by exploring folders.
    It also handles path/directory definitions and either files exists
    """

    # =============================================================================
    # get files in paths functions
    # =============================================================================
    @staticmethod
    def get_all_files_paths(directory: str) -> list:
        """Explore the main folder and list all files, including their paths.

        Args:
        ----
        directory (str): The path of the directory to explore. You can also input a
        filepath
        Returns:
        list: A list of file paths.
        """
        # Check if the input is a file path
        if os.path.isfile(directory):
            return [directory]

        # Check if the directory exists and check if it starts with ./ or ../
        if not PathExplorer.assert_directory(directory):
            return []

        file_paths = []
        for root, _, files in os.walk(directory):
            for file in files:
                file_path = os.path.join(root, file)
                file_paths.append(file_path)
        return file_paths

    @staticmethod
    def get_all_paths_with_extension_name(directory: str) -> list[dict]:
        """Get a hashmap with file extensions lists of file paths
            with that extension as values.

        Args:
        ----
        directory (str): The path of the directory to explore.

        Returns:
        -------
        dict: A list  [file paths, file extensions]
        """
        all_file_paths = PathExplorer.get_all_files_paths(directory)

        temp_extensions = set()
        paths_with_extension = []
        for file_path in all_file_paths:
            file_extension = PathExplorer.get_single_file_extension(file_path)
            file_name = PathExplorer.get_single_file_name(file_path)
            paths_with_extension.append(
                {
                    "file_path": file_path,
                    "file_extension": file_extension,
                    "file_name": file_name,
                    "file_full_name": file_name + file_extension,
                },
            )

            temp_extensions.add(file_extension)
        return paths_with_extension

    # =============================================================================
    # get single files path & extensions
    # =============================================================================
    @staticmethod
    def get_single_file_extension(single_file_path: str) -> str:
        """Get the file extension of a single file.

        Args:
        ----
        single_file_path (str): The path of the file.

        Returns:
        -------
        str: The file extension.
        """
        _, file_extension = os.path.splitext(single_file_path)
        return file_extension.lower()

    @staticmethod
    def get_single_file_name(single_file_path: str) -> str:
        """Get the file name without extension of a single file.

        Args:
        ----
        single_file_path (str): The path of the file.

        Returns:
        -------
        str: The file name without extension.
        """
        file_name, _ = os.path.splitext(single_file_path)
        return os.path.basename(file_name)

    # =============================================================================
    # path manipulation
    # =============================================================================
    @staticmethod
    def split_path(path: str) -> list:
        """Split a path into sub path.
        Useful to construct new paths.

        Parameters
        ----------
        path : str
            path string.

        Returns
        -------
        folders : list
            list of sub path.

        """
        folders = []
        while True:
            path, folder = os.path.split(path)
            if folder:
                folders.append(folder)
            else:
                if path:
                    folders.append(path)
                break
        folders.reverse()
        return folders

    # =============================================================================
    # assert functions
    # =============================================================================
    @staticmethod
    def assert_directory(directory: str) -> bool:
        """Check if the directory exits.
        check if the directory given starts with ./ or ../
        use only relative path please:)
        """
        if os.path.exists(directory):
            return True

        if directory[0] == "." or directory[0:2] == "..":
            if os.path.exists(directory):
                return True
            else:
                logging.debug("Directory does not exist")
                return False
        else:
            logging.debug("Directory must start with './' or '../' ")
            return False

    @staticmethod
    def assert_file_exists(file_path: str) -> bool:
        """Check if a file exists"""
        if os.path.exists(file_path):
            return True
        else:
            logging.debug("This file does not exists: {file_path}")
            return False

    @staticmethod
    def check_path_type(path: str) -> str:
        """Check if the path is a directory or a file."""
        # if the path points towards a file we check if it exits
        if os.path.isfile(path):
            if PathExplorer.assert_file_exists(path):
                return "File"

        # if path is a directory we check if it has the correct format './' '../'
        elif os.path.isdir(path):
            if PathExplorer.assert_directory(path):
                return "Directory"

        else:
            return "Invalid path"


if __name__ == "__main__":
    directory = r"./_data_raw/"
    files = PathExplorer.get_all_paths_with_extension_name(directory)
    print(files)
