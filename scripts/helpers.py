import os
import pandas as pd
from datetime import datetime

def save_data_to_file(data, model_name, dataset_name, output_dir='./Experiments/'):
    """Saves model performance in a CSV file with a fitting name.

    Args:
        data (pd.DataFrame): DataFrame containing model performance data.
        model_name (str): Name of the model.
        dataset_name (str): Name of the dataset.
        output_dir (str): Directory to save the CSV file to. Default is 'output'.
    """
    # Check if data is a DataFrame
    if not isinstance(data, pd.DataFrame):
        raise TypeError("The 'data' parameter must be a pandas DataFrame.")

    # Create a fitting file name with a timestamp
    timestamp = datetime.now().strftime("%Y_%m_%d_%Hh")
    file_name = f"{model_name}_{dataset_name}_performance_{timestamp}.csv"

    # Combine the output directory and file name
    file_path = os.path.join(output_dir, file_name)

    # Save the DataFrame to a CSV file
    try:
        data.to_csv(file_path, index=False)
        print(f"Model performance saved to {file_path} successfully.")
    except Exception as e:
        print(f"Error: Unable to save model performance to {file_path}. {str(e)}")



