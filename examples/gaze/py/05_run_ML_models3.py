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
