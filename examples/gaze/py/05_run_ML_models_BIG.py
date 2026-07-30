import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import statsmodels.api as sm
import sys;

from sklearn.decomposition import PCA
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.feature_selection import SelectFromModel, RFECV
from sklearn.linear_model import LogisticRegression
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.metrics import (accuracy_score, roc_auc_score, roc_curve, confusion_matrix)

ext='.png';

def bootstrap_auc_ci(y_true, y_pred_proba, n_bootstraps=1000):
    """Calculates 95% CI for AUROC using bootstrapping."""
    rng = np.random.RandomState(42)
    bootstrapped_scores = []
    
    for i in range(n_bootstraps):
        # resample predictions with replacement
        indices = rng.randint(0, len(y_pred_proba), len(y_pred_proba))
        if len(np.unique(y_true[indices])) < 2:
            continue # Skip if bootstrap sample only has 1 class by chance
            
        score = roc_auc_score(y_true[indices], y_pred_proba[indices])
        bootstrapped_scores.append(score)
        
    sorted_scores = np.array(bootstrapped_scores)
    sorted_scores.sort()
    
    ci_lower = sorted_scores[int(0.025 * len(sorted_scores))]
    ci_upper = sorted_scores[int(0.975 * len(sorted_scores))]
    return ci_lower, ci_upper

def cohens_d(group1, group2):
    """Calculates Cohen's d effect size."""
    n1, n2 = len(group1), len(group2)
    var1, var2 = np.var(group1, ddof=1), np.var(group2, ddof=1)
    pooled_sd = np.sqrt(((n1 - 1) * var1 + (n2 - 1) * var2) / (n1 + n2 - 2))
    return (np.mean(group1) - np.mean(group2)) / pooled_sd


# ==========================================
# 0. SETUP & DATA LOADING
# ==========================================
print("--- 0. Loading Data ---")
df = pd.read_csv('allregressors.csv')
if( len(sys.argv) > 0 ):
    minsecs = float(sys.argv[1]);
    minsubjs = int(sys.argv[2]);
    pass;
else:
    minsecs = 4;
    minsubjs = 40;
    pass

df = df[ (df.minviewsecs == minsecs) & (df.minviewsubjs == minsubjs) ].reset_index(drop=True);

print(df);

REMOVE_CENT_BIAS=False;
if(REMOVE_CENT_BIAS):
    df = df[[c for c in df.columns if 'centerbias' not in c]]
    pass;

# Extract 'C' (Controls) or 'P' (Patients)
df['Class'] = df['subj'].astype(str).apply(
    lambda x: 'C' if x.startswith('C') else ('P' if x.startswith('P') else None)
)
df = df.dropna(subset=['Class'])

# Separate features (X) and target (y)
df_X = df.drop(columns=['subj', 'Class',
                        'minviewsubjs',
                        'minviewsecs',
                        'minviewvids']);
df_y = df['Class']

constant_columns = [col for col in df_X.columns if df_X[col].nunique() <= 1]
if len(constant_columns) > 0:
    df_X = df_X.drop(columns=constant_columns)
    print(constant_columns)
    print(f"Dropped {len(constant_columns)} constant columns (zero variance):")
    pass;
    #raise Exception(f"Dropped {len(constant_columns)} constant columns (zero variance):")
    
# Encode target: 'C' -> 0, 'P' -> 1
le = LabelEncoder()
y_encoded = le.fit_transform(df_y) 

# Standardize the features
scaler = StandardScaler()
X_scaled = pd.DataFrame(scaler.fit_transform(df_X), columns=df_X.columns)

# Define custom palettes
cp_classes = {'C': 'blue', 'P': 'red'}  
cp_models = ['#2ca02c', '#ff7f0e', '#9467bd', '#7f7f7f'] 

# ==========================================
# 1. PCA VISUALIZATION
# ==========================================
print("--- 1. Generating PCA Plot ---")
pca = PCA(n_components=2)
X_pca = pca.fit_transform(X_scaled)

plt.figure(figsize=(8, 6))
sns.scatterplot(x=X_pca[:, 0], y=X_pca[:, 1], hue=df_y, palette=cp_classes, alpha=0.7)
plt.title(f"PCA of Regressors\nPC1: {pca.explained_variance_ratio_[0]:.1%} | PC2: {pca.explained_variance_ratio_[1]:.1%}")
plt.xlabel("Principal Component 1")
plt.ylabel("Principal Component 2")
plt.legend(title="Group")
plt.tight_layout()
plt.savefig("01_PCA_Plot"+ext, bbox_inches='tight')
plt.close()

# ==========================================
# 2. CROSS-CORRELATION CLUSTERMAP
# ==========================================
print("--- 2. Generating Clustermap ---")
corr_matrix = df_X.corr()
g = sns.clustermap(corr_matrix, cmap='coolwarm', center=0, annot=False, figsize=(12, 12))
g.fig.suptitle("Regressor Cross-Correlations (Grouped by Similarity)", y=1.02)
g.savefig("02_CrossCorrelation_Clustermap"+ext, bbox_inches='tight')
plt.close(g.fig) 

# ==========================================
# 3. RECURSIVE FEATURE ELIMINATION (RFECV)
# ==========================================
print("--- 3. Running RFECV ---")
cv_rfe = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
rfe_estimator = RandomForestClassifier(n_estimators=100, random_state=42)
rfecv = RFECV(estimator=rfe_estimator, step=1, cv=cv_rfe, scoring='roc_auc')
rfecv.fit(X_scaled, y_encoded)

plt.figure(figsize=(8, 5))
if hasattr(rfecv, 'cv_results_'):
    scores = rfecv.cv_results_['mean_test_score']
else:
    scores = rfecv.grid_scores_ 
    
plt.plot(range(1, len(scores) + 1), scores, marker='o', color='black')
plt.title("RFECV: Model Performance vs. Number of Features")
plt.xlabel("Number of Features Selected")
plt.ylabel("Cross-Validated AUROC")
plt.grid(True, alpha=0.3)
plt.axvline(x=rfecv.n_features_, color='red', linestyle='--', label=f'Optimal: {rfecv.n_features_} features')
plt.legend()
plt.tight_layout()
plt.savefig("03_RFECV_Performance"+ext, bbox_inches='tight')
plt.close()

# ==========================================
# 4. LASSO FEATURE SELECTION
# ==========================================
print("--- 4. Running LASSO ---")
# Updated for sklearn 1.8: Use l1_ratio=1.0 for an L1 (LASSO) penalty
lasso = LogisticRegression(solver='saga', l1_ratio=1.0, random_state=42, C=0.5, max_iter=2000)
#lasso = LogisticRegression(penalty='l1', solver='liblinear', random_state=42, C=0.5)
lasso.fit(X_scaled, y_encoded)

selected_mask = SelectFromModel(lasso, prefit=True).get_support()
selected_features = X_scaled.columns[selected_mask]
X_selected = X_scaled.loc[:, selected_mask]

# Store all absolute coefficients mapped to their feature names
all_features = df_X.columns
lasso_coefs_abs = np.abs(lasso.coef_[0])
feature_weights = dict(zip(all_features, lasso_coefs_abs))

# Plot LASSO Coefs for selected features only
if len(selected_features) > 0:
    coefs_selected = lasso_coefs_abs[selected_mask]
    sorted_idx = np.argsort(-coefs_selected)
    top_features = selected_features[sorted_idx]

    plt.figure(figsize=(10, max(4, len(top_features) * 0.4)))
    sns.barplot(x=coefs_selected[sorted_idx], y=top_features, hue=top_features, palette="viridis", legend=False)
    #sns.barplot(x=coefs_selected[sorted_idx], y=top_features, palette="viridis")
    plt.title("LASSO Feature Selection: Magnitudes")
    plt.xlabel("Absolute Coefficient")
    plt.tight_layout()
    plt.savefig("04_LASSO_Features"+ext, bbox_inches='tight')
    plt.close()

# ==========================================
# 5. DISTRIBUTIONS OF ALL FEATURES
# ==========================================
print(f"--- 5. Generating Feature Distributions (for all {len(all_features)} regressors) ---")

for i, feature in enumerate(all_features):
    weight = feature_weights[feature]
    
    # Format the title weight label
    if weight > 0:
        weight_label = f"LASSO Weight: {weight:.4f}"
    else:
        weight_label = "LASSO Dropped (Weight: 0.0)"
        
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    # Histogram / Density
    sns.histplot(data=df, x=feature, hue='Class', palette=cp_classes, 
                 kde=True, ax=axes[0], alpha=0.4, stat="density", common_norm=False)
    axes[0].set_title(f"{feature}\n[{weight_label}]")
    
    # Box & Whisker
    sns.boxplot(data=df, x='Class', y=feature, hue='Class', palette=cp_classes, legend=False, ax=axes[1])
    sns.swarmplot(data=df, x='Class', y=feature, color='black', alpha=0.5, ax=axes[1])
    axes[1].set_title(f"Boxplot: {feature}")
    
    plt.tight_layout()
    # Pad file index with zeros so they sort correctly in the folder (e.g., 05_Feature_001...)
    safe_filename = feature.replace('/', '_').replace('\\', '_')
    plt.savefig(f"05_Feature_{i+1:03d}_{safe_filename}"+ext, bbox_inches='tight')
    plt.close()
    pass;

# ==========================================
# 6. CROSS-VALIDATED MODELING
# ==========================================
print("--- 6. Cross-Validating Models ---")
models = {
    "Logistic Regression": LogisticRegression(l1_ratio=0.0, random_state=42),
    "LDA": LinearDiscriminantAnalysis(),
    "SVM (RBF)": SVC(probability=True, random_state=42),
    "Random Forest": RandomForestClassifier(n_estimators=100, random_state=42)
}

cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
results_list = []
roc_data = {}

if len(selected_features) > 0:
    for name, model in models.items():
        y_pred = cross_val_predict(model, X_selected, y_encoded, cv=cv)
        y_prob = cross_val_predict(model, X_selected, y_encoded, cv=cv, method='predict_proba')[:, 1]
        
        cm = confusion_matrix(y_encoded, y_pred)
        tn, fp, fn, tp = cm.ravel()
        
        acc = accuracy_score(y_encoded, y_pred)
        sens = tp / (tp + fn) if (tp + fn) > 0 else 0 
        spec = tn / (tn + fp) if (tn + fp) > 0 else 0 
        auc = roc_auc_score(y_encoded, y_prob) 
        
        # Calculate Bootstrapped CI for AUROC
        ci_lower, ci_upper = bootstrap_auc_ci(y_encoded, y_prob)
        auc_string = f"{auc:.3f} [{ci_lower:.2f}-{ci_upper:.2f}]"
        
        results_list.append({
            "Model": name, 
            "Accuracy": acc, 
            "Sensitivity": sens, 
            "Specificity": spec, 
            "AUROC": auc,              # RAW NUMBER (For plots and .idxmax() to work)
            "AUROC_CI": auc_string     # STRING (For the printed table)
        })
        
        # Store ROC curve data
        fpr, tpr, _ = roc_curve(y_encoded, y_prob)
        roc_data[name] = (fpr, tpr, auc, cm)

    results_df = pd.DataFrame(results_list)
    
    # Print the clean table using the string CI column
    print("\nModel Performance Table (with 95% CIs):")
    print_cols = ['Model', 'Accuracy', 'Sensitivity', 'Specificity', 'AUROC_CI']
    print(results_df[print_cols].to_string(index=False))
    
    
    # ==========================================
    # 7. MODEL PERFORMANCE PLOTS
    # ==========================================
    print("--- 7. Generating Model Plots ---")
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))

    # ROC Curves
    for name, (fpr, tpr, auc, _) in roc_data.items():
        axes[0].plot(fpr, tpr, label=f"{name} (AUC = {auc:.2f})")
    axes[0].plot([0, 1], [0, 1], 'k--')
    axes[0].set_title("ROC Curves")
    axes[0].set_xlabel("False Positive Rate")
    axes[0].set_ylabel("True Positive Rate")
    axes[0].legend(loc="lower right")

    # Best Confusion Matrix
    best_model = results_df.loc[results_df['AUROC'].idxmax(), 'Model']
    sns.heatmap(roc_data[best_model][3], annot=True, fmt='d', cmap='Blues', ax=axes[1], 
                xticklabels=le.classes_, yticklabels=le.classes_)
    axes[1].set_title(f"Confusion Matrix: {best_model} (Best AUROC)")
    axes[1].set_ylabel("Actual")
    axes[1].set_xlabel("Predicted")

    plt.tight_layout()
    plt.savefig("06_ROC_and_ConfusionMatrix"+ext, bbox_inches='tight')
    plt.close()

    # Bar Chart
    df_melted = results_df.melt(id_vars="Model", value_vars=["Accuracy", "Sensitivity", "Specificity", "AUROC"], var_name="Metric", value_name="Score")
    plt.figure(figsize=(12, 6))
    ax = sns.barplot(data=df_melted, x='Model', y='Score', hue='Metric', palette=cp_models)
    plt.title("Model Performance Comparison")
    plt.ylim(0, 1.1)
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    for container in ax.containers:
        ax.bar_label(container, fmt='%.2f', padding=3, size=9)
    plt.tight_layout()
    plt.savefig("07_Model_Metrics_BarChart"+ext, bbox_inches='tight')
    plt.close()

    # ==========================================
    # 8. STATISTICAL INFERENCE (EFFECT SIZES)
    # ==========================================
    print("--- 8. Calculating Effect Sizes (Logit) ---")
    inf_features = list(top_features[:10]) 

    X_inf = X_scaled[inf_features]
    X_inf = sm.add_constant(X_inf) 

    try:
        
        logit = sm.Logit(y_encoded, X_inf).fit(disp=0) 
        
        or_df = pd.DataFrame({
            'Feature': inf_features,
            'Odds Ratio': np.exp(logit.params[1:]),
            'Lower CI': np.exp(logit.conf_int()[1:][0]),
            'Upper CI': np.exp(logit.conf_int()[1:][1]),
            'P-Value': logit.pvalues[1:]
        }).reset_index(drop=True)

        # Inside your existing Section 8 try block:
        # Plotting the Forest Plot (Updated for Log Scale)
        plt.figure(figsize=(10, len(inf_features) * 0.6 + 2))
        
        plt.errorbar(x=or_df['Odds Ratio'], y=or_df['Feature'], 
                     xerr=[or_df['Odds Ratio'] - or_df['Lower CI'], or_df['Upper CI'] - or_df['Odds Ratio']], 
                     fmt='o', color='black', capsize=5, capthick=2)
        
        plt.axvline(x=1, color='red', linestyle='--')
        
        # CRITICAL FIX: Set x-axis to log scale
        plt.xscale('log')
        # Limit the view so exploding CIs just run off the page without squishing everything
        plt.xlim(0.1, 10) 
        
        # Adjust annotations for log scale positioning
        plt.text(0.9, plt.ylim()[1], '← Associated with Control', horizontalalignment='right', color='blue', fontsize=11, style='italic')
        plt.text(1.1, plt.ylim()[1], 'Associated with Patient →', horizontalalignment='left', color='red', fontsize=11, style='italic')
        
        plt.title("Effect Sizes (Odds Ratios) of Top Regressors\n(Log Scale, limits truncated at 0.1 and 10)")
        plt.xlabel("Odds Ratio (Log Scale)")
        plt.grid(axis='x', alpha=0.3)
        
        for j, pval in enumerate(or_df['P-Value']):
            if pval < 0.05:
                # Place the asterisk safely inside the visible plot limit
                plot_limit = min(or_df['Upper CI'].iloc[j] * 1.1, 9.5)
                plt.text(plot_limit, j, '*', color='red', fontsize=14, va='center')
                pass;
            pass;

        plt.tight_layout()
        plt.savefig("08B_Effect_Sizes_ForestPlot_LogScaled"+ext, bbox_inches='tight')
        plt.close()
        pass;
                
    except Exception as e:
        print(f"Statsmodels Logit failed: {e}")
        
        
        # ==========================================
# NEW: UNIVARIATE COHEN'S D (ALL FEATURES)
# ==========================================
print("--- Calculating Cohen's d for all features ---")
cohens_d_results = {}

for feature in all_features:
    # Get raw values for C (0) and P (1)
    c_values = df_X[y_encoded == 0][feature].values
    p_values = df_X[y_encoded == 1][feature].values
    
    # Calculate effect size (Patient - Control)
    # Positive d means Patient mean is higher. Negative means Control mean is higher.
    d_val = cohens_d(p_values, c_values)
    cohens_d_results[feature] = d_val

# Sort by absolute effect size
d_df = pd.DataFrame(list(cohens_d_results.items()), columns=['Feature', 'Cohens_d'])
d_df['Abs_d'] = d_df['Cohens_d'].abs()
d_df = d_df.sort_values(by='Abs_d', ascending=False)

plt.figure(figsize=(10, max(6, len(all_features) * 0.3)))
sns.barplot(data=d_df, x='Cohens_d', y='Feature', hue='Feature', palette='coolwarm', legend=False)
#sns.barplot(data=d_df, x='Cohens_d', y='Feature', palette='coolwarm')
plt.title("Univariate Effect Sizes (Cohen's d)\nPositive = Higher in Patients, Negative = Higher in Controls")
plt.xlabel("Cohen's d Effect Size")
plt.axvline(x=0, color='black', linewidth=1)
# Standard lines for small (0.2), med (0.5), large (0.8) effects
plt.axvline(x=0.5, color='gray', linestyle='--', alpha=0.5)
plt.axvline(x=-0.5, color='gray', linestyle='--', alpha=0.5)
plt.axvline(x=0.8, color='red', linestyle='--', alpha=0.5)
plt.axvline(x=-0.8, color='blue', linestyle='--', alpha=0.5)
plt.tight_layout()
plt.savefig("08A_Cohens_d_All_Features"+ext, bbox_inches='tight')
plt.close()
        
print("\nPipeline Complete! All PDFs saved successfully.")
