import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
import string
import re

nltk.download('punkt')
stop_words = set(stopwords.words('english'))
stemmer = PorterStemmer()

def preprocess(text):
    preprocessed_text = " ".join([stemmer.stem(word) for word in word_tokenize(text) if word and (word not in stop_words) and (word not in string.punctuation) and (not any(c.isdigit() for c in word))])
    return re.sub(r'[^\w\s]', '', string=preprocessed_text).lower()