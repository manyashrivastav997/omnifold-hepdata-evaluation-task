"""
Weighted histogram computation for physics analysis.

This module provides a function to compute and plot weighted histograms.
Weighted histograms are commonly used in physics analyses where each event
has an associated weight (e.g., from Monte Carlo simulations). The function
includes validation, optional plotting, and uncertainty calculation.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os
from typing import Union, Tuple, Optional


def weighted_histogram(
    data: Union[pd.DataFrame, np.ndarray, pd.Series],
    observable: Optional[Union[str, np.ndarray, pd.Series]] = None,
    weight_column: Optional[Union[str, np.ndarray, pd.Series]] = None,
    bins: Union[int, np.ndarray] = 20,
    range: Optional[Tuple[float, float]] = None,
    density: bool = False,
    plot: bool = True,
    xlabel: Optional[str] = None,
    ylabel: Optional[str] = None,
    title: Optional[str] = None,
    figsize: Tuple[float, float] = (10, 6),
    save_path: Optional[str] = None,
    return_uncertainty: bool = False
) -> Union[Tuple[np.ndarray, np.ndarray, np.ndarray], Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]]:
    """
    Compute a weighted histogram from data.
    
    This function creates histograms where each data point has an associated weight.
    It supports both DataFrame and array inputs, optional density normalization,
    plotting with matplotlib, and statistical uncertainty calculation.
    
    Parameters
    ----------
    data : pd.DataFrame, np.ndarray, or pd.Series
        Input data. If DataFrame, specify observable and weight_column as column names.
        If array/Series, these are the observable values.
    observable : str, np.ndarray, pd.Series, or None
        Observable to histogram. Column name if data is DataFrame, otherwise array of values.
    weight_column : str, np.ndarray, pd.Series, or None
        Event weights. Column name if data is DataFrame, otherwise array of weights.
        If None, uniform weights are used.
    bins : int or array-like, default 20
        Number of bins or bin edges.
    range : tuple of float, optional
        (min, max) range for binning. Required if bins is an integer.
    density : bool, default False
        If True, normalize histogram to unit area.
    plot : bool, default True
        If True, create a matplotlib plot.
    xlabel, ylabel, title : str, optional
        Plot labels and title.
    figsize : tuple of float, default (10, 6)
        Figure size in inches.
    save_path : str, optional
        If provided, save plot to this file path.
    return_uncertainty : bool, default False
        If True, compute and return statistical uncertainties.
    
    Returns
    -------
    hist : np.ndarray
        Histogram bin values.
    bin_edges : np.ndarray
        Bin edge positions (length = len(hist) + 1).
    bin_centers : np.ndarray
        Bin center positions (length = len(hist)).
    uncertainty : np.ndarray, optional
        Statistical uncertainty per bin (only if return_uncertainty=True).
    
    Examples
    --------
    >>> df = pd.DataFrame({'pT': [50, 100, 150], 'weight': [1.2, 0.9, 1.1]})
    >>> hist, edges, centers = weighted_histogram(df, 'pT', 'weight', bins=10, range=(0, 200))
    
    >>> # With uncertainty
    >>> hist, edges, centers, unc = weighted_histogram(
    ...     df, 'pT', 'weight', bins=10, range=(0, 200),
    ...     return_uncertainty=True, plot=False
    ... )
    """
    
    # Parse input format
    if isinstance(data, pd.DataFrame):
        if observable is None or weight_column is None:
            raise ValueError("observable and weight_column required when data is DataFrame")
        if not isinstance(observable, str) or not isinstance(weight_column, str):
            raise TypeError("observable and weight_column must be column names (str) for DataFrame input")
        
        if observable not in data.columns:
            raise ValueError(f"Observable '{observable}' not found in DataFrame")
        if weight_column not in data.columns:
            raise ValueError(f"Weight column '{weight_column}' not found in DataFrame")
        
        obs_data = data[observable].values
        weights = data[weight_column].values
        obs_name = observable
        
    else:
        # Array or Series input
        if isinstance(data, pd.Series):
            obs_data = data.values
            obs_name = data.name if data.name else "observable"
        else:
            obs_data = np.asarray(data)
            obs_name = "observable"
        
        if observable is not None:
            obs_data = np.asarray(observable) if not isinstance(observable, pd.Series) else observable.values
            obs_name = observable.name if isinstance(observable, pd.Series) and observable.name else obs_name
        
        if weight_column is None:
            weights = np.ones(len(obs_data))
        elif isinstance(weight_column, str):
            raise TypeError("weight_column cannot be str for array input")
        else:
            weights = np.asarray(weight_column) if not isinstance(weight_column, pd.Series) else weight_column.values
    
    # Validate data
    if len(obs_data) == 0:
        raise ValueError("Observable data is empty")
    if len(weights) == 0:
        raise ValueError("Weight data is empty")
    if len(obs_data) != len(weights):
        raise ValueError(f"Length mismatch: {len(obs_data)} observables vs {len(weights)} weights")
    
    # Check for NaN or inf values
    if np.any(~np.isfinite(obs_data)):
        raise ValueError(f"Observable contains {np.sum(~np.isfinite(obs_data))} non-finite values")
    if np.any(~np.isfinite(weights)):
        raise ValueError(f"Weights contain {np.sum(~np.isfinite(weights))} non-finite values")
    
    # Negative weights are valid in some physics contexts (e.g., NLO corrections)
    if np.any(weights < 0):
        print(f"Warning: {np.sum(weights < 0)} negative weights detected")
    
    # Validate bins
    if isinstance(bins, int):
        if bins <= 0:
            raise ValueError(f"Number of bins must be positive, got {bins}")
        if range is None:
            raise ValueError("range required when bins is int")
        if not isinstance(range, (tuple, list)) or len(range) != 2:
            raise ValueError("range must be (min, max) tuple")
        if range[0] >= range[1]:
            raise ValueError(f"Invalid range: {range}")
    else:
        bins = np.asarray(bins)
        if len(bins) < 2:
            raise ValueError("Bin edges must have at least 2 elements")
        if not np.all(np.diff(bins) > 0):
            raise ValueError("Bin edges must be strictly increasing")
    
    # Compute histogram
    hist, bin_edges = np.histogram(obs_data, bins=bins, range=range, weights=weights, density=density)
    bin_centers = 0.5 * (bin_edges[:-1] + bin_edges[1:])
    
    # Compute uncertainty if requested
    uncertainty = None
    if return_uncertainty:
        uncertainty = np.sqrt(np.histogram(obs_data, bins=bin_edges, weights=weights**2)[0])
    
    # Plotting
    if plot or save_path:
        fig, ax = plt.subplots(figsize=figsize)
        
        # Step plot (standard in physics)
        ax.step(bin_edges, np.append(hist, hist[-1]), where='post', linewidth=2, label='Weighted histogram')
        
        # Add error bars if uncertainty computed
        if return_uncertainty:
            ax.errorbar(bin_centers, hist, yerr=uncertainty, fmt='none', color='black', capsize=2, label='Statistical uncertainty')
        
        ax.set_xlabel(xlabel if xlabel else obs_name, fontsize=12)
        ax.set_ylabel(ylabel if ylabel else ("Density" if density else "Weighted Events"), fontsize=12)
        if title:
            ax.set_title(title, fontsize=14)
        
        ax.grid(True, alpha=0.3, linestyle='--')
        
        # Add statistics box
        stats_text = f"Events: {len(obs_data)}\nTotal weight: {np.sum(weights):.2e}"
        ax.text(0.95, 0.95, stats_text, transform=ax.transAxes,
                verticalalignment='top', horizontalalignment='right',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5), fontsize=10)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
        
        if plot:
            plt.show()
        else:
            plt.close()
    
    # Return results
    if return_uncertainty:
        return hist, bin_edges, bin_centers, uncertainty
    else:
        return hist, bin_edges, bin_centers


def run_tests():
    """Run basic validation tests."""
    print("Running tests...\n")
    
    # Test 1: Basic functionality with uniform weights
    print("Test 1: Basic histogram")
    df = pd.DataFrame({'pT': np.random.uniform(0, 200, 1000), 'weight': np.ones(1000)})
    hist, edges, centers = weighted_histogram(df, 'pT', 'weight', bins=20, range=(0, 200), plot=False)
    assert len(hist) == 20 and len(edges) == 21 and len(centers) == 20
    assert np.isclose(np.sum(hist), 1000)
    print("✓ Passed\n")
    
    # Test 2: Weight preservation
    print("Test 2: Weight preservation")
    df['weight'] = np.random.uniform(0.5, 1.5, 1000)
    hist, edges, centers = weighted_histogram(df, 'pT', 'weight', bins=20, range=(0, 200), plot=False)
    assert np.isclose(np.sum(hist), np.sum(df['weight']))
    print("✓ Passed\n")
    
    # Test 3: Array input
    print("Test 3: Array input")
    pT_array = np.random.uniform(0, 200, 500)
    weight_array = np.random.uniform(0.8, 1.2, 500)
    hist, edges, centers = weighted_histogram(pT_array, weight_column=weight_array, bins=15, range=(0, 200), plot=False)
    assert len(hist) == 15
    print("✓ Passed\n")
    
    # Test 4: Density normalization
    print("Test 4: Density normalization")
    hist_density, edges, centers = weighted_histogram(df, 'pT', 'weight', bins=20, range=(0, 200), density=True, plot=False)
    integral = np.sum(hist_density * np.diff(edges))
    assert np.isclose(integral, 1.0, rtol=1e-5)
    print("✓ Passed\n")
    
    # Test 5: NaN detection
    print("Test 5: NaN detection")
    df_invalid = df.copy()
    df_invalid.loc[0, 'weight'] = np.nan
    try:
        weighted_histogram(df_invalid, 'pT', 'weight', bins=10, range=(0, 100), plot=False)
        assert False, "Should raise ValueError"
    except ValueError as e:
        assert "non-finite" in str(e)
    print("✓ Passed\n")
    
    # Test 6: Uncertainty calculation
    print("Test 6: Uncertainty calculation")
    hist, edges, centers, unc = weighted_histogram(df, 'pT', 'weight', bins=20, range=(0, 200), 
                                                     return_uncertainty=True, plot=False)
    assert unc is not None and len(unc) == len(hist)
    assert np.all(unc >= 0)
    print("✓ Passed\n")
    
    print("="*50)
    print("All tests passed!")
    print("="*50)


if __name__ == "__main__":
    run_tests()
    
    # Example usage
    print("\nExample: Dilepton pT distribution")
    df_example = pd.DataFrame({
        'pT_ll': np.random.exponential(100, 5000),
        'weights_nominal': np.random.uniform(0.8, 1.2, 5000)
    })
    
    hist, edges, centers = weighted_histogram(
        df_example, 
        'pT_ll', 
        'weights_nominal',
        bins=30,
        range=(0, 500),
        xlabel='Dilepton $p_T$ [GeV]',
        ylabel='Events / 16.7 GeV',
        title='Weighted Histogram Example',
        plot=True
    )
