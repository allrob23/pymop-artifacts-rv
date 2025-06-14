import zipfile
import os

def unzip_all_in_folder(folder_path):
    # Convert to absolute path first
    abs_folder_path = os.path.abspath(folder_path)
    
    # Check if the folder exists
    if not os.path.exists(abs_folder_path):
        print(f"The folder '{abs_folder_path}' does not exist.")
        return
    
    # Get the directory and base name of the folder path
    parent_dir = os.path.dirname(abs_folder_path)
    base_name = os.path.basename(abs_folder_path)
    
    # Create a parallel folder with "_unzipped" appended to the base name
    unzipped_folder_path = os.path.join(parent_dir, base_name + "_unzipped")
    os.makedirs(unzipped_folder_path, exist_ok=True)
    
    # Loop through all files in the folder
    for file_name in os.listdir(abs_folder_path):
        if file_name.endswith('.zip'):
            # Full path to the zip file
            zip_file_path = os.path.join(abs_folder_path, file_name)
            
            # Set extraction path to the new folder
            extract_folder = os.path.join(unzipped_folder_path, os.path.splitext(file_name)[0])
            os.makedirs(extract_folder, exist_ok=True)
            
            # Unzip the file
            with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
                zip_ref.extractall(extract_folder)
            
            print(f"Unzipped '{file_name}' into '{extract_folder}'")

# Example usage
folder_path = '.'
unzip_all_in_folder(folder_path)