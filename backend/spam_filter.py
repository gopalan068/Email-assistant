import os
import joblib

class SpamFilter:
    def __init__(self, model_path=None):
        if model_path is None:
            # Default location
            backend_dir = os.path.dirname(os.path.abspath(__file__))
            model_path = os.path.join(backend_dir, "..", "models", "spam_classifier.pkl")
            
        self.model_path = os.path.abspath(model_path)
        self.model = None
        self.vectorizer = None
        self.load_model()
        
    def load_model(self):
        if not os.path.exists(self.model_path):
            print(f"Warning: Spam classifier model file not found at {self.model_path}. Fallback to false (not spam).")
            return
        try:
            data = joblib.load(self.model_path)
            self.model = data["model"]
            self.vectorizer = data["vectorizer"]
            print(f"Loaded spam classifier model from {self.model_path}")
        except Exception as e:
            print(f"Error loading spam classifier: {e}")
            
    def is_spam(self, subject: str, sender: str, body: str) -> bool:
        if self.model is None or self.vectorizer is None:
            return False
            
        # Prepare text input in the same format as the training text
        # Subject + body
        text = f"Subject: {subject}\n\n{body}"
        try:
            vec = self.vectorizer.transform([text])
            prediction = self.model.predict(vec)[0]
            return bool(prediction == 1)
        except Exception as e:
            print(f"Error predicting spam: {e}")
            return False
