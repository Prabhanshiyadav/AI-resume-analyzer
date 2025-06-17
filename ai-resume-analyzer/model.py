from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer

tfidf_vectorizer = TfidfVectorizer()
bert_model = SentenceTransformer('all-MiniLM-L6-v2')

def calculate_tfidf_similarity(resume_text, jd_text):
    vectors = tfidf_vectorizer.fit_transform([resume_text, jd_text])
    return cosine_similarity(vectors[0], vectors[1])[0][0]

def calculate_bert_similarity(resume_text, jd_text):
    embeddings = bert_model.encode([resume_text, jd_text])
    return cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
