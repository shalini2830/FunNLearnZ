import re
from sklearn.feature_extraction.text import TfidfVectorizer

def extract_keywords_and_subheadings(text):
    """
    This function extracts keywords and attempts to recognize subheadings 
    by looking for specific patterns like '1.', '2.', '3.' or capitalized headings.
    """
    # Regular expression for extracting words of length >= 5
    words = re.findall(r'\b[A-Za-z]{5,}\b', text)
    processed_text = ' '.join(words)  # Convert to a single string
    
    # Use TF-IDF Vectorizer to rank words by importance
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform([processed_text])
    
    # Get feature names (words) and their scores
    feature_names = vectorizer.get_feature_names_out()
    scores = tfidf_matrix.toarray()[0]
    
    # Pair words with scores and sort by score
    word_score_pairs = sorted(zip(feature_names, scores), key=lambda x: x[1], reverse=True)
    
    # Extract top N keywords (adjust N as needed)
    top_keywords = [word for word, score in word_score_pairs if score > 0.1]
    
    # Extract subheadings - e.g., sections like "1. Introduction", "2. Methodology"
    subheadings = re.findall(r'\d+\.\s+[A-Za-z ]{5,}', text)  # Pattern to match subheadings
    subheadings = [subheading.strip() for subheading in subheadings]
    
    return top_keywords, subheadings
