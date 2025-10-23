summary= """Based on the following associations {associations}, write a short summary. 
            Format the output as follows : {"summary": summary, "meta":{"gene": gene, "disease": disease}
            Do not provide comments. """

structured_summary = """<instruction>Based on the following associations {associations}, write a short summary. </instruction>
                        <context>
                        Associations: {associations}
                        </context>
                        
                        <code_block format="json">
                        // Your JSON here
                        </code_block>            
"""