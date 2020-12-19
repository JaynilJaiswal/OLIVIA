

from sentence_transformers import SentenceTransformer

# Load the BERT model. Various models trained on Natural Language Inference (NLI) https://github.com/UKPLab/sentence-transformers/blob/master/docs/pretrained-models/nli-models.md and 
# Semantic Textual Similarity are available https://github.com/UKPLab/sentence-transformers/blob/master/docs/pretrained-models/sts-models.md

model = SentenceTransformer('bert-base-nli-mean-tokens')

# A corpus is a list with documents split by sentences.
sentences = ['weather','clouds','time','sun','rain','dust','strom','winds']
sentence = ['Absence of sanity', 
             'Lack of saneness',
             'A man is eating food.',
             'A man is eating a piece of bread.',
             'The girl is carrying a baby.',
             'A man is riding a horse.',
             'A woman is playing violin.',
             'Two men pushed carts through the woods.',
             'A man is riding a white horse on an enclosed ground.',
             'A monkey is playing drums.',
             'A cheetah is running behind its prey.',
             'Get me updates on stock market',
             'Get me updates on rupee market',
             "get me details of",
            "1. Abstractive Model",
            "2. Extractive Model",
             "linux",
            "Launch",
            "Build"]

# Each sentence is encoded as a 1-D vector with 78 columns
sentence_embeddings = model.encode(sentence)

print('Sample BERT embedding vector - length', len(sentence_embeddings[0]))

print('Sample BERT embedding vector - note includes negative values', sentence_embeddings[0])


# code adapted from https://github.com/UKPLab/sentence-transformers/blob/master/examples/application_semantic_search.py
import scipy
#query = "second one" #@param {type: 'string'}
query = "rocket"

queries = [query]
query_embeddings = model.encode(queries)

# Find the closest 3 sentences of the corpus for each query sentence based on cosine similarity
number_top_matches = 5 #@param {type: "number"}

print("Semantic Search Results")

for query, query_embedding in zip(queries, query_embeddings):
    distances = scipy.spatial.distance.cdist([query_embedding], sentence_embeddings, "cosine")[0]

    results = zip(range(len(distances)), distances)
    results = sorted(results, key=lambda x: x[1])

    print("\n\n======================\n\n")
    print("Query:", query)
    print("\nTop 5 most similar sentences in corpus:")

    for idx, distance in results[0:number_top_matches]:
        print(sentence[idx].strip(), "(Cosine Score: %.4f)" % (1-distance))


