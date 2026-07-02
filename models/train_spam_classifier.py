import os
import sys
import joblib
from datasets import load_dataset
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, precision_score, recall_score
import pandas as pd

def train_classifier():
    print("Loading SetFit/enron_spam dataset from Hugging Face...")
    # Load dataset
    try:
        dataset = load_dataset("SetFit/enron_spam")
    except Exception as e:
        print(f"Error loading dataset from HF: {e}")
        sys.exit(1)
    
    # Convert to pandas DataFrames
    train_df = pd.DataFrame(dataset['train'])
    test_df = pd.DataFrame(dataset['test'])
    
    print(f"Loaded {len(train_df)} training samples and {len(test_df)} test samples.")
    
    # Identify message and label columns
    text_col = 'text' if 'text' in train_df.columns else 'message'
    label_col = 'label'
    
    X_train = train_df[text_col].fillna("")
    y_train = train_df[label_col]
    
    X_test = test_df[text_col].fillna("")
    y_test = test_df[label_col]
    
    print("Vectorizing text using TfidfVectorizer...")
    # Max features capped for speed and memory efficiency
    vectorizer = TfidfVectorizer(stop_words='english', max_features=10000, ngram_range=(1, 2))
    X_train_vec = vectorizer.fit_transform(X_train)
    X_test_vec = vectorizer.transform(X_test)
    
    print("Training LogisticRegression classifier...")
    # Using class_weight='balanced' to handle class distribution, but we want high precision on Spam (class 1)
    # class_weight={0: 1.5, 1: 1.0} helps increase precision on spam (makes it harder to predict spam, reducing false positives)
    model = LogisticRegression(C=1.0, class_weight={0: 1.5, 1: 1.0}, max_iter=1000)
    model.fit(X_train_vec, y_train)
    
    y_pred = model.predict(X_test_vec)
    
    print("\nEvaluation Results:")
    print(classification_report(y_test, y_pred, target_names=['Ham', 'Spam']))
    
    spam_precision = precision_score(y_test, y_pred, pos_label=1)
    spam_recall = recall_score(y_test, y_pred, pos_label=1)
    print(f"Spam Precision (Avoid labeling Ham as Spam): {spam_precision:.4f}")
    print(f"Spam Recall: {spam_recall:.4f}")
    
    # Ensure models directory exists
    models_dir = os.path.dirname(os.path.abspath(__file__))
    os.makedirs(models_dir, exist_ok=True)
    
    # Save model and vectorizer
    model_path = os.path.join(models_dir, "spam_classifier.pkl")
    joblib.dump({"model": model, "vectorizer": vectorizer}, model_path)
    print(f"\nTrained model and vectorizer saved to {model_path}")

if __name__ == "__main__":
    train_classifier()
