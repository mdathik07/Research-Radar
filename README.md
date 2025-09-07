# Research-Radar

## Description
Research-Radar is a research paper recommendation system that uses content-based filtering via cosine similarity between vectors created with TF-IDF and saved in MongoDB.

## [+] Installation
1. `cd Backend; pip install -r requirements.txt`
2. `python manage.py runserver`
3. `cd Frontend; npm install`
4. `npm run dev`

## [+] Features
- **Content-Based Filtering**: This method recommends articles by analyzing their content rather than tracking user behavior. It finds relevant articles based on what’s written, ensuring quality recommendations.  
- **Article Ranking**: Articles are ranked based on relevance and quality, with the best ones highlighted. Less relevant articles are still considered but given lower priority.  
- **Text Analysis**: The system scans articles for keywords and context to understand their main topics, ensuring accurate recommendations.  
- **No User Tracking**: Research-Radar focuses entirely on the content itself, not on tracking your reading habits or personal data.
