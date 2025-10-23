# SeqOne ML engineer challenge

## Notes
Determining the basal identity of skeletal cells and their gene expression profile is one of the most urgent questions in bone biology.
Articles related to the labeling : 
https://pubmed.ncbi.nlm.nih.gov/37079387/
https://pmc.ncbi.nlm.nih.gov/articles/PMC4507066/
https://pmc.ncbi.nlm.nih.gov/articles/PMC6477889/
https://pmc.ncbi.nlm.nih.gov/articles/PMC4030116/
https://www.caducee.net/actualite-medicale/1603/bronchiolite-du-nourrisson-un-lien-avec-le-gene-de-br-l-interleukine-8.html
At present, genome‐wide association studies (GWAS), including replication of identified loci, are the preferred method for gene discovery, but only one, relatively small, GWAS of bronchiolitis have been performed without genome‐wide significant findings.24 A number of susceptibility genes have been suggested from candidate gene studies. Most studies focused on RSV bronchiolitis, and the reported associations include genes related to immune regulation and surfactant proteins.25 Several of these genes have also been associated with asthma,25 suggesting that the association between RSV bronchiolitis and later asthma development might partly be explained by shared genetics.


## Task 
- the system has to generate a formatted response that gives the genes that are the most likely to cause the disease.

- Example:
  - Description : "Le patient a un syndrome interstitiel pulmonaire. Il est diabétique. Il a également un Glaucome/DMLA"
  - Réponse : "The genes that are the most likely to cause the disease are:

Gene1
Gene2
..."

The goal is not to use only the knowledge from the LLM but to enrich it with external sources to make the answers reliable. Here the most relevant source to enrich it is the hpo.jax resource. You can find it here : https://hpo.jax.org/.
With this database, all human symptoms are encoded with a unique ID of the shape HP:XXXXXXX. The resource also provided a list of all genes associated to a given symptom. The resources files are available here https://hpo.jax.org/data/annotations. You are also free to integrate in your system any resource you find useful.

## Related Resources

- **HPO: human phenotype ontology.**: Provides standardized vocabulary of phenotypic abnormalities encountered in human disease. Each term in the HPO describes a phenotypic abnormality, such as Atrial septal defect.

- **OMIM**:  An Online Catalog of Human Genes and Genetic Disorders

- **NCBI**: NCBI's Gene resources include collections of curated nucleotide sequences used as references, sequence clusters to predict and study homologs, and various databases and tools for the study of gene expression.

- **ORPHA**: OrphaNet. Knowledge on rare diseases and orphan drugs

- **SNOMED**: Systematized Nomenclature OF Medicine Clinical Terms

- **MONDO**: provides precise equivalences between disease concepts, we created Mondo, which provides a logic-based structure for unifying multiple disease resources.

<p align="center">
<img src="./plots/connected_components.png" />
</p>

## Steps 

### **1. Domain Knowledge Discovery**
   - HPO terms appear as pivots between the disease related pieces of knowledge and gene information
   - 22 964 nodes available in the annotation files have the degree of 1 ( can be seen as "leaves")
   - the connected nodes form a set of 4469 nodes 
   - some data is inconsistent (duplicates)
   - coverage vary a lot from one source to another

### _Improvement (1):_
- further explore the structure of each resource separately to better handle the overall picture. Stick to HPO. 
- possibly introduce direction, weights and negatively weighted (explicitly false) relations (for critical cases)
- How to compute weights?
- possibly introduce reifications of some relations of the kind "gene G is responsible for abnormality A with local frequency F" and this information is to be manipulated as a whole for some reason


###  **2. Lexicalization**
   - the goal is to link gene symbols to some textual expression of HPs and diseases
   - some lexicalizations are directly available  from the resources
   - the semi-lexicalised graph is passed to a LLM completion agent in order to generate summaries about each connected node based on its neighbours

### _Improvement (2):_
- use / train an evaluation Agent to evaluate lexicalizations produced by the completion Agent 
- or use a controlled GAN architecture depending on explainability insights


### **3. Vectorization**
   - structuring the textual data obtained in (2) as LangChain Document object with metadata
   - loading into a VectorStore as embedding

### _Improvement (3):_
- benchmark VectorStores
- try local approach rather than global LLM based vectorization, try indexing strategies to pre-select relevant documents to browse given a query
- update VectorStore incrementally 

### **4. Retrieval**
- specific retrieval agent for testing
- scoring function (i.e. cosine similarity) to locally evaluate how close the response is to the query

### _Improvement (4):_
- use cache
- diversify templates and scoring functions 
- (also for 2) benchmark LLMS to grasp a relevant LLM param space etc : use some straightforward factual task (as we would do to check if a given model actually "knows" gps coordinates of French cities, a task easy to plot and see inconsistencies)
- backpropagate the knowledge gained from retrieval to support lexicalization process and (maybe?) infer connexions in the "conceptual" "layer". How to validate the knowledge gain? (i.e. we only backpropagate if it is new and relevant given the previous expert knowledge we used)
- explore reinforcement learning from retrieval with knowledge gain as reward



## Project structure 
```
test-nadia/
├── codebase/
│   ├── __pycache__/
│   │   ├── Retriever.cpython-313.pyc
│   │   ├── templates.cpython-313.pyc
│   │   ├── utest.cpython-313-pytest-8.4.1.pyc
│   │   └── utils.cpython-313.pyc
│   ├── Builder.py
│   ├── cli.py
│   ├── knowledge.py
│   ├── Retriever.py
│   ├── templates.py
│   ├── utest.py
│   └── utils.py
├── config.yml
├── plots/
│   └── connected_components.png
├── poetry.lock
├── project_description.md
├── pyproject.toml
└── resources/
    ├── annotations/
    │   ├── genes_to_disease.txt
    │   ├── genes_to_phenotype.txt
    │   ├── maxo-annotations.tsv
    │   ├── phenotype.hpoa
    │   └── phenotype_to_genes.txt
    ├── documents/
    ├── ontology/
    │   └── hp.json
    └──vectors/
       ├── index.faiss
       └── index.pkl

```

_Note : the resources are those from the HPO website. They are not fully uploaded here, but they are publicly available._


## Test Results
The solution of the challenge has been implemented based on domain knowledge resources. 
It has been tested on the provided data using a commandline interface . 

Example of description :
```
 Le patient a un Polykystose hépato rénale. Une Maladie lithiasique rénale sévère depuis l'enfance, avec urique et oxalate Ca. 
 Il a eu des infections urinaires récidivantes ainsi qu'une Polykystose hépato rénale. HTA développé à l'adolescence.
```

Example of response : 

```
Response :
- NEK8
- GDF6
- PHEX
 Score (cosine): 0.59
 ```
