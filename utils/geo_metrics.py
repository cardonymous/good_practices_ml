from typing import List
import pandas as pd
import numpy as np
import torch
import os
from sklearn import metrics
import ast
import sys
sys.path.append('.')

def calculate_experiment_country_accuracy(batch_df: pd.DataFrame) -> float:
    """
    Calculate accuracy score based on country labels.

    Args:
        batch_df (pd.DataFrame): DataFrame containing 'label' and 'Predicted labels'.

    Returns:
        float: Accuracy score based on country labels.
    """
    return metrics.accuracy_score(batch_df["label"].tolist(), batch_df["Predicted labels"].tolist())

def calculate_country_accuracy(country_list: pd.DataFrame, predictions: torch.Tensor, labels: torch.Tensor ) -> float:
    """
    Calculate accuracy score based on country labels.

    Args:
        country_list (pd.DataFrame): DataFrame containing country list.
        predictions (torch.Tensor): Predicted labels.
        labels (torch.Tensor): True labels. 

    Returns:
        float: Accuracy score based on country labels.
    """
    index_predictions = torch.argmax(predictions, dim=1)
    predictions = country_list['Country'].iloc[index_predictions].tolist()
    return metrics.accuracy_score(labels, predictions)

def calculate_experiment_region_accuracy(country_list: pd.DataFrame, batch_df: pd.DataFrame) -> float:
    """
    Calculate accuracy score based on region labels.

    Args:
        repo_path (str): Path to repository.
        batch_df (pd.DataFrame): DataFrame containing 'label' and 'Predicted labels'.

    Returns:
        float: Accuracy score based on region labels.
    """

    merged_df = pd.merge(batch_df, country_list, left_on='Predicted labels', right_on='Country', how='inner')
    merged_df = merged_df.rename(columns={'Intermediate Region Name': 'predicted_region'})
    del merged_df['Country']
    merged_df = pd.merge(merged_df, country_list, left_on='label', right_on='Country', how='inner')
    merged_df = merged_df.rename(columns={'Intermediate Region Name': 'reference_region'})
    del merged_df['Country']
    return metrics.accuracy_score(merged_df["reference_region"].tolist(), merged_df["predicted_region"].tolist())

def calculate_region_accuracy(country_list: pd.DataFrame, predictions: torch.Tensor, labels: torch.Tensor) -> float:
    """
    Calculate accuracy score based on region labels.

    Args:
        country_list (pd.DataFrame): DataFrame containing country list.
        predictions (torch.Tensor): Predicted labels.
        labels (torch.Tensor): True labels. 

    Returns:
        float: Accuracy score based on region labels.
    """
    index_predictions = [torch.argmax(prediciton) for prediciton in predictions]
    region_prediciotn = [country_list['Intermediate Region Name'].iloc[index.item()] for index in index_predictions]
    region_label = [country_list['Intermediate Region Name'].loc[country_list['Country'] ==index] for index in labels]

    return np.mean(metrics.accuracy_score(region_label, region_prediciotn))


def calculate_metric(repo_path: str, batch_df: pd.DataFrame, metric_name: str) -> float:
    """
    Calculate specified metric.

    Args:
        repo_path (str): Path to repository.
        batch_df (pd.DataFrame): DataFrame containing 'label' and 'Predicted labels'.
        metric_name (str): Name of the metric to be calculated ('country_acc', 'region_acc' or 'mixed').

    Returns:
        float: Calculated metric value.
    """
    country_list = pd.read_csv(f'{repo_path}/utils/country_list/country_list_region_and_continent.csv')
    batch_df['Probs-Array'] = batch_df['All-Probs'].apply(lambda x: ast.literal_eval(x))
    batch_df['Predicted labels'] = batch_df['Probs-Array'].apply(lambda x: country_list['Country'].iloc[np.argmax(np.array(x))])

    if metric_name == 'country_acc':
        return calculate_experiment_country_accuracy(batch_df)
    elif metric_name == 'region_acc':
        return calculate_experiment_region_accuracy(country_list, batch_df)
    elif metric_name == 'mixed':
        return calculate_experiment_country_accuracy(batch_df) * 0.5 + calculate_experiment_region_accuracy(country_list, batch_df) * 0.5
    else:
        raise ValueError(f"The metric {metric_name} is not known.")
    
def calculate_experiment_metric(repo_path: str, exp_dir:str, metric_name: str) -> list:
    """
    Calculate metric for each experiment directory.

    Args:
        repo_path (str): Path to repository.
        exp_dirs (List[str]): List of experiment directories.
        exp_names (List[str]): List of experiment names.
        metric_name (str): Name of the metric to be calculated ('country_acc', 'region_acc' or 'mixed').

    Returns:
        dict: Dictionary with experiment names as keys and corresponding metric values as lists.
    """
    exp_metric = []
    for batch_file in os.listdir(exp_dir):
        if not os.path.isdir(os.path.join(exp_dir, batch_file)):
            batch_df = pd.read_csv(os.path.join(exp_dir, batch_file))
            exp_metric.append(calculate_metric(repo_path, batch_df, metric_name))
    return exp_metric
