#!/usr/bin/env python3
"""
Chart classification training using Random Forest.

This script trains a Random Forest classifier on chart images for production use.
Perfect for small-medium datasets (290-10,000 samples).
"""

import logging
import numpy as np
import json
from pathlib import Path
from PIL import Image
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score
import joblib
from typing import Tuple, List

# Configuration constants
IMAGE_SIZE = (64, 64)  # Resize target for sklearn compatibility
CHART_TYPES = ['bar', 'line', 'pie', 'doughnut']
TYPE_MAPPING = {chart_type: i for i, chart_type in enumerate(CHART_TYPES)}
MODEL_FILENAME = "chart_classifier_rf.pkl"
RANDOM_STATE = 42

# Setup logging
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


def load_data_for_sklearn(dataset_path: str) -> Tuple[np.ndarray, np.ndarray]:
    """
    Load and preprocess chart images for sklearn Random Forest.

    Args:
        dataset_path: Path to dataset directory containing PNG and JSON files

    Returns:
        Tuple of (features, labels) as numpy arrays

    Raises:
        ValueError: If insufficient data found
    """
    images = []
    labels = []

    logging.info("Loading dataset from %s", dataset_path)
    dataset_dir = Path(dataset_path)

    if not dataset_dir.exists():
        raise ValueError(f"Dataset path does not exist: {dataset_path}")

    png_files = list(dataset_dir.glob("*.png"))
    if not png_files:
        raise ValueError(f"No PNG files found in {dataset_path}")

    for img_file in png_files:
        json_file = img_file.with_suffix('.json')
        if not json_file.exists():
            logging.warning(
                "Missing JSON file for %s, skipping", img_file.name)
            continue

        try:
            # Load and preprocess image
            img = Image.open(img_file).convert('RGB')
            img = img.resize(IMAGE_SIZE)
            img_array = np.array(img).flatten()

            # Load chart type from metadata
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            chart_type = data.get('metadata', {}).get('chartType')
            if not chart_type or chart_type not in TYPE_MAPPING:
                logging.warning("Invalid chart type '%s' in %s, skipping",
                                chart_type, json_file.name)
                continue

            # Normalize pixel values and add to dataset
            images.append(img_array / 255.0)
            labels.append(TYPE_MAPPING[chart_type])

        except Exception as e:
            logging.error("Error processing %s: %s", img_file.name, e)
            continue

    if len(images) < 10:
        raise ValueError(
            f"Insufficient data: only {len(images)} valid samples found")

    return np.array(images), np.array(labels)


def print_dataset_stats(features: np.ndarray, labels: np.ndarray) -> None:
    """Print dataset statistics."""
    logging.info("Dataset loaded successfully")
    logging.info("Samples: %d", len(features))
    logging.info("Feature shape: %s", features.shape)

    print("\nLabel distribution:")
    for i, chart_type in enumerate(CHART_TYPES):
        count = np.sum(labels == i)
        print(f"  {chart_type}: {count}")


def train_model(X_train: np.ndarray, y_train: np.ndarray) -> RandomForestClassifier:
    """Train Random Forest classifier."""
    logging.info("Training Random Forest classifier...")

    clf = RandomForestClassifier(
        n_estimators=100,
        random_state=RANDOM_STATE,
        n_jobs=-1,
        max_depth=None,
        min_samples_split=2,
        min_samples_leaf=1,
        bootstrap=True
    )

    clf.fit(X_train, y_train)
    logging.info("Training completed")
    return clf


def evaluate_model(model: RandomForestClassifier, X_test: np.ndarray,
                   y_test: np.ndarray) -> float:
    """Evaluate model and print metrics."""
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)

    logging.info("Test accuracy: %.3f", accuracy)

    print(f"\nTest Accuracy: {accuracy:.3f}")
    print("\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=CHART_TYPES))

    return accuracy


def save_model(model: RandomForestClassifier, filename: str = MODEL_FILENAME) -> None:
    """Save trained model to disk."""
    joblib.dump(model, filename)
    logging.info("Model saved as %s", filename)
    print(f"\nModel saved as {filename}")


def show_feature_importance(model: RandomForestClassifier, top_n: int = 10) -> None:
    """Display top feature importances (pixel positions)."""
    importances = model.feature_importances_
    top_features = np.argsort(importances)[-top_n:]

    print(f"\nTop {top_n} most important pixels: {top_features}")
    logging.info("Feature importance analysis completed")


def main() -> None:
    """Main training pipeline."""
    dataset_path = "../dataset-gather/dataset"

    try:
        # Load and preprocess data
        X, y = load_data_for_sklearn(dataset_path)
        print_dataset_stats(X, y)

        # Split data with stratification
        X_train, X_test, y_train, y_test = train_test_split(
            X, y,
            test_size=0.2,
            random_state=RANDOM_STATE,
            stratify=y
        )

        print(f"\nTrain: {len(X_train)}, Test: {len(X_test)}")

        # Train model
        model = train_model(X_train, y_train)

        # Evaluate performance
        accuracy = evaluate_model(model, X_test, y_test)

        # Save model for production use
        save_model(model)

        # Show feature importance
        show_feature_importance(model)

        if accuracy == 1.0:
            print("\n🎯 Perfect accuracy achieved! Model ready for production.")
        elif accuracy >= 0.9:
            print(
                f"\n✅ Excellent accuracy ({accuracy:.1%}). Model ready for production.")
        else:
            print(f"\n⚠️  Consider collecting more data or trying different features.")

    except Exception as e:
        logging.error("Training failed: %s", e)
        print(f"Training failed: {e}")
        return 1

    return 0


if __name__ == "__main__":
    exit(main())
