import pandas as pd
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
import string
import re


# read data from json file
def read_json(file_path, limit = 10000):
    # only read part of the data due to memory limit 
    return pd.read_json(file_path, lines = True, nrows = limit)

# preprocess abstracts of papers
def preprocess_abstracts(data):
    # remove missing values
    data = data.dropna(subset=['abstract'])
    # remove duplicates
    data = data.drop_duplicates(subset=['abstract'])
    # tokenize abstracts, stemming, and remove stop words
    stop_words = set(stopwords.words('english'))
    stemmer = PorterStemmer()
    print('preprocessing abstracts...')
    data['abstract'] = data['abstract'].apply(lambda x: word_tokenize(x))
    data['abstract'] = data['abstract'].apply(lambda x: [stemmer.stem(word) for word in x])
    data['abstract'] = data['abstract'].apply(lambda x: [word for word in x if word not in stop_words])
    # remove punctuation
    data['abstract'] = data['abstract'].apply(lambda x: [word for word in x if word not in string.punctuation])
    # remove numbers
    data['abstract'] = data['abstract'].apply(lambda x: [word for word in x if not any(c.isdigit() for c in word)])
    # remove empty strings
    data['abstract'] = data['abstract'].apply(lambda x: [word for word in x if word])
    # join words back together
    data['abstract'] = data['abstract'].apply(lambda x: ' '.join(x))
    # remove special characters
    data['abstract'] = data['abstract'].apply(lambda x: re.sub(r'[^\w\s]', '', x))
    # convert to lower case
    data['abstract'] = data['abstract'].apply(lambda x: x.lower())
    return data