"""
train_demo_model.py
───────────────────
Generates a small, working fake-news classifier and TF-IDF vectorizer
and saves them to  app/models/  so the API can start immediately
even before you have a real trained model.

Run once:
    python scripts/train_demo_model.py

The demo model is trained on ~50 hand-crafted samples.
It is NOT production-quality — replace with your own trained artefacts.
"""

import pickle
import random
from pathlib import Path

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.model_selection import train_test_split
from sklearn import metrics

# ── Training data (50 samples — 25 fake, 25 real) ────────────────────────────

FAKE_NEWS = [
    "SHOCKING: Scientists CONFIRM that vaccines contain microchips to track citizens!",
    "BREAKING: Government secretly adding fluoride to water to control minds of population",
    "EXPOSED: The moon landing was faked in a Hollywood studio, NASA finally admits",
    "You won't BELIEVE what they're hiding: Chemtrails are poisoning our children daily",
    "EXCLUSIVE: COVID-19 was created in a secret lab funded by billionaires for depopulation",
    "Wake up sheeple! 5G towers are actually mind control devices disguised as cell towers",
    "They don't want you to know: Eating bleach cures cancer, doctors suppress the truth",
    "LEAKED: Hillary Clinton runs a secret pizza restaurant child trafficking ring",
    "Mainstream media LIES: Climate change is a hoax invented by globalists for profit",
    "ALERT: George Soros is funding a secret army to overthrow the US government",
    "Scientists SHOCKED to find that the Earth is actually flat, cover-up revealed",
    "BOMBSHELL: Elvis Presley is alive and living in a secret government facility",
    "Share before removed: Big pharma is hiding a cure for all cancers worth billions",
    "REVEALED: Obama was actually born in Kenya, new documents prove citizenship fraud",
    "The deep state EXPOSED: CIA has been running drug cartels for decades, whistleblower says",
    "URGENT: Water fluoridation linked to autism, pediatricians bribed to hide evidence",
    "They're watching you: New smart TVs contain secret cameras recording your home 24/7",
    "PROOF: The Illuminati controls all world governments through secret banking cartels",
    "Doctor FIRED for revealing that common cold medicine causes immediate heart attacks",
    "BREAKING: Alien bodies found at Area 51, government worker leaks classified photos",
    "Massive cover-up: Thousands die from flu shots every year, CDC hides the data",
    "EXPOSED: George W Bush personally planned and executed the 9/11 attacks",
    "They don't want you healthy: Big pharma destroys natural cancer cure discoveries",
    "SHOCKING truth about sunscreen: It causes cancer and they've known for 30 years",
    "LEAKED memo shows WHO deliberately spread COVID-19 to reduce world population",
]

REAL_NEWS = [
    "Federal Reserve raises interest rates by 25 basis points in effort to control inflation",
    "NASA's James Webb Space Telescope captures new images of galaxy formation 13 billion years ago",
    "Senate passes bipartisan infrastructure bill allocating $1.2 trillion for roads and bridges",
    "World Health Organization reports progress in malaria vaccine trials across sub-Saharan Africa",
    "Apple reports quarterly earnings of $90 billion, beating analyst expectations by 8 percent",
    "Study published in Nature shows Mediterranean diet reduces cardiovascular disease risk by 30%",
    "European Central Bank announces quantitative easing program to stimulate sluggish economy",
    "Supreme Court rules 6-3 in favor of environmental protections for wetlands in landmark case",
    "Pfizer announces Phase 3 trial results showing 91% efficacy for updated COVID booster",
    "University of Oxford researchers develop new battery technology with 3x energy density",
    "Department of Labor reports unemployment rate falls to 3.7%, lowest in five years",
    "China and the United States agree to resume climate talks at upcoming G20 summit",
    "Tesla recalls 200,000 vehicles over software defect affecting rearview camera systems",
    "IMF revises global GDP growth forecast downward to 2.9% citing persistent inflation pressures",
    "Researchers at MIT develop new cancer immunotherapy showing 70% response rate in trials",
    "United Nations Climate Conference agrees to accelerate phase-out of coal power by 2040",
    "Amazon reports 15% year-over-year growth in cloud computing revenue for third quarter",
    "CDC recommends updated flu vaccine formulation for upcoming Northern Hemisphere season",
    "Federal judge blocks merger between two major airlines citing antitrust concerns",
    "SpaceX successfully launches 60 Starlink satellites into low Earth orbit from Cape Canaveral",
    "Global semiconductor shortage expected to ease as TSMC opens new fabrication plant in Arizona",
    "WHO declares end to mpox public health emergency as cases decline globally",
    "US Treasury issues new guidance on cryptocurrency reporting requirements for tax purposes",
    "NASA confirms Perseverance rover has collected 23 rock samples from Jezero Crater on Mars",
    "Bank of England holds interest rates steady as inflation approaches 2% target",
]

# ── Build dataset ─────────────────────────────────────────────────────────────

texts  = FAKE_NEWS + REAL_NEWS
labels = [0] * len(FAKE_NEWS) + [1] * len(REAL_NEWS)   # 0=Fake, 1=Real

# Shuffle
combined = list(zip(texts, labels))
random.seed(42)
random.shuffle(combined)
texts, labels = zip(*combined)

X_train, X_test, y_train, y_test = train_test_split(
    texts, labels, test_size=0.2, random_state=42, stratify=labels
)

# ── Train ─────────────────────────────────────────────────────────────────────

print("Training demo model…")

vectorizer = TfidfVectorizer(
    ngram_range=(1, 2),
    max_features=5000,
    sublinear_tf=True,
    strip_accents="unicode",
    analyzer="word",
    token_pattern=r"\b[a-zA-Z]{3,}\b",
)

model = LogisticRegression(
    C=1.0,
    max_iter=1000,
    random_state=42,
    solver="lbfgs",
)

X_train_vec = vectorizer.fit_transform(X_train)
X_test_vec  = vectorizer.transform(X_test)
model.fit(X_train_vec, y_train)

# ── Evaluate ──────────────────────────────────────────────────────────────────

y_pred = model.predict(X_test_vec)
acc    = metrics.accuracy_score(y_test, y_pred)
print(f"Demo model accuracy on test split: {acc * 100:.1f}%")
print(metrics.classification_report(y_test, y_pred, target_names=["Fake", "Real"]))

# ── Save ──────────────────────────────────────────────────────────────────────

out_dir = Path("app/models")
out_dir.mkdir(parents=True, exist_ok=True)

model_path = out_dir / "model.pkl"
vec_path   = out_dir / "vectorizer.pkl"

with model_path.open("wb") as f:
    pickle.dump(model, f)

with vec_path.open("wb") as f:
    pickle.dump(vectorizer, f)

print(f"\n✅  Saved model      → {model_path.resolve()}")
print(f"✅  Saved vectorizer → {vec_path.resolve()}")
print("\nYou can now start the server with:  python main.py")
print("Replace these demo files with your production model.pkl and vectorizer.pkl when ready.")
