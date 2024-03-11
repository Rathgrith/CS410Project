import DataPipeline.utils as datautils

# read arxiv json with limit
data = datautils.read_json('./arxiv-metadata-oai-snapshot.json', limit=10000)
print(data.head())
print(data.columns)
print(data.shape)
data = datautils.preprocess_abstracts(data)
# print preprocessed abstracts
print(data['abstract'].head())
print(data.shape)
