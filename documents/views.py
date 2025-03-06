from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Document
from difflib import SequenceMatcher
from django.shortcuts import render, redirect, get_object_or_404
from .utils import get_embedding,cosine_similarity,check_for_matches
import openai
import numpy as np
import os
import re
from collections import Counter
from datetime import date
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count
from django.db.models.functions import TruncDate
from django.contrib.auth.models import User




# @login_required
# def upload_document(request):
#     if request.method == "POST":
#         uploaded_file = request.FILES.get("document")
#         if not uploaded_file:
#             messages.error(request, "No file selected.")
#             return redirect("upload_document")
        
#         # Use the file name or an input title
#         profile = request.user.profile
#         title = request.POST.get("title", uploaded_file.name)
#         if profile.credits>0:
#             try:
#                 text_content = uploaded_file.read().decode("utf-8")
#             except Exception as e:
#                 messages.error(request, f"Error reading file: {e}")
#                 return redirect("upload_document")
            
#             # Generate the embedding from OpenAI's API
#             try:
#                 embedding = get_embedding(text_content)  # returns a list of floats
#             except Exception as e:
#                 messages.error(request, f"Error generating embedding: {e}")
#                 return redirect("upload_document")
            
#             # Create and save the Document instance with the embedding
#             document = Document.objects.create(
#                 user=request.user,
#                 title=title,
#                 file=uploaded_file,
#                 text_content=text_content,
#                 embedding=embedding
#             )
            
#         else:
#             messages.error(request, "Not enough credits to scan the document.")
#             return redirect("profile")
#         # Deduct 1 credit from the user's profile (ensure credit system integration)
        
#         profile.credits -= 1
#         profile.save()
#         messages.success(request, "Document uploaded and scanned successfully! 1 credit deducted.")
        
#         # Check for matching documents using the stored embedding
#         matches = check_for_matches(document, threshold=0.75)
#         print('----------------------',document)
#         if matches:
#             messages.info(request, f"Found {len(matches)} similar document(s).")
#             # Optionally, store matches data in the session or pass it to a view
#         else:
#             messages.info(request, "No similar documents found.")
        
#         return redirect("document_detail", doc_id=document.id)
    
#     return render(request, "documents/upload_document.html")

# @login_required
# def upload_document(request):
#     if request.method == "POST":
#         uploaded_file = request.FILES.get("document")
#         if not uploaded_file:
#             messages.error(request, "No file selected.")
#             return redirect("upload_document")
        
#         title = request.POST.get("title", uploaded_file.name)
        
#         # Read the file and try decoding as UTF-8, then fallback if needed.
#         try:
#             file_bytes = uploaded_file.read()
#             print('-------------------',file_bytes)
#             try:
#                 text_content = file_bytes.decode("utf-8")
#                 print('------------------',text_content)
#             except UnicodeDecodeError:
#                 # Fallback: decode with 'latin-1' and ignore errors (adjust as needed)
#                 text_content = file_bytes.decode("latin-1", errors="ignore")
#                 print('------------------',text_content)

#         except Exception as e:
#             messages.error(request, f"Error reading file: {e}")

#             return redirect("upload_document")
        
#         # Generate embedding using OpenAI's API
#         try:
#             embedding = get_embedding(text_content)  # This returns a list of floats
#             print('---------------',embedding)
#         except Exception as e:
#             messages.error(request, f"Error generating embedding: {e}")
#             print('----------------',e,'error')
#             return redirect("upload_document")
        
#         # Create and save the Document instance with the embedding
#         document = Document.objects.create(
#             user=request.user,
#             title=title,
#             file=uploaded_file,
#             text_content=text_content,
#             embedding=embedding
#         )
        
#         # Deduct 1 credit from the user's profile (ensure your credit system is integrated)
#         profile = request.user.profile
#         if profile.credits > 0:
#             profile.credits -= 1
#             profile.save()
#             messages.success(request, "Document uploaded and scanned successfully! 1 credit deducted.")
#         else:
#             messages.error(request, "Not enough credits to scan the document.")
#             document.delete()
#             return redirect("profile")
        
#         # Check for matching documents using the stored embedding
#         matches = check_for_matches(document, threshold=0.75)
#         if matches:
#             messages.info(request, f"Found {len(matches)} similar document(s).")
#             # Optionally, you can pass 'matches' to the document detail view via session or context.
#         else:
#             messages.info(request, "No similar documents found.")
        
#         return redirect("document_detail", doc_id=document.id)
    
#     return render(request, "documents/upload_document.html")

@login_required
def document_detail(request, doc_id):
    document = get_object_or_404(Document, id=doc_id)
    return render(request, "documents/document_detail.html", {"document": document})


# Assuming you add an optional embedding field to your model (e.g., a JSONField or TextField)
# For simplicity, let's assume we recalculate on the fly in this example

@login_required
def document_matches(request, doc_id):
    target_doc = get_object_or_404(Document, id=doc_id)
    target_text = target_doc.text_content
    try:
        target_embedding = get_embedding(target_text)
    except Exception as e:
        messages.error(request, f"Error generating embedding: {e}")
        return redirect("document_detail", doc_id=doc_id)
    
    all_documents = Document.objects.exclude(id=doc_id)
    matches = []
    
    for doc in all_documents:
        try:
            current_embedding = get_embedding(doc.text_content)
            similarity = cosine_similarity(target_embedding, current_embedding)
            # Set a threshold (e.g., 0.75 or any value that suits your data)
            if similarity > 0.75:
                matches.append((doc, similarity))
        except Exception as e:
            continue  # handle error (maybe log it) and skip document
    
    # Sort matches by similarity (highest first)
    matches.sort(key=lambda x: x[1], reverse=True)
    
    return render(request, "documents/document_matches.html", {"document": target_doc, "matches": matches})



import json
import string
import numpy as np
from collections import Counter
from django.shortcuts import render
from django.http import JsonResponse
from django.views import View
from django.core.files.storage import default_storage
from .models import Document
from nltk.corpus import stopwords

# Helper function to preprocess text
def preprocess_text(text):
    text = text.lower().translate(str.maketrans('', '', string.punctuation))
    words = text.split()
    return words


# Filter out common stopwords to capture more meaningful topics
def get_filtered_words(text):
    words = preprocess_text(text)
    stop_words = set(stopwords.words('english'))
    filtered_words = [word for word in words if word not in stop_words]
    return filtered_words

# Compute common topics (words) across a list of document texts
def common_topics(documents, top_n=10):
    counter = Counter()
    for text in documents:
        filtered = get_filtered_words(text)
        counter.update(filtered)
    return counter.most_common(top_n)


# Helper function to compute cosine similarity
def cosine_similarity(vec1, vec2):
    words = list(set(vec1.keys()).union(set(vec2.keys())))
    vec1_array = np.array([vec1.get(word, 0) for word in words])
    vec2_array = np.array([vec2.get(word, 0) for word in words])
    
    dot_product = np.dot(vec1_array, vec2_array)
    norm1 = np.linalg.norm(vec1_array)
    norm2 = np.linalg.norm(vec2_array)
    
    return dot_product / (norm1 * norm2) if norm1 and norm2 else 0.0
def check_for_matches(new_document, threshold=0.5):
    """
    Compare the new document's word frequency (stored in the embedding field)
    against all other documents. Returns a list of tuples: (document, similarity).
    """
    new_embedding = new_document.embedding  # This is a dict stored as JSON
    matches = []
    all_docs = Document.objects.exclude(id=new_document.id)
    for doc in all_docs:
        existing_embedding = doc.embedding
        similarity = cosine_similarity(new_embedding, existing_embedding)
        if similarity >= threshold:
            matches.append((doc, similarity))
    matches.sort(key=lambda x: x[1], reverse=True)
    return matches

#         return JsonResponse({'document_id': document.id, 'similar_documents': similarities})
import json
# from .utils import preprocess_text, cosine_similarity  # Ensure these functions exist

@login_required
def upload_document(request):
    if request.method == "POST":
        uploaded_file = request.FILES.get("document")
        if not uploaded_file:
            messages.error(request, "No file selected.")
            return redirect("upload_document")
        title = request.POST.get("title", uploaded_file.name)
        # Read the file content safely
        try:
            file_bytes = uploaded_file.read()
            try:
                text_content = file_bytes.decode("utf-8")
            except UnicodeDecodeError:
                text_content = file_bytes.decode("latin-1", errors="ignore")
        except Exception as e:
            messages.error(request, f"Error reading file: {e}")
            return redirect("upload_document")

        # Preprocess and compute word frequency
        words = preprocess_text(text_content)
        word_freq = dict(Counter(words))

        # Deduct credit before saving document
        profile = request.user.profile
        if profile.credits > 0:
            profile.credits -= 1
            profile.save()
        else:
            messages.error(request, "Not enough credits to scan the document.")
            return redirect("profile")

        # Save document in the database

        document = Document.objects.create(
            user=request.user,
            title=title,
            file=uploaded_file,
            text_content=text_content,
            embedding=word_freq  # Save the word frequency dict in the JSONField
        )
        # Compare with existing documents using cosine similarity
        # existing_docs = Document.objects.exclude(id=document.id)
        similar_docs = check_for_matches(document)
        # Provide feedback on document similarity
        if similar_docs:
            messages.info(request, f"Found {len(similar_docs)} similar document(s).")
        else:
            messages.info(request, "No similar documents found.")

        # return redirect("document_detail", doc_id=document.id)

        return render(request, "documents/document_matches.html", {"document": document, "matches": similar_docs})

    return render(request, "documents/upload_document.html")


@staff_member_required
def analytics_dashboard(request):
    scans_per_day = (
        Document.objects
        .annotate(scan_date=TruncDate('uploaded_at'))
        .values('scan_date','user__username')
        .annotate(num_scans=Count('id'))
        .order_by('scan_date','user__username')

    )
    common_words_counter = Counter()
    all_documents = Document.objects.all()
    for doc in all_documents:
        words = get_filtered_words(doc.text_content)
        common_words_counter.update(words)
    top_common_words = common_words_counter.most_common(10)
    users_data = (
        User.objects
        .annotate(total_scans=Count('documents'))
        .order_by('-total_scans')
    )

    credit_usage_stats = []
    for user in users_data:
        # Assuming every user has an associated profile (created on signup)
        profile = user.profile
        used_credits = 20 - profile.credits  # Adjust if your reset logic is different
        credit_usage_stats.append({
            'username': user.username,
            'total_scans': user.total_scans,
            'credits_used': used_credits,
            'credits_remaining': profile.credits,
        })
    context = {
        'scans_per_day': scans_per_day,
        'top_common_words': top_common_words,
        'credit_usage_stats': credit_usage_stats,
    }
    return render(request, 'documents/dashboard.html', context)