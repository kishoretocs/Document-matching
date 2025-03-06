
from django.db import models
from django.contrib.auth.models import User

class Document(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='documents')
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to='documents/')
    text_content = models.TextField(blank=True, null=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    embedding = models.JSONField(null=True,blank=True)

    def __str__(self):
        return self.title


# #new 
# # models.py
# from django.db import models
# from django.contrib.auth.models import User
# import json

# class Document(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     content = models.TextField(null=True,blank=True)
#     word_freq = models.TextField(null=True,blank=True)  # Stores JSON-serialized word frequencies
#     uploaded_at = models.DateTimeField(auto_now_add=True)

#     def set_word_freq(self, freq_dict):
#         self.word_freq = json.dumps(freq_dict)

#     def get_word_freq(self):
#         return json.loads(self.word_freq)