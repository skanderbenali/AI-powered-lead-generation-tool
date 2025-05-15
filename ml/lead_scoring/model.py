import pandas as pd
import numpy as np
import joblib
import logging
from typing import Dict, Any, List, Optional, Tuple
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LeadScoringModel:
    """Lead scoring model using Random Forest classifier"""
    
    def __init__(
        self,
        model_path: Optional[str] = None,
        categorical_features: Optional[List[str]] = None,
        numerical_features: Optional[List[str]] = None
    ):
        """
        Initialize the lead scoring model.
        
        Args:
            model_path: Path to saved model file
            categorical_features: List of categorical feature names
            numerical_features: List of numerical feature names
        """
        self.model = None
        self.preprocessor = None
        self.model_path = model_path
        
        # Default features if not provided
        self.categorical_features = categorical_features or [
            'industry', 'title', 'company_size', 'location', 'source'
        ]
        self.numerical_features = numerical_features or [
            'company_employees', 'connections_count', 'profile_completeness',
            'email_valid', 'website_valid'
        ]
        
        # Feature importances for explaining scores
        self.feature_importances = {}
        
        # Load model if path provided
        if model_path:
            self.load_model(model_path)
    
    def preprocess_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Preprocess input data for model training or prediction.
        
        Args:
            data: Input data as DataFrame
        
        Returns:
            Preprocessed data
        """
        # Create preprocessor if not already created
        if self.preprocessor is None:
            # Create preprocessing pipeline
            categorical_transformer = Pipeline(steps=[
                ('onehot', OneHotEncoder(handle_unknown='ignore'))
            ])
            
            numerical_transformer = Pipeline(steps=[
                ('scaler', StandardScaler())
            ])
            
            self.preprocessor = ColumnTransformer(
                transformers=[
                    ('cat', categorical_transformer, self.categorical_features),
                    ('num', numerical_transformer, self.numerical_features)
                ]
            )
        
        # Apply preprocessing
        return self.preprocessor.fit_transform(data)
    
    def train(
        self,
        data: pd.DataFrame,
        target_column: str = 'converted',
        test_size: float = 0.2,
        random_state: int = 42
    ) -> Dict[str, float]:
        """
        Train the lead scoring model.
        
        Args:
            data: Training data
            target_column: Target column name
            test_size: Test set size
            random_state: Random state for reproducibility
        
        Returns:
            Dictionary of evaluation metrics
        """
        logger.info("Training lead scoring model")
        
        # Split features and target
        X = data.drop(columns=[target_column])
        y = data[target_column]
        
        # Split train and test sets
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=random_state
        )
        
        # Preprocess data
        X_train_processed = self.preprocess_data(X_train)
        
        # Train model
        self.model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            min_samples_split=5,
            min_samples_leaf=2,
            random_state=random_state
        )
        
        self.model.fit(X_train_processed, y_train)
        
        # Extract feature importances
        feature_names = (
            self.preprocessor.named_transformers_['cat'].named_steps['onehot'].get_feature_names_out(self.categorical_features).tolist() +
            self.numerical_features
        )
        
        self.feature_importances = dict(zip(feature_names, self.model.feature_importances_))
        
        # Evaluate model
        X_test_processed = self.preprocessor.transform(X_test)
        y_pred = self.model.predict(X_test_processed)
        
        metrics = {
            'accuracy': accuracy_score(y_test, y_pred),
            'precision': precision_score(y_test, y_pred, average='weighted'),
            'recall': recall_score(y_test, y_pred, average='weighted'),
            'f1_score': f1_score(y_test, y_pred, average='weighted')
        }
        
        logger.info(f"Model trained with metrics: {metrics}")
        
        return metrics
    
    def predict(self, data: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray, List[Dict[str, Any]]]:
        """
        Predict lead scores for input data.
        
        Args:
            data: Input data
        
        Returns:
            Tuple of (predicted scores, predicted probabilities, explanations)
        """
        if self.model is None:
            raise ValueError("Model not trained or loaded")
        
        # Preprocess data
        X_processed = self.preprocessor.transform(data)
        
        # Make predictions
        y_pred = self.model.predict(X_processed)
        y_proba = self.model.predict_proba(X_processed)[:, 1]  # Probability of positive class
        
        # Generate explanations
        explanations = self._generate_explanations(data, y_proba)
        
        return y_pred, y_proba, explanations
    
    def _generate_explanations(
        self, 
        data: pd.DataFrame, 
        scores: np.ndarray
    ) -> List[Dict[str, Any]]:
        """
        Generate explanations for predicted scores.
        
        Args:
            data: Input data
            scores: Predicted scores
        
        Returns:
            List of explanations
        """
        explanations = []
        
        for i, row in data.iterrows():
            explanation = {
                'score': float(scores[i]),
                'reasons': [],
                'factors': {}
            }
            
            # Add top factors
            for feature, value in row.items():
                if feature in self.categorical_features:
                    feature_key = f"{feature}_{value}"
                    if feature_key in self.feature_importances:
                        importance = self.feature_importances[feature_key]
                        explanation['factors'][feature] = {
                            'value': value,
                            'importance': float(importance)
                        }
                elif feature in self.numerical_features:
                    importance = self.feature_importances.get(feature, 0)
                    explanation['factors'][feature] = {
                        'value': float(value),
                        'importance': float(importance)
                    }
            
            # Sort factors by importance and keep top 5
            top_factors = sorted(
                explanation['factors'].items(),
                key=lambda x: x[1]['importance'],
                reverse=True
            )[:5]
            
            explanation['factors'] = dict(top_factors)
            
            # Generate text reasons
            score = scores[i]
            if score >= 0.8:
                explanation['reasons'].append("High-quality lead with strong fit for target criteria")
            elif score >= 0.6:
                explanation['reasons'].append("Good potential lead with moderate fit for target criteria")
            elif score >= 0.4:
                explanation['reasons'].append("Average lead quality with some matching attributes")
            else:
                explanation['reasons'].append("Low-quality lead with poor fit for target criteria")
            
            # Add specific reasons based on top factors
            for feature, info in top_factors[:3]:
                if info['importance'] > 0.05:
                    explanation['reasons'].append(f"{feature.replace('_', ' ').title()} ({info['value']}) is a significant factor")
            
            explanations.append(explanation)
        
        return explanations
    
    def save_model(self, path: str) -> None:
        """
        Save model to file.
        
        Args:
            path: Path to save model
        """
        if self.model is None:
            raise ValueError("Model not trained")
        
        # Save model, preprocessor, and feature importances
        joblib.dump({
            'model': self.model,
            'preprocessor': self.preprocessor,
            'categorical_features': self.categorical_features,
            'numerical_features': self.numerical_features,
            'feature_importances': self.feature_importances
        }, path)
        
        logger.info(f"Model saved to {path}")
    
    def load_model(self, path: str) -> None:
        """
        Load model from file.
        
        Args:
            path: Path to model file
        """
        try:
            data = joblib.load(path)
            
            self.model = data['model']
            self.preprocessor = data['preprocessor']
            self.categorical_features = data['categorical_features']
            self.numerical_features = data['numerical_features']
            self.feature_importances = data['feature_importances']
            
            logger.info(f"Model loaded from {path}")
            
        except Exception as e:
            logger.error(f"Error loading model: {str(e)}")
            raise


def generate_mock_training_data(n_samples: int = 1000) -> pd.DataFrame:
    """
    Generate mock training data for demonstration.
    
    Args:
        n_samples: Number of samples to generate
    
    Returns:
        DataFrame with mock data
    """
    np.random.seed(42)
    
    # Generate mock data
    industries = ['Technology', 'Finance', 'Healthcare', 'Manufacturing', 'Retail', 'Education']
    titles = ['CEO', 'CTO', 'VP Sales', 'VP Marketing', 'Director', 'Manager', 'Consultant']
    company_sizes = ['1-10', '11-50', '51-200', '201-500', '501-1000', '1001+']
    locations = ['San Francisco', 'New York', 'London', 'Berlin', 'Singapore', 'Remote']
    sources = ['linkedin', 'website', 'referral', 'conference']
    
    data = {
        'industry': np.random.choice(industries, n_samples),
        'title': np.random.choice(titles, n_samples),
        'company_size': np.random.choice(company_sizes, n_samples),
        'location': np.random.choice(locations, n_samples),
        'source': np.random.choice(sources, n_samples),
        'company_employees': np.random.randint(1, 10000, n_samples),
        'connections_count': np.random.randint(0, 2000, n_samples),
        'profile_completeness': np.random.uniform(0, 1, n_samples),
        'email_valid': np.random.choice([0, 1], n_samples, p=[0.2, 0.8]),
        'website_valid': np.random.choice([0, 1], n_samples, p=[0.3, 0.7])
    }
    
    # Generate target variable based on features
    # Higher quality leads are more likely to have:
    # - Executive titles
    # - Larger companies
    # - More connections
    # - Complete profiles
    # - Valid contact info
    
    df = pd.DataFrame(data)
    
    # Calculate conversion probability based on features
    title_scores = {
        'CEO': 0.8,
        'CTO': 0.7,
        'VP Sales': 0.75,
        'VP Marketing': 0.7,
        'Director': 0.6,
        'Manager': 0.4,
        'Consultant': 0.3
    }
    
    size_scores = {
        '1-10': 0.3,
        '11-50': 0.4,
        '51-200': 0.5,
        '201-500': 0.6,
        '501-1000': 0.7,
        '1001+': 0.8
    }
    
    # Calculate probability of conversion
    prob = (
        df['title'].map(title_scores) * 0.3 +
        df['company_size'].map(size_scores) * 0.2 +
        (df['connections_count'] / 2000) * 0.15 +
        df['profile_completeness'] * 0.15 +
        df['email_valid'] * 0.1 +
        df['website_valid'] * 0.1
    )
    
    # Generate converted label
    df['converted'] = np.random.binomial(1, prob)
    
    return df


if __name__ == "__main__":
    # Generate mock data
    data = generate_mock_training_data(1000)
    
    # Train model
    model = LeadScoringModel()
    metrics = model.train(data)
    
    print(f"Model trained with metrics: {metrics}")
    
    # Save model
    model.save_model("lead_scoring_model.joblib")
    
    # Test prediction
    test_data = generate_mock_training_data(10).drop(columns=['converted'])
    predictions, probabilities, explanations = model.predict(test_data)
    
    for i, (pred, prob, exp) in enumerate(zip(predictions, probabilities, explanations)):
        print(f"\nLead {i+1}:")
        print(f"Prediction: {'Converted' if pred == 1 else 'Not Converted'}")
        print(f"Probability: {prob:.2f}")
        print(f"Reasons: {', '.join(exp['reasons'])}")
        print("Top factors:")
        for feature, info in exp['factors'].items():
            print(f"  - {feature}: {info['value']} (importance: {info['importance']:.3f})")
