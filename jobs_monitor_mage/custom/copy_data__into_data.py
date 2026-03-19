if 'custom' not in globals():
    from mage_ai.data_preparation.decorators import custom
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test

from mage_ai.settings.repo import get_repo_path
import os, shutil

@custom
def copy_data_to_project_subfolder(*args, **kwargs):
    repo_path = get_repo_path()
    project_root = os.path.dirname(repo_path)

    source_dir = os.path.join(project_root,'data')
    destination_dir = os.path.join(repo_path,'data')

    try:
        if not os.path.exists(source_dir):
            print(f"⚠️ Source directory {source_dir} not found. Nothing to copy.")
            return
        os.makedirs(destination_dir, exist_ok=True)
        shutil.copytree(source_dir, destination_dir, dirs_exist_ok=True)
        print(f"✅ Successfully copied data from {source_dir} to {destination_dir}")
    except Exception as e:
        print(f"❌ Error copying files: {e}")
        raise e

    return args