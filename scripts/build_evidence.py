"""Build aggregate-only website evidence from the saved, read-only METEOR audit.

Usage: python scripts/build_evidence.py --source-dir PATH
No database, network, secrets, or raw descriptions are included in the output.
"""
from artifact_io import write_data
import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
import re

STATES = dict(line.split('|') for line in '''AL|Alabama
AK|Alaska
AZ|Arizona
AR|Arkansas
CA|California
CO|Colorado
CT|Connecticut
DE|Delaware
DC|District of Columbia
FL|Florida
GA|Georgia
HI|Hawaii
ID|Idaho
IL|Illinois
IN|Indiana
IA|Iowa
KS|Kansas
KY|Kentucky
LA|Louisiana
ME|Maine
MD|Maryland
MA|Massachusetts
MI|Michigan
MN|Minnesota
MS|Mississippi
MO|Missouri
MT|Montana
NE|Nebraska
NV|Nevada
NH|New Hampshire
NJ|New Jersey
NM|New Mexico
NY|New York
NC|North Carolina
ND|North Dakota
OH|Ohio
OK|Oklahoma
OR|Oregon
PA|Pennsylvania
RI|Rhode Island
SC|South Carolina
SD|South Dakota
TN|Tennessee
TX|Texas
UT|Utah
VT|Vermont
VA|Virginia
WA|Washington
WV|West Virginia
WI|Wisconsin
WY|Wyoming'''.splitlines())
FOREIGN = re.compile(r'\b(?:India|United Kingdom|England|Canada|Ontario|Quebec|Manitoba|British Columbia|Germany|France|Spain|Italy|Portugal|Poland|Netherlands|Belgium|Switzerland|Ireland|Australia|New Zealand|Brazil|Argentina|Mexico|China|Japan|Singapore|Malaysia|Philippines|Vietnam|Viet Nam|Denmark|Finland|Norway|Sweden|Greece|Bulgaria|Czechia|Tunisia|Costa Rica)\b|中国', re.I)
# Known corrupt country/state expansions observed in the saved source. Do not
# turn the source's India->Indiana or Colombia->Colorado errors into US demand.
CONFLICT = re.compile(r'^(?:Hyderabad|Gurugram|Maharashtra|Mh|Ka|Hr|Ts), Indiana$|^(?:Antioquia|Atl.ntico|Bogot.), Colorado$|^Rp, Delaware$', re.I)
SKILLS = {'SQL': r'\bSQL\b', 'Python': r'\bPython\b', 'R': r'\bR\b',
          'Power BI': r'\bPower\s*BI\b', 'Tableau': r'\bTableau\b', 'Excel': r'\bExcel\b'}


def locate(row):
    """Return one state or an explicit exclusion bucket; no city geocoding."""
    location = (row.get('location_text') or '').strip()
    country = (row.get('countryiso') or '').strip().upper()
    if CONFLICT.search(location):
        return 'location_conflict', None
    if country and country not in ('US', 'USA'):
        return 'explicit_non_us', None
    # Poland, Ohio is an actual US municipality, not a country reference.
    if FOREIGN.search(location) and location.casefold() != 'poland, ohio':
        return 'explicit_non_us', None
    pieces = [x.strip() for x in re.split(r'[,;|]', location)]
    found = {abbr for abbr, name in STATES.items()
             if any(p.casefold() == name.casefold() for p in pieces)}
    # Abbreviations must follow a comma and end at punctuation/ZIP. This avoids
    # treating IN/OR/ME inside prose or foreign region prefixes as US states.
    for match in re.finditer(r',\s*([A-Za-z]{2})(?=\s*(?:\d{5}\b|[,;|]|$))', location):
        if match[1].upper() in STATES:
            found.add(match[1].upper())
    if 'DC' in found:
        found.discard('WA')  # Washington is the city in Washington, DC.
    if len(found) > 1 or (';' in location and found):
        return 'ambiguous_or_multi_location', None
    if found:
        return 'mapped_state', found.pop()
    if re.search(r'\bremote\b|work at home', location, re.I):
        return 'remote_unallocated', None
    if country in ('US', 'USA') or re.search(r'\bUnited States\b|\bUSA?\b|U\.S\.', location, re.I):
        return 'us_unallocated', None
    return 'unknown', None


def build(source, destination):
    names = ['audit.json', 'candidates.json', 'reviewed-examples.json']
    inputs = {name: json.loads((source / name).read_text(encoding='utf-8-sig')) for name in names}
    audit = inputs['audit.json']
    broad = inputs['candidates.json']
    rows = [r for r in broad if r['commercial_signal']]
    assert len(rows) == audit['counts']['commercial_candidates']
    assert len(broad) == audit['counts']['broad_candidates']
    buckets, state_counts, state_hashes = Counter(), Counter(), {s: set() for s in STATES}
    monthly = Counter(r['posted_at'][:7] for r in rows)
    for row in rows:
        bucket, state = locate(row)
        buckets[bucket] += 1
        if state:
            state_counts[state] += 1
            state_hashes[state].add(row['text_fingerprint'])
    months = [f'{year}-{month:02}' for year in (2025, 2026)
              for month in range(1, 13 if year == 2025 else 10)]
    naics = Counter(str(r.get('naics_code') or '').strip() for r in rows)
    soc = Counter(str(r.get('soc_code') or '').strip() for r in rows)
    data = {
        'as_of': '2026-11-02', 'audit_as_of_utc': audit['as_of_utc'],
        'window': audit['window'], 'population': 'Historical screened posting records, all geographies; not current vacancies',
        'counts': {**audit['counts'], 'database_records': audit['enrichment_coverage']['total'],
                   'focused_title_records': audit['focused_commercial_title_counts']['records'],
                   'reviewed_examples': len(inputs['reviewed-examples.json'])},
        'geography': {
            'method': 'Single explicit full state name or comma-delimited postal abbreviation in location text. Explicit foreign countries, known corrupted locations and ambiguous/multiple states excluded. No city-only inference. State matches are inferred, not verified.',
            'denominator': len(rows), 'mapped_records': sum(state_counts.values()),
            'buckets': dict(sorted(buckets.items())),
            'states': [{'code': code, 'name': name, 'records': state_counts[code],
                        'distinct_employer_text_hashes': len(state_hashes[code])} for code, name in STATES.items()],
            'zero_meaning': 'No qualifying mapped record in this screened sample, not zero jobs in the state',
            'remote_note': 'Remote without an allocated state includes unknown country; do not describe all remote records as US remote jobs.'
        },
        'monthly': [{'month': m, 'records': monthly[m]} for m in months],
        'skills': [{'name': name, 'records': sum(bool(re.search(pattern, r.get('description') or '', re.I)) for r in rows),
                    'denominator': len(rows)} for name, pattern in SKILLS.items()],
        'skills_method': 'Whole-term mentions in original descriptions only; mentions are not validated requirements. R may include non-language uses. Multiple skills per record; not additive.',
        'classification': {
            'denominator': len(rows), 'naics_nonblank': len(rows)-naics[''],
            'naics_4_6_digit': sum(n for code, n in naics.items() if re.fullmatch(r'\d{4,6}', code)),
            'naics_3254_prefix': sum(n for code, n in naics.items() if code.startswith('3254')),
            'soc_nonblank': len(rows)-soc[''],
            'soc_standard_format': sum(n for code, n in soc.items() if re.fullmatch(r'\d{2}-\d{4}(?:\.\d{2})?', code)),
            'warning': 'Existing codes are unvalidated enrichment. Coverage and format do not measure accuracy. No industry employment or occupational growth estimate is derived from these codes.'
        },
        'country_codes': [{'code': code, 'records': n} for code, n in audit['countryiso']],
        'limitations': [
            'Historical January 2025–September 2026 records; active flags and saved URL values do not verify a current vacancy.',
            'Keyword screening admits adjacent industries and false positives; this is not a complete pharma analytics market census.',
            'Monthly record changes reflect ingestion and changing source coverage as well as posting activity; they are not employment growth.',
            'Employer/text hashes detect repeated text, not unique requisitions or vacancies. State hash totals may repeat a hash across states.',
            'State assignment is conservative text inference with known conflicts excluded; remaining location errors may exist.',
            'The 13 annotated historical examples are purposive, not a representative validation sample.',
            'No graduate placement, salary uplift, or causal certificate outcomes were measured.'
        ],
        'provenance': {'source_project': 'IndustryClassification/docs/research/pharma-demand',
                       'source_sha256': {name: hashlib.sha256((source/name).read_bytes()).hexdigest() for name in names},
                       'builder': 'scripts/build_evidence.py', 'raw_descriptions_published': False}
    }
    assert sum(monthly.values()) == sum(x['records'] for x in data['monthly']) == len(rows)
    assert sum(buckets.values()) == len(rows)
    assert sum(state_counts.values()) == buckets['mapped_state']
    assert dict(audit['commercial_monthly']) == {k: v for k, v in monthly.items() if v}
    assert len({r['text_fingerprint'] for r in rows}) == audit['counts']['commercial_distinct_employer_text']
    write_data('meteor',data)
    # Explicit whitelist: no raw text, person data, database credentials or HTML.
    keep = ('id', 'company_name', 'title', 'location_text', 'posted_at', 'apply_url',
            'role_family', 'education_experience_review', 'data_tools_review', 'curriculum_mapping', 'review_basis')
    examples = [{k: row[k] for k in keep} for row in inputs['reviewed-examples.json']]
    write_data('reviewed-examples',examples)
    print(f'EVIDENCE_AGGREGATES_OK: {len(rows)} commercial records; {sum(state_counts.values())} state-mapped; {len(examples)} reviewed examples')
    print(json.dumps(dict(buckets), sort_keys=True))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-dir', type=Path, required=True)
    parser.add_argument('--output-dir', type=Path, default=None, help='Deprecated; task-scoped Parquet paths are fixed by artifact_io.')
    args = parser.parse_args()
    build(args.source_dir, args.output_dir)
