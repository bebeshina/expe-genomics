summary= """Based on the following associations {associations}, write a short summary. 
            Format the output as follows : {"summary": summary, "meta":{"gene": gene, "disease": disease}
            Do not provide comments. """

response="""Based on the following description provide the list of gene symbols of up to 3 main genes that may be related to the description. 
            Description: {description}
            Response format: 
            - Gene 1: gene 1 symbol
            - Gene 2: gene 2 symbol
            - Gene 3:...
           Provide a brief explanation based on documents.
            
"""