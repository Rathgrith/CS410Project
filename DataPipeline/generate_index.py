from utils import build_indexes

metadata_path = 'arxiv-metadata-oai-snapshot.json'  # Adjust the path to your metadata file
build_indexes(metadata_path, limit=float('inf'), fields=['title', 'abstract', 'authors'])
