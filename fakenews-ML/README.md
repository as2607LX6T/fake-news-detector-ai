# 📰 Fake News Detection System

A production-quality machine learning pipeline that classifies news articles as **Fake** or **Real** using NLP + scikit-learn.

---

## Project Structure

```
fake_news_detector/
│
├── data/                        ← Place Fake.csv and True.csv here
│   ├── Fake.csv
│   └── True.csv
│
├── src/                         ← All Python source modules
│   ├── __init__.py
│   ├── preprocess.py            ← NLP cleaning pipeline
│   ├── train.py                 ← Full training pipeline + inference helper
│   ├── evaluate.py              ← Metrics, confusion matrix, comparison table
│   └── predict.py               ← Reusable predictor class (for APIs/apps)
│
├── models/                      ← Saved artefacts (auto-created after training)
│   ├── best_model.pkl
│   ├── tfidf_vectorizer.pkl
│   └── training_metadata.pkl
│
├── reports/                     ← Evaluation reports + plots (auto-created)
│   ├── logistic_regression_confusion_matrix.png
│   ├── passive_aggressive_classifier_confusion_matrix.png
│   ├── multinomial_naive_bayes_confusion_matrix.png
│   ├── model_comparison.png
│   └── *_report.txt
│
├── notebooks/
│   └── fake_news_detection.ipynb  ← Interactive walkthrough
│
├── tests/
│   └── test_pipeline.py           ← Unit tests
│
├── requirements.txt
└── README.md
```

---

## Quick Start

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Place datasets
```
data/Fake.csv
data/True.csv
```
Download from: https://www.kaggle.com/datasets/clmentbisaillon/fake-and-real-news-dataset

### 3. Train
```bash
python src/train.py
```

### 4. Predict
```python
from src.predict import FakeNewsPredictor

predictor = FakeNewsPredictor()
result = predictor.predict("Scientists confirm moon is made of cheese.")
print(result)
# {'label': 0, 'verdict': 'FAKE', 'confidence': 0.97, 'cleaned_text': '...'}
```

### 5. Jupyter Notebook
```bash
jupyter notebook notebooks/fake_news_detection.ipynb
```

---

## ML Pipeline Overview

```
Raw CSV Data
     │
     ▼
Load & Label          (Fake=0, Real=1)
     │
     ▼
Merge & Shuffle       (combined dataset, random_state=42)
     │
     ▼
NLP Preprocessing     (lowercase → strip URLs → remove punct → stopwords → stem)
     │
     ▼
Train/Test Split      (80/20, stratified)
     │
     ▼
TF-IDF Vectorisation  (50k features, bigrams, sublinear_tf)
     │
     ▼
Train 3 Models        (Logistic Regression, Passive Aggressive, Naive Bayes)
     │
     ▼
Evaluate All          (accuracy, precision, recall, F1, confusion matrix)
     │
     ▼
Save Best Model       (best_model.pkl + tfidf_vectorizer.pkl)
```

---

## Why These Algorithms?

| Algorithm | Why It Works for Fake News |
|-----------|---------------------------|
| **Logistic Regression** | Strong linear baseline; works great with high-dimensional TF-IDF; outputs calibrated probabilities |
| **Passive Aggressive** | Online learning; efficient with sparse matrices; designed for large-scale text |
| **Naive Bayes** | Probabilistic; fast; excellent at exploiting word-frequency patterns |

---

## TF-IDF Explained Simply

> "Give high scores to words that are **frequent in this article** but **rare across all articles**."

- `TF` = How often does "conspiracy" appear in this article? (high → informative for this article)
- `IDF` = How rare is "conspiracy" across the whole dataset? (rare = more informative overall)
- `TF × IDF` = The word's discriminative power

Words like "the", "is", "a" get low scores (common everywhere).
Words like "hoax", "coverup", "breaking" get high scores in certain articles.

---

## Accuracy Tips & Future Upgrades

### Quick Wins (same stack)
- `GridSearchCV` for hyperparameter tuning → +1–3%
- Add `SVM` with linear kernel → often beats LR on text
- Ensemble voting classifier → +1–3%
- Include article `subject` and `date` as features

### BERT / Deep Learning Upgrade
```python
from transformers import pipeline

classifier = pipeline(
    "text-classification",
    model="jy46604790/Fake-News-Bert-Detect"
)
result = classifier("Moon landing was staged in a Hollywood studio.")
```

BERT understands **context**, not just word frequencies — it's pre-trained on billions of words and typically achieves 98–99% accuracy on this dataset.

---

## Dataset Source

Kaggle: [Fake and Real News Dataset](https://www.kaggle.com/datasets/clmentbisaillon/fake-and-real-news-dataset)

- **Fake.csv**: 23,481 articles (political fake news, 2015–2018)
- **True.csv**: 21,417 articles (Reuters real news, same period)
