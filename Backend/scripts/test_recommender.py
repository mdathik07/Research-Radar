# scripts/test_recommender.py
import os, sys, django

# Add the parent folder (the one containing "Backend" package) to sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Backend.settings")
django.setup()

from api.recommender import DocumentSearch

def main():
    ds = DocumentSearch()
    try:
        results = ds.search("deep learning", min_results=10, threshold=0.2)
    except ValueError as e:
        print("Error:", e)
        return

    print(f"Found {len(results)} results:")
    for p in results:
        print(p.id, "-", (p.title[:120] if p.title else "(no title)"))

if __name__ == "__main__":
    main()
