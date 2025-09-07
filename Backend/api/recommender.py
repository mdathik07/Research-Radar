# import numpy as np
# import joblib
# from sklearn.feature_extraction.text import TfidfVectorizer
# from sklearn.metrics.pairwise import cosine_similarity
# from pathlib import Path
# from .models import Papers
# import yake

# class DocumentSearch:
#     def __init__(self, vectors_path='doc_vectors.joblib'):
#         self.vectors_path = Path(vectors_path)
#         self.vectorizer = None
#         self.doc_vectors = None
#         self.paper_ids = None
#         self.load_or_create_vectors()
    
#     def preprocess(self, text):
#         return str(text).lower()
    
#     def load_or_create_vectors(self):
#         if self.vectors_path.exists():
#             saved_data = joblib.load(self.vectors_path)
#             self.vectorizer = saved_data['vectorizer']
#             self.doc_vectors = saved_data['vectors']
#             self.paper_ids = saved_data['paper_ids']
#         else:
#             self.compute_and_save_vectors()
    
#     def compute_and_save_vectors(self):
#         # Get all papers from database
#         papers = Papers.objects.all().values('id', 'title', 'abstract', 'authors')
        
#         if not papers:
#             raise ValueError("No papers found in database")
        
#         combined_docs = []
#         paper_ids = []
        
#         for paper in papers:
#             # Include title, abstract, and authors in the vector
#             combined_text = f"{paper['title']} {paper['abstract']} {paper['authors']}"
#             combined_docs.append(combined_text)
#             paper_ids.append(paper['id'])
        
#         self.vectorizer = TfidfVectorizer(preprocessor=self.preprocess)
#         self.doc_vectors = self.vectorizer.fit_transform(combined_docs)
#         self.paper_ids = paper_ids
        
#         joblib.dump({
#             'vectorizer': self.vectorizer,
#             'vectors': self.doc_vectors,
#             'paper_ids': self.paper_ids
#         }, self.vectors_path)
    
#     def search(self, query_terms, author=None, min_results=25, threshold=0.3):
#         """
#         Search for papers based on query terms and optionally filter by author.
        
#         Args:
#             query_terms (str): Search query
#             author (str, optional): Author name to filter results
#             min_results (int): Minimum number of results
#             threshold (float): Minimum similarity score (0-1)
            
#         Returns:
#             QuerySet: Matching Papers objects
#         """
#         query_vector = self.vectorizer.transform([self.preprocess(query_terms)])
#         similarities = cosine_similarity(self.doc_vectors, query_vector).flatten()
        
#         high_similarity_indices = np.where(similarities >= threshold)[0]
#         high_similarity_papers = [(i, similarities[i]) for i in high_similarity_indices]
#         high_similarity_papers.sort(key=lambda x: -x[1])
        
#         if len(high_similarity_papers) < min_results:
#             sorted_indices = np.argsort(-similarities)
#             additional_indices = [
#                 i for i in sorted_indices 
#                 if i not in high_similarity_indices
#             ]
            
#             additional_papers = [
#                 (i, similarities[i]) 
#                 for i in additional_indices[:min_results - len(high_similarity_papers)]
#             ]
#             high_similarity_papers.extend(additional_papers)
        
#         selected_paper_ids = [self.paper_ids[i[0]] for i in high_similarity_papers]
        
#         # Get base queryset
#         results = Papers.objects.filter(id__in=selected_paper_ids)
        
#         # Filter by author if provided
#         if author:
#             results = results.filter(authors__icontains=author)
        
#         return results

#     def refresh_vectors(self):
#         """
#         Force refresh of document vectors
#         """
#         self.compute_and_save_vectors()

# class InterestAmplifier:
#     def __init__(self, text, user):
#         self.text = text
#         self.user = user
#         kw_extractor = yake.KeywordExtractor()
#         self.keywords = [kw for kw, _ in kw_extractor.extract_keywords(text)]

#     def update_interests(self, new_keywords):
#         interests = self.user.interests.split()  
#         interests.extend(new_keywords)
#         interests = interests[-5:]  
#         self.user.interests = ' '.join(interests)  
#         self.user.save() 

#     def from_search(self):
#         if self.text == self.user.interests:
#             return
#         self.update_interests(self.keywords)
    
#     def from_pdf(self):
#         self.update_interests(self.keywords[:3] if len(self.keywords) > 3 else self.keywords)

#     def from_paper(self):
#         self.update_interests(self.keywords[:3] if len(self.keywords) > 3 else self.keywords)



# Backend/api/recommender.py
import os
from pathlib import Path

import joblib
import numpy as np
import yake
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from django.conf import settings
from django.db.models import Case, When

from .models import Papers


class DocumentSearch:
    def __init__(self, vectors_path: str | Path = None):
        # default to project base dir so file is persisted with the project
        default_path = Path(settings.BASE_DIR) / "doc_vectors.joblib"
        self.vectors_path = Path(vectors_path) if vectors_path else default_path
        self.vectorizer = None
        self.doc_vectors = None
        self.paper_ids = []
        self.load_or_create_vectors()

    def preprocess(self, text: str) -> str:
        return str(text or "").lower()

    def load_or_create_vectors(self):
        try:
            if self.vectors_path.exists():
                saved_data = joblib.load(self.vectors_path)
                self.vectorizer = saved_data.get("vectorizer")
                self.doc_vectors = saved_data.get("vectors")
                self.paper_ids = saved_data.get("paper_ids", [])
                # If any part missing, recompute
                if self.vectorizer is None or self.doc_vectors is None or not self.paper_ids:
                    self.compute_and_save_vectors()
            else:
                self.compute_and_save_vectors()
        except Exception:
            # If joblib file is corrupt or incompatible, recompute from DB
            self.compute_and_save_vectors()

    def compute_and_save_vectors(self):
        papers = list(Papers.objects.all().values("id", "title", "abstract", "authors"))
        if not papers:
            raise ValueError("No papers found in database. Add some Papers before building vectors.")

        combined_docs = []
        paper_ids = []
        for paper in papers:
            title = paper.get("title") or ""
            abstract = paper.get("abstract") or ""
            authors = paper.get("authors") or ""
            combined_text = f"{title} {abstract} {authors}"
            combined_docs.append(combined_text)
            paper_ids.append(paper["id"])

        self.vectorizer = TfidfVectorizer(preprocessor=self.preprocess)
        self.doc_vectors = self.vectorizer.fit_transform(combined_docs)
        self.paper_ids = paper_ids

        # Ensure parent dir exists (safe for OneDrive or other paths)
        try:
            self.vectors_path.parent.mkdir(parents=True, exist_ok=True)
            joblib.dump(
                {"vectorizer": self.vectorizer, "vectors": self.doc_vectors, "paper_ids": self.paper_ids},
                self.vectors_path,
            )
        except Exception:
            # If saving fails (permissions/OneDrive lock), continue without saving
            pass

    def search(self, query_terms: str, author: str | None = None, min_results: int = 25, threshold: float = 0.3):
        """
        Return an ordered list of Paper model instances matching the query.
        """
        if self.vectorizer is None or self.doc_vectors is None:
            # try to build vectors if not present
            self.compute_and_save_vectors()

        query_vector = self.vectorizer.transform([self.preprocess(query_terms)])
        similarities = cosine_similarity(self.doc_vectors, query_vector).flatten()

        # indices with similarity >= threshold
        high_idx = np.where(similarities >= threshold)[0]
        high_list = [(i, similarities[i]) for i in high_idx]
        high_list.sort(key=lambda x: -x[1])

        if len(high_list) < min_results:
            sorted_idx = np.argsort(-similarities)
            additional = [i for i in sorted_idx if i not in high_idx]
            needed = min_results - len(high_list)
            additional_papers = [(i, similarities[i]) for i in additional[:needed]]
            high_list.extend(additional_papers)

        # map to paper ids preserving ranking order
        selected_paper_ids = []
        seen = set()
        for idx, score in high_list:
            pid = self.paper_ids[idx]
            if pid not in seen:
                selected_paper_ids.append(pid)
                seen.add(pid)

        if not selected_paper_ids:
            return []

        # preserve ordering using Case/When
        ordering = Case(*[When(pk=pid, then=pos) for pos, pid in enumerate(selected_paper_ids)])
        qs = Papers.objects.filter(pk__in=selected_paper_ids).annotate(_order=ordering).order_by("_order")

        # filter by author if requested (note: will alter ordering only if fewer results remain)
        if author:
            qs = qs.filter(authors__icontains=author)

        return list(qs)

    def refresh_vectors(self):
        """Force refresh of document vectors (rebuild from DB)."""
        self.compute_and_save_vectors()


class InterestAmplifier:
    def __init__(self, text: str, user):
        self.text = text or ""
        self.user = user
        kw_extractor = yake.KeywordExtractor()
        self.keywords = [kw for kw, _ in kw_extractor.extract_keywords(self.text)]

    def update_interests(self, new_keywords):
        interests = (self.user.interests or "").split()
        interests.extend(new_keywords)
        # keep last 5
        interests = interests[-5:]
        self.user.interests = " ".join(interests)
        self.user.save()

    def from_search(self):
        if self.text == (self.user.interests or ""):
            return
        self.update_interests(self.keywords)

    def from_pdf(self):
        self.update_interests(self.keywords[:3])

    def from_paper(self):
        self.update_interests(self.keywords[:3])
