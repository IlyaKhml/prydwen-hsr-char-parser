import pickle
import os

def save_result_to_file(result, filename):
    """
    Saves the result dictionary containing DataFrames, lists, and other structures into a file.
    
    Args:
        result (dict): The dictionary to save.
        filename (str): The file path to save the data.
    """

    try:
        os.makedirs(os.path.dirname(filename), exist_ok=True)
        with open(filename, 'wb') as file:
            pickle.dump(result, file)
    
    except Exception as e:
        print(f"Error saving data: {e}")


def load_result_from_file(filename):
    """
    Loads the result dictionary from a file.
    
    Args:
        filename (str): The file path to load the data from.
        
    Returns:
        dict: The loaded result dictionary.
    """
    try:
        with open(filename, 'rb') as file:
            result = pickle.load(file)

        return result
    
    except Exception as e:
        print(f"Error loading data: {e}")
        return None