import os

import pandas as pd
from definitions import RESOURCE_DIR


def load():
    for f in os.listdir(f"{RESOURCE_DIR}/annotations"):
        print("processing %s" % f.upper())
        df = pd.read_csv("%s/annotations/%s" % (RESOURCE_DIR, f), sep="	")
        print(df.info())
        fr = pd.DataFrame(df.describe(include="object")).T
        print(fr.to_latex())

