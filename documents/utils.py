import openai
import numpy as np
import os
from .models import Document  

# Set your API key from the environment variable (ensure you set it in your shell)
# openai.api_key = "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"

def get_embedding(text, model="text-embedding-ada-002"):
    """
    Sends the text to OpenAI's API and returns the embedding as a list.
    """
    response = openai.Embedding.create(input=[text], model=model)
    embedding = response["data"][0]["embedding"]
    return embedding

def cosine_similarity(vec1, vec2):
    """
    Compute cosine similarity between two vectors.
    """
    vec1 = np.array(vec1)
    vec2 = np.array(vec2)
    return np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2))

def check_for_matches(new_document, threshold=0.75):
    """
    Compare the new document's embedding against all other documents.
    Returns a list of tuples: (document, similarity_score) for those
    with similarity above the given threshold.
    """
    new_embedding = new_document.embedding  # this is stored as JSON (a list)
    matches = []
    all_docs = Document.objects.exclude(id=new_document.id)
    for doc in all_docs:
        # Calculate cosine similarity between embeddings
        sim = cosine_similarity(new_embedding, doc.embedding)
        if sim > threshold:
            matches.append((doc, sim))
    # Sort by highest similarity first
    matches.sort(key=lambda x: x[1], reverse=True)
    return matches
