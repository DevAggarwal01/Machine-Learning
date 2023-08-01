import math
import numpy as np
from nltk import RegexpTokenizer
import networkx



data = 'Quantum computing is a revolutionary paradigm that utilizes the principles of quantum mechanics to process and manipulate information. At its core, quantum computing harnesses the unique properties of quantum bits, or qubits, which can exist in a superposition of both 0 and 1 states simultaneously. This allows quantum computers to perform computations in parallel, potentially providing exponential speedups for certain types of problems compared to classical computers. One of the key concepts in quantum computing is entanglement. When qubits become entangled, their states become correlated in such a way that the state of one qubit cannot be described independently of the others. This property enables quantum computers to manipulate and process information in a highly interconnected manner, leading to the potential for solving complex problems more efficiently. However, quantum computing faces significant challenges. Quantum systems are susceptible to errors caused by decoherence, which is the loss of quantum coherence due to environmental interactions. Ensuring the reliability and stability of qubits is a major technical hurdle. Additionally, building large-scale quantum computers remains a significant engineering feat due to the delicate nature of qubits and the need for precise control over quantum states. Despite these challenges, quantum computing holds immense promise. It has the potential to revolutionize fields such as cryptography, optimization, simulation, and machine learning, tackling problems that are currently intractable for classical computers. Ongoing research and development in quantum computing are focused on improving qubit stability, developing error-correction techniques, and exploring new technologies to build more powerful and scalable quantum systems.'
if(data[-1]=='.'):
    data = data[:-1]
sentences = data.split('.')
similarityScore = np.zeros((len(sentences), len(sentences)))

tokenizer = RegexpTokenizer(r'\w+')

for s1 in range(0,len(sentences)-1):
    for s2 in range(s1+1, len(sentences)):
        if(s1 == s2):
            continue
        sentence1 = tokenizer.tokenize(sentences[s1])
        sentence2 = tokenizer.tokenize(sentences[s2])
        count = 0
        for x in range(len(sentence1)):
            for y in range(x, len(sentence2)):
                if(sentence1[x]==sentence2[y]):
                    count+=1
        similarityScore[s1, s2] = count/(math.log(len(sentence1))+math.log(len(sentence2)))
        similarityScore[s2, s1] = similarityScore[s1, s2]

print(similarityScore.max())

def pagerank(trans_mat, eps=0.0001, d=0.85):
    prob = np.ones(len(trans_mat)) / len(trans_mat)
    count = 0
    while count < 20:
        new_prob = np.ones(len(trans_mat)) * (1-d) / len(trans_mat) + d*trans_mat.T.dot(prob)
        delta = abs(new_prob-prob).sum()
        if delta <= eps:
            return new_prob
        prob = new_prob
        count +=1
    return prob

nx_graph = networkx.from_numpy_array(similarityScore)
results = networkx.pagerank(nx_graph)
ranked_sentences = sorted(((results[i],s) for i,s in enumerate(sentences)), reverse=True)

for i in range(5):
    print(ranked_sentences[i][1], end=". ")

results = pagerank(similarityScore)
sorted_results = np.sort(results)
sorted_results = sorted_results[::-1]
print("\n")
for x in range(len(results)):
    if results[x]==sorted_results[0]:
        print(sentences[x], end=". ")
    elif results[x]==sorted_results[1]:
        print(sentences[x], end=". ")
    elif results[x]==sorted_results[2]:
        print(sentences[x], end=". ")
    elif results[x]==sorted_results[3]:
        print(sentences[x], end=". ")
    elif results[x]==sorted_results[4]:
        print(sentences[x], end=". ")
