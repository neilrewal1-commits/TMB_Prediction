"""Use the repository's original feature validator and fixed model."""
import pickle
from functools import lru_cache

import pandas as pd

from prototype_core import GENES, ROOT, genomic_csv

STATUSES = ['Unknown', 'Mutated', 'Not mutated']


def reviewed_features(rows):
    if len(rows) != len(GENES) or {r['gene'] for r in rows} != set(GENES):
        raise ValueError('Exactly one row for each of the 50 required genes is needed.')
    values = {}
    for row in rows:
        status = row['status']
        if status not in STATUSES[1:]:
            raise ValueError('Every gene must have a confirmed status. Unknown is not negative.')
        if not str(row.get('evidence', '')).strip():
            raise ValueError('Every gene needs supporting text or a source reference.')
        values[row['gene']] = 1 if status == 'Mutated' else 0
    return genomic_csv(pd.DataFrame([values]).to_csv(index=False).encode(), single_patient=True)


@lru_cache(maxsize=1)
def load_model():
    with (ROOT / 'Best_Model_RF_50Trees_7Depth').open('rb') as handle:
        return pickle.load(handle)


def predict(rows):
    frame = reviewed_features(rows)
    prediction = int(load_model().predict(frame.to_numpy())[0])
    return {'label': ['Low study category', 'High study category'][prediction],
            'model': 'Original 50-gene random forest',
            'scope': 'Research category; not measured TMB in mutations/Mb',
            'features': frame.iloc[0].to_dict()}
