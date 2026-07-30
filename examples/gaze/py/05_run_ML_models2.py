import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.feature_selection import SelectFromModel
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.metrics import (accuracy_score, precision_score, recall_score, 
                             roc_auc_score, roc_curve, confusion_matrix)

# ==========================================
# 0. LOAD DATA & EXTRACT TARGETS
# ==========================================
print("--- Loading Data and Extracting Targets ---")
df = pd.read_csv('allregressors.csv')

# Extract 'C' or 'P' based on the first letter of 'subj'
df['Class'] = df['subj'].astype(str).apply(
    lambda x: 'C' if x.startswith('C') else ('P' if x.startswith('P') else None)
)

# Clean up rows that didn't match
df = df.dropna(subset=['Class'])

# Separate features (X) and target (y)
df_X = df.drop(columns=['subj', 'Class'])
df_y = df['Class']

# Encode target variable: 'C' -> 0, 'P' -> 1
le = LabelEncoder()
y_encoded = le.fit_transform(df_y) 

# Standardize the features
scaler = StandardScaler()
X_scaled = scaler.fit_transform(df_X)
X_scaled = pd.DataFrame(X_scaled, columns=df_X.columns)

# ==========================================
# 1. CROSS-CORRELATION CLUSTERMAP
# ==========================================
# This reveals the "meta" factors before LASSO crushes them
print("\n--- Generating Cross-Correlation Clustermap ---")
corr_matrix = df_X.corr()

# Clustermap automatically groups highly correlated variables together
g = sns.clustermap(corr_matrix, cmap='coolwarm', center=0, 
                   annot=False, figsize=(10, 10), 
                   cbar_kws={'label': 'Pearson Correlation'})
g.fig.suptitle("Regressor Cross-Correlations (Grouped by Similarity)", y=1.02, fontsize=14)
plt.show()

# ==========================================
# 2. FEATURE SELECTION (LASSO)
# ==========================================
print("\n--- Running LASSO Feature Selection ---")
lasso_selector = LogisticRegression(penalty='l1', solver='liblinear', random_state=42, C=0.5)
lasso_selector.fit(X_scaled, y_encoded)

model_selector = SelectFromModel(lasso_selector, prefit=True)
selected_mask = model_selector.get_support()
selected_features = X_scaled.columns[selected_mask]
X_selected = X_scaled.loc[:, selected_mask]

# Store absolute coefficients for ranking later
coefs = np.abs(lasso_selector.coef_[0])

print(f"Selected {len(selected_features)} features out of {len(df_X.columns)}")




# ==========================================
# 2. CROSS-VALIDATED MODELING (Updated for Specificity)
# ==========================================
models = {
    "Logistic Regression": LogisticRegression(random_state=42),
    "LDA": LinearDiscriminantAnalysis(),
    "SVM (RBF)": SVC(probability=True, random_state=42),
    "Random Forest": RandomForestClassifier(n_estimators=100, random_state=42)
}

cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
results_list = []

print("--- Running Cross-Validation ---")
if len(selected_features) > 0:
    for name, model in models.items():
        y_pred = cross_val_predict(model, X_selected, y_encoded, cv=cv)
        y_prob = cross_val_predict(model, X_selected, y_encoded, cv=cv, method='predict_proba')[:, 1]
        
        # Extract Confusion Matrix components
        cm = confusion_matrix(y_encoded, y_pred)
        tn, fp, fn, tp = cm.ravel()
        
        # Calculate Metrics
        acc = accuracy_score(y_encoded, y_pred)
        sens = tp / (tp + fn) if (tp + fn) > 0 else 0  # Sensitivity (Recall)
        spec = tn / (tn + fp) if (tn + fp) > 0 else 0  # Specificity
        auc = roc_auc_score(y_encoded, y_prob)
        
        results_list.append({
            "Model": name, 
            "Accuracy": acc, 
            "Sensitivity": sens, 
            "Specificity": spec, 
            "AUROC": auc
        })

    # Output clean results table
    results_df = pd.DataFrame(results_list).round(3)
    print("\nModel Performance Table:")
    print(results_df.to_string(index=False))

    # ==========================================
    # 3. PLOT: MODEL METRICS COMPARISON
    # ==========================================
    print("\n--- Generating Model Comparison Plot ---")
    
    # Reshape the dataframe for seaborn grouped bar plot using pd.melt
    df_melted = results_df.melt(id_vars="Model", 
                                value_vars=["Accuracy", "Sensitivity", "Specificity", "AUROC"],
                                var_name="Metric", 
                                value_name="Score")
    
    plt.figure(figsize=(12, 6))
    
    # Custom palette: Green, Orange, Purple, Gray (strictly avoiding Red/Blue)
    safe_palette = ['#2ca02c', '#ff7f0e', '#9467bd', '#7f7f7f']
    
    ax = sns.barplot(data=df_melted, x='Model', y='Score', hue='Metric', palette=safe_palette)
    
    plt.title("Machine Learning Model Performance Comparison", fontsize=14, pad=15)
    plt.ylabel("Score (0.0 to 1.0)", fontsize=12)
    plt.xlabel("Model", fontsize=12)
    plt.ylim(0, 1.05) # Add a little headroom above 1.0 for the legend
    
    # Move the legend outside the plot so it doesn't cover the bars
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left', title="Metrics")
    
    # Add numerical labels on top of the bars for exact reading
    for container in ax.containers:
        ax.bar_label(container, fmt='%.2f', padding=3, size=9)
        
    plt.tight_layout()
    plt.show()

    pass;

'''
# ==========================================
# 3. CROSS-VALIDATED MODELING
# ==========================================
models = {
    "Logistic Regression": LogisticRegression(random_state=42),
    "LDA": LinearDiscriminantAnalysis(),
    "SVM (RBF)": SVC(probability=True, random_state=42),
    "Random Forest": RandomForestClassifier(n_estimators=100, random_state=42)
}

cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
results_list = []
roc_data = {}

print("--- Running Cross-Validation ---")
if len(selected_features) > 0:
    for name, model in models.items():
        y_pred = cross_val_predict(model, X_selected, y_encoded, cv=cv)
        y_prob = cross_val_predict(model, X_selected, y_encoded, cv=cv, method='predict_proba')[:, 1]
        
        acc = accuracy_score(y_encoded, y_pred)
        prec = precision_score(y_encoded, y_pred, zero_division=0) 
        rec = recall_score(y_encoded, y_pred, zero_division=0)
        auc = roc_auc_score(y_encoded, y_prob)
        cm = confusion_matrix(y_encoded, y_pred)
        
        results_list.append({
            "Model": name, "Accuracy": acc, "Precision (P)": prec, 
            "Recall (P)": rec, "AUROC": auc
        })
        
        fpr, tpr, _ = roc_curve(y_encoded, y_prob)
        roc_data[name] = (fpr, tpr, auc, cm)

    print("\nModel Performance Table:")
    print(pd.DataFrame(results_list).round(3).to_string(index=False))

'''

# ==========================================
# 4. PLOTS: TOP VARIABLES (DISTRIBUTIONS & BOXPLOTS)
# ==========================================
print("\n--- Generating Plots for Top Variables ---")

if len(selected_features) > 0:
    # Identify the top 4 features by LASSO coefficient magnitude
    top_n = min(4, len(selected_features))
    
    # Sort the selected features by their coefficient magnitude
    sorted_indices = np.argsort(-coefs[selected_mask])
    top_features = selected_features[sorted_indices][:top_n]
    
    # Custom color palette matching your request
    custom_palette = {'C': 'blue', 'P': 'red'}

    for feature in top_features:
        fig, axes = plt.subplots(1, 2, figsize=(14, 5))
        
        # Plot A: Overlapping Histograms / KDE
        sns.histplot(data=df, x=feature, hue='Class', palette=custom_palette, 
                     kde=True, ax=axes[0], alpha=0.4, stat="density", 
                     common_norm=False, element="step")
        axes[0].set_title(f"Distribution of {feature}")
        axes[0].set_ylabel("Density")
        
        # Plot B: Box & Whisker Plot
        sns.boxplot(data=df, x='Class', y=feature, palette=custom_palette, ax=axes[1])
        # Add swarmplot overlay for data point visibility (optional but highly recommended)
        sns.swarmplot(data=df, x='Class', y=feature, color='black', alpha=0.5, ax=axes[1])
        axes[1].set_title(f"Boxplot of {feature} (Control vs. Patient)")
        
        plt.tight_layout()
        plt.show()
