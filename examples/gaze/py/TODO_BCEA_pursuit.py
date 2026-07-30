import numpy as np
import scipy.stats as stats
import matplotlib.pyplot as plt

def calculate_bcea(x, y, p=0.6827):
    """
    Calculates the Bivariate Contour Ellipse Area (BCEA).
    
    Parameters:
    x, y (array-like): Arrays of gaze coordinates.
    p (float): Probability area (default 0.6827 for 1 standard deviation).
    
    Returns:
    float: The area of the ellipse in the squared units of x and y.
    """
    x = np.asarray(x)
    y = np.asarray(y)
    
    # Need at least 2 points to compute covariance
    if len(x) < 2 or len(y) < 2:
        return np.nan
        
    # Covariance matrix of x and y
    cov_matrix = np.cov(x, y)
    
    # Eigenvalues give the variance along the principal axes
    eigenvalues, _ = np.linalg.eigh(cov_matrix)
    
    # Clip negative values that can occur from floating point errors on perfectly straight lines
    eigenvalues = np.maximum(eigenvalues, 0)
    
    # Chi-square value for 2 degrees of freedom at probability p
    chi2_val = stats.chi2.ppf(p, 2)
    
    # Area of ellipse
    bcea = np.pi * chi2_val * np.sqrt(eigenvalues[0] * eigenvalues[1])
    return bcea

def calculate_detrended_bcea(x, y, p=0.6827):
    """
    Removes the linear trajectory (smooth pursuit) before calculating BCEA.
    This isolates the 'wobble' or noise during the pursuit.
    """
    x = np.asarray(x)
    y = np.asarray(y)
    
    if len(x) < 2:
        return np.nan
        
    time = np.arange(len(x))
    
    # Fit a 1st degree polynomial (line) and subtract it
    x_detrended = x - np.polyval(np.polyfit(time, x, 1), time)
    y_detrended = y - np.polyval(np.polyfit(time, y, 1), time)
    
    return calculate_bcea(x_detrended, y_detrended, p)

# ==========================================
# TEST AND VISUALIZE THE DIFFERENCE
# ==========================================
# 1. Simulate a stationary fixation (just noise around a center point)
fix_x = np.random.normal(500, 5, 100)
fix_y = np.random.normal(500, 5, 100)

# 2. Simulate a smooth pursuit (moving diagonally across the screen + noise)
time_steps = np.arange(100)
pursuit_x = 200 + (3 * time_steps) + np.random.normal(0, 5, 100)
pursuit_y = 200 + (3 * time_steps) + np.random.normal(0, 5, 100)

print("--- BCEA Results ---")
print(f"Stationary Fixation Standard BCEA: {calculate_bcea(fix_x, fix_y):.2f}")

print(f"Smooth Pursuit Standard BCEA:      {calculate_bcea(pursuit_x, pursuit_y):.2f} (Massive, misleading)")
print(f"Smooth Pursuit Detrended BCEA:     {calculate_detrended_bcea(pursuit_x, pursuit_y):.2f} (Accurate noise measurement)")
