import nltk as n
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer, WordNetLemmatizer

n.download('punkt')
n.download('stopwords')
n.download('wordnet')

text_input = input("Enter a sentence: ")

tokens = word_tokenize(text_input)
print("Tokens:", tokens)

stop_words = set(stopwords.words('english'))
filtered = [w for w in tokens if w.lower() not in stop_words]
print("Stopwords Removed:", filtered)

stemmer = PorterStemmer()
stemmed = [stemmer.stem(w) for w in filtered]
print("Stemming Result:", stemmed)

lemmatizer = WordNetLemmatizer()
lemmatized = [lemmatizer.lemmatize(w) for w in filtered]
print("Lemmatization Result:", lemmatized)