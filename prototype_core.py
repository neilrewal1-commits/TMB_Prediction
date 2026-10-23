"""Patient-profile and input checks for an educational research prototype.

No text-generation service or medical decision model is called here.
"""
from __future__ import annotations
import csv
import hashlib
import io
import json
import math
from pathlib import Path
import re

import pandas as pd

ROOT = Path(__file__).resolve().parent
GENES = json.loads((ROOT / 'demo_data' / 'feature_schema.json').read_text())['genes']
MAX_BYTES = 5 * 1024 * 1024
FIELDS = {
    'diagnosis': 'Documented diagnosis',
    'stage': 'Documented stage',
    'staging_edition': 'Staging edition',
    'imaging_findings': 'Imaging findings',
    'age': 'Age',
    'weight': 'Weight',
    'albumin': 'Albumin',
    'nlr': 'NLR',
    'measured_tmb': 'Measured TMB',
    'prior_systemic': 'Prior systemic therapy',
    'other_conditions': 'Other conditions',
    'treatment_history': 'Treatment history',
}
ALIASES = {v.lower(): k for k, v in FIELDS.items()}
ALIASES.update({'recorded pathological stage': 'stage', 'recorded pathologic stage': 'stage',
                'pathologic stage': 'stage', 'impression': 'imaging_findings',
                'diagnosis': 'diagnosis', 'patient age': 'age'})


def genomic_csv(data: bytes, *, single_patient=False) -> pd.DataFrame:
    if not data or len(data) > MAX_BYTES:
        raise ValueError('Choose a nonempty CSV smaller than 5 MB.')
    try:
        text = data.decode('utf-8-sig')
        reader = csv.reader(io.StringIO(text))
        header = next(reader)
        if len(header) != len(set(header)):
            raise ValueError('Duplicate gene columns are not allowed.')
        if any(len(row) != len(header) for row in reader if row):
            raise ValueError('Every CSV row must have exactly one value per gene column.')
        frame = pd.read_csv(io.StringIO(text))
    except (UnicodeError, StopIteration, pd.errors.ParserError, pd.errors.EmptyDataError) as exc:
        raise ValueError('This file could not be read as a UTF-8 gene CSV.') from exc
    if frame.empty:
        raise ValueError('The CSV has no patient rows.')
    if single_patient and len(frame) != 1:
        raise ValueError('Upload exactly one patient row for this patient profile.')
    missing, extra = sorted(set(GENES) - set(frame)), sorted(set(frame) - set(GENES))
    if missing or extra:
        parts = []
        if missing: parts.append('Missing genes: ' + ', '.join(missing))
        if extra: parts.append('Unexpected columns: ' + ', '.join(extra))
        raise ValueError('; '.join(parts) + '. Missing genes cannot be assumed negative.')
    ordered = frame.loc[:, GENES].apply(pd.to_numeric, errors='coerce')
    if ordered.isna().any().any() or not ordered.isin([0, 1]).all().all():
        raise ValueError('Every gene value must be 0 or 1, with no blanks or unknowns.')
    return ordered.astype(int)


def document_text(data: bytes, filename: str) -> list[str]:
    if not data or len(data) > MAX_BYTES:
        raise ValueError('Choose a nonempty report smaller than 5 MB.')
    suffix = Path(filename).suffix.lower()
    try:
        if suffix == '.pdf':
            from pypdf import PdfReader
            reader = PdfReader(io.BytesIO(data))
            if reader.is_encrypted:
                raise ValueError('Encrypted PDFs are not supported.')
            if len(reader.pages) > 30:
                raise ValueError('Use a report of 30 pages or fewer.')
            pages = [page.extract_text() or '' for page in reader.pages]
        elif suffix == '.txt':
            pages = [data.decode('utf-8-sig')]
        else:
            raise ValueError('Use a PDF or UTF-8 TXT report.')
    except ValueError:
        raise
    except Exception as exc:
        raise ValueError('Could not extract text. Use a readable PDF or TXT report.') from exc
    if not any(p.strip() for p in pages):
        raise ValueError('No readable text found. This version does not perform OCR on scanned images.')
    return pages


def inspect_report(data: bytes, filename: str, expected_id: str, stage: str) -> dict:
    pages = document_text(data, filename)
    text = '\n'.join(pages)
    explicit_ids = re.findall(r'^\s*Case ID\s*:\s*(\S+)', text, re.M | re.I)
    if explicit_ids and any(x != expected_id for x in explicit_ids):
        raise ValueError('The report Case ID does not match the selected case.')
    simulated = bool(re.search(r'\b(SIMULATED|FICTIONAL|SYNTHETIC)\b', text, re.I))
    rows = []
    allowed = {'diagnosis','stage','staging_edition','imaging_findings','treatment_history'} if stage == 'imaging' else {'age','weight','albumin','nlr','measured_tmb','prior_systemic','other_conditions','treatment_history'}
    for page, content in enumerate(pages, 1):
        for line in content.splitlines():
            if ':' not in line: continue
            label, value = line.split(':', 1)
            key = ALIASES.get(label.strip().lower())
            if key in allowed and value.strip():
                rows.append({'field': key, 'value': value.strip(), 'page': page, 'excerpt': line.strip()})
    provenance = 'Simulated report' if simulated else 'Uploaded report — user confirmed'
    if not simulated and 'RECONSTRUCTED RESEARCH SUMMARY' in text:
        provenance = 'Report labeled reconstructed — user confirmed'
    return {'id': hashlib.sha256(data).hexdigest(), 'filename': filename,
            'case_id': expected_id, 'stage': stage, 'pages': pages, 'fields': rows,
            'simulated': simulated, 'explicit_case_id': bool(explicit_ids),
            'provenance': provenance}


def current_facts(documents: list[dict]) -> tuple[dict, list[str]]:
    """Keep contradictory evidence visible; do not resolve it by upload order."""
    grouped = {}
    for doc in documents:
        for row in doc['fields']:
            grouped.setdefault(row['field'], []).append(dict(row, filename=doc['filename'],
                provenance=doc['provenance'], document_id=doc['id']))
    facts, conflicts = {}, []
    for key, records in grouped.items():
        values = {r['value'].strip().casefold() for r in records}
        if len(values) > 1:
            conflicts.append(key)
        else:
            facts[key] = records[-1]
    return facts, conflicts


def commit_report(documents: list[dict], document: dict) -> tuple[list[dict], list[str]]:
    if any(d['id'] == document['id'] for d in documents):
        raise ValueError('This report is already in this case. Remove it before replacing it.')
    before, old_conflicts = current_facts(documents)
    after, conflicts = current_facts(documents + [document])
    changes = []
    for key in set(before) | set(after) | set(conflicts):
        if key in conflicts and key not in old_conflicts:
            changes.append(FIELDS[key] + ': conflicting reports — review needed')
        elif key in after and (key not in before or before[key]['value'] != after[key]['value']):
            changes.append(FIELDS[key] + ': ' + after[key]['value'])
    if not changes: changes = ['Report added; no new supported structured facts.']
    return documents + [document], sorted(changes)


def numeric(value: str, field: str) -> float:
    patterns = {
        'age': r'(\d+(?:\.\d+)?)\s*(?:years?|yrs?)',
        'albumin': r'(\d+(?:\.\d+)?)\s*g/dL',
        'nlr': r'(\d+(?:\.\d+)?)(?:\s*ratio)?',
        'measured_tmb': r'(\d+(?:\.\d+)?)\s*(?:mut/Mb|mutations/Mb)',
    }
    match = re.fullmatch(patterns[field], value.strip(), re.I)
    if not match:
        raise ValueError(FIELDS[field] + ': missing value, qualifier, or unsupported unit.')
    result = float(match.group(1))
    if not math.isfinite(result) or (field in {'age','albumin'} and result <= 0):
        raise ValueError(FIELDS[field] + ': invalid value.')
    return result


def loris_readiness(facts: dict, conflicts: list[str]) -> dict:
    """Expose required inputs; no unverified score version is chosen for users."""
    keys = ['diagnosis','age','albumin','nlr','measured_tmb','prior_systemic']
    missing = [FIELDS[k] for k in keys if k not in facts]
    errors = []
    values = {}
    for key in ['age','albumin','nlr','measured_tmb']:
        if key in facts:
            try: values[key] = numeric(facts[key]['value'], key)
            except ValueError as exc: errors.append(str(exc))
    if 'prior_systemic' in facts and facts['prior_systemic']['value'].strip().lower() not in ['yes','no']:
        errors.append('Prior systemic therapy: confirm yes or no before checkpoint therapy.')
    if 'diagnosis' in facts:
        # A free-text diagnosis is never classified into a model cancer category.
        values['diagnosis_text'] = facts['diagnosis']['value']
    return {'missing':missing,'errors':errors,'fields_present':not missing and not errors,
            'values':values,'conflicts':[FIELDS[k] for k in conflicts if k in keys]}


def export_summary(case: dict, mode: str, genomic: dict | None, documents: list[dict], clinical: dict | None = None) -> str:
    facts, conflicts = current_facts(documents)
    lines = ['CANCER CARE · CASE SUMMARY', 'Case: ' + case['id'], 'Data: ' + mode, '']
    if genomic:
        lines += ['TMB study category: ' + genomic['label'], 'Input: ' + genomic['source'], '']
    for doc in documents:
        lines += ['Report: ' + doc['filename'] + ' (' + doc['provenance'] + ')']
        for row in doc['fields']:
            if row['field'] in conflicts:
                lines += [f"Conflicting evidence — {FIELDS[row['field']]}: {row['value']} (page {row['page']})"]
    for key, row in facts.items():
        lines += [FIELDS[key] + ': ' + row['value'],
                  f"Source: {row['filename']}, page {row['page']} ({row['provenance']})"]
    if conflicts: lines += ['', 'Conflicting fields: ' + ', '.join(FIELDS[k] for k in conflicts)]
    lines += ['', 'Unknown or unresolved:', *['- '+FIELDS[k] for k in FIELDS if k not in facts]]
    lines += ['', 'LORIS: no response estimate issued.',
              'Sources:', 'https://www.cancerimagingarchive.net/collection/tcga-stad/',
              'https://github.com/rootchang/LORIS',
              'https://www.cancer.gov/types/stomach/treatment/by-stage']
    if clinical:
        lines += ['', 'SEPARATE CLINICAL ASSESSMENT',
                  'Provenance: '+clinical['provenance'], 'Assessment source: '+clinical['source'],
                  'Calculated group: '+str(clinical['staging']['stage']),
                  'Components: '+clinical['staging']['tnm'],
                  'Review blockers: '+ '; '.join(clinical['staging']['blockers']+clinical['treatment']['blockers'])]
        for card in clinical['treatment']['cards']:
            lines += ['Discussion option: '+card['title'],card['why'],card['checks'],'Evidence: '+card['source']]
        lines += ['Missing: '+', '.join(clinical['treatment']['missing']),*clinical['treatment']['notes'],
                  'Rules: '+clinical['staging']['version']]
    return '\n'.join(lines)
