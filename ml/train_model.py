import pandas as pd
import re
import pickle
import os

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

# Load dataset
df = pd.read_csv('data/train.txt', sep=';', names=['text', 'emotion'])

def clean_text(text):
    text = text.lower()
    text = text.replace("not happy", "sad")
    text = text.replace("not good", "bad")
    text = text.replace("not okay", "bad")
    text = re.sub(r'[^a-zA-Z]', ' ', text)
    return text

df['cleaned'] = df['text'].apply(clean_text)

vectorizer = TfidfVectorizer(
    ngram_range=(1,3),
    max_features=15000,
    stop_words='english'
)

X = vectorizer.fit_transform(df['cleaned'])
y = df['emotion']

model = LogisticRegression(max_iter=300)
model.fit(X, y)

os.makedirs("models", exist_ok=True)

pickle.dump(model, open('models/model.pkl', 'wb'))
pickle.dump(vectorizer, open('models/vectorizer.pkl', 'wb'))

print("✅ Model trained successfully!")