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
# Load the data from the CSV file
df = pd.read_csv('allregressors.csv')

EXCLUDE_CENTERBIAS=True;
if(EXCLUDE_CENTERBIAS):
    df = df[ [c for c in df.columns if 'centerbias' not in c ] ];
    pass;
#print(df[ [ c for c in df.columns if 'pupil' in c]] );
# Ensure the 'subj' column is treated as a string, then extract 'C' or 'P'
# This creates a new column called 'Class' based on the first letter
df['Class'] = df['subj'].astype(str).apply(
    lambda x: 'C' if x.startswith('C') else ('P' if x.startswith('P') else None)
)

# Drop any rows where the subject ID didn't start with C or P (data cleaning)
initial_len = len(df)
df = df.dropna(subset=['Class'])
if len(df) < initial_len:
    print(f"Dropped {initial_len - len(df)} rows that did not start with 'C' or 'P'.")

# Separate features (X) and target (y)
# We must drop 'subj' so the model doesn't try to use the string ID as a regressor, 
# and drop 'Class' because it's our target variable.
df_X = df.drop(columns=['subj', 'Class'])
df_y = df['Class']

print(f"Dataset shape (Regressors only): {df_X.shape}")
print(f"Class distribution:\n{df_y.value_counts()}\n")

# Encode target variable: 'C' -> 0, 'P' -> 1
le = LabelEncoder()
y_encoded = le.fit_transform(df_y) 
print(f"Class mapping: {dict(zip(le.classes_, le.transform(le.classes_)))}")

# Standardize the features
# Note: This assumes all remaining columns in df_X are numeric regressors.
# If you have non-numeric regressors, you will need to use pd.get_dummies() first.
scaler = StandardScaler()
X_scaled = scaler.fit_transform(df_X)
X_scaled = pd.DataFrame(X_scaled, columns=df_X.columns)

# ==========================================
# 1. FEATURE SELECTION (LASSO)
# ==========================================
print("\n--- Running LASSO Feature Selection ---")
# C=0.5 controls regularization. Smaller C = fewer features selected. 
# You may need to tune this if it selects too many or zero features.
lasso_selector = LogisticRegression(penalty='l1', solver='liblinear', random_state=42, C=0.5)
lasso_selector.fit(X_scaled, y_encoded)

# Get selected features
model_selector = SelectFromModel(lasso_selector, prefit=True)
selected_mask = model_selector.get_support()
selected_features = X_scaled.columns[selected_mask]
X_selected = X_scaled.loc[:, selected_mask]

print(f"Selected {len(selected_features)} features out of {len(df_X.columns)}:")
print(list(selected_features), "\n")

# Plot Feature Importances
if len(selected_features) > 0:
    coefs = np.abs(lasso_selector.coef_[0])
    plt.figure(figsize=(10, max(4, len(selected_features) * 0.3))) # Dynamic height
    sns.barplot(x=coefs[selected_mask], y=selected_features, palette="viridis")
    plt.title("LASSO Feature Selection: Selected Feature Magnitudes")
    plt.xlabel("Absolute Coefficient")
    plt.tight_layout()
    #plt.show()
    plt.savefig('regressor_coeffs.pdf');
    plt.close();
else:
    print("Warning: LASSO selected 0 features. Try increasing 'C' in LogisticRegression (e.g., C=1.0 or C=10).")

# ==========================================
# 2. CROSS-VALIDATED MODELING
# ==========================================
models = {
    "Logistic Regression": LogisticRegression(random_state=42),
    "LDA": LinearDiscriminantAnalysis(),
    "SVM (RBF)": SVC(probability=True, random_state=42),
    "Random Forest": RandomForestClassifier(n_estimators=100, random_state=42)
}

# Stratified K-Fold ensures 'C' and 'P' are balanced across all folds
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
results_list = []
roc_data = {}

print("--- Running Cross-Validation ---")
if len(selected_features) > 0:
    for name, model in models.items():
        # Get out-of-fold predictions
        y_pred = cross_val_predict(model, X_selected, y_encoded, cv=cv)
        y_prob = cross_val_predict(model, X_selected, y_encoded, cv=cv, method='predict_proba')[:, 1]
        
        # Calculate Metrics (Precision/Recall calculated for 'P' class by default)
        acc = accuracy_score(y_encoded, y_pred)
        prec = precision_score(y_encoded, y_pred, zero_division=0) 
        rec = recall_score(y_encoded, y_pred, zero_division=0)
        auc = roc_auc_score(y_encoded, y_prob)
        cm = confusion_matrix(y_encoded, y_pred)
        
        results_list.append({
            "Model": name,
            "Accuracy": acc,
            "Precision (Patient)": prec,
            "Recall (Patient)": rec,
            "AUROC": auc
        })
        
        # Store ROC curve data
        fpr, tpr, _ = roc_curve(y_encoded, y_prob)
        roc_data[name] = (fpr, tpr, auc, cm)

    # Output clean results table
    results_df = pd.DataFrame(results_list).round(3)
    print("\nModel Performance Table (Cross-Validated):")
    print(results_df.to_string(index=False))

    # ==========================================
    # 3. PLOTS: ROC CURVES & CONFUSION MATRICES
    # ==========================================
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))

    # Plot 1: ROC Curves
    ax = axes[0]
    for name, (fpr, tpr, auc, _) in roc_data.items():
        ax.plot(fpr, tpr, label=f"{name} (AUC = {auc:.2f})")

    ax.plot([0, 1], [0, 1], 'k--', label="Random Guess")
    ax.set_title("Receiver Operating Characteristic (ROC)")
    ax.set_xlabel("False Positive Rate")
    ax.set_ylabel("True Positive Rate")
    ax.legend(loc="lower right")
    ax.grid(alpha=0.3)

    # Plot 2: Confusion Matrix for the best model (by AUROC)
    best_model_name = results_df.loc[results_df['AUROC'].idxmax(), 'Model']
    best_cm = roc_data[best_model_name][3]

    ax2 = axes[1]
    sns.heatmap(best_cm, annot=True, fmt='d', cmap='Blues', ax=ax2, 
                xticklabels=le.classes_, yticklabels=le.classes_)
    ax2.set_title(f"Confusion Matrix: {best_model_name} (Best AUROC)")
    ax2.set_xlabel("Predicted Class")
    ax2.set_ylabel("Actual Class")

    plt.tight_layout()
    #plt.show()
    plt.savefig('regressor_results.pdf');
    plt.close();
