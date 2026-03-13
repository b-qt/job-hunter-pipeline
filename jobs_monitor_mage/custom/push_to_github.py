import os
if 'custom' not in globals():
    from mage_ai.data_preparation.decorators import custom
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test


@custom
def push_to_github(*args, **kwargs) -> None:
    """
    push the data to github
    """
    try:
        os.system('git add /home/src/data/jobs.json /home/src/data/insights.json')
        os.system("git commit -m 'Update data from Mage'")
        os.system('git push origin main')
        print("Data pushed to GitHub successfully.")
    except Exception as e:
        print(f"An error occurred while pushing data to GitHub: {e}")

    return {}