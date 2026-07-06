import pandas as pd
import numpy as np
from pathlib import Path

INPUT_PATH = Path('data/insdn.csv')
OUTPUT_PATH = Path('data/final1.csv')

FEATURE_CANDIDATES = {
    'packet_count': ['packet_count', 'pktcount', 'packets', 'tot_pkts'],
    'byte_count': ['byte_count', 'bytecount', 'bytes', 'tot_bytes'],
    'flow_duration_sec': ['flow_duration_sec', 'dur_sec', 'duration_sec'],
    'flow_duration_nsec': ['flow_duration_nsec', 'dur_nsec', 'duration_nsec'],
    'packet_count_per_second': ['packet_count_per_second', 'pkt_per_sec', 'packets_per_second'],
    'byte_count_per_second': ['byte_count_per_second', 'bytes_per_second', 'byte_per_sec'],
    'label': ['label', 'Label', 'class', 'Class']
}


def pick_column(df, aliases, required=True):
    for name in aliases:
        if name in df.columns:
            return name
    if required:
        raise KeyError(f'Missing required column. Tried: {aliases}')
    return None


def clean_label(value):
    text = str(value).strip().lower()
    benign_tokens = {'normal', 'benign', '0', 'legitimate'}
    return 0 if text in benign_tokens else 1


def main():
    if not INPUT_PATH.exists():
        raise FileNotFoundError(f'Input dataset not found: {INPUT_PATH}')

    df = pd.read_csv(INPUT_PATH)
    print('Loaded rows, cols:', df.shape)

    cols = {key: pick_column(df, aliases) for key, aliases in FEATURE_CANDIDATES.items()}
    work = df.copy()

    for key in ['packet_count', 'byte_count', 'flow_duration_sec', 'flow_duration_nsec',
                'packet_count_per_second', 'byte_count_per_second']:
        col = cols.get(key)
        if col and col in work.columns:
            work[col] = pd.to_numeric(work[col], errors='coerce')

    work['label'] = work[cols['label']].apply(clean_label)

    sec = pd.to_numeric(work[cols['flow_duration_sec']], errors='coerce').fillna(0)
    nsec = pd.to_numeric(work[cols['flow_duration_nsec']], errors='coerce').fillna(0)
    work['duration'] = sec + (nsec / 1e9)

    work['packet_count'] = pd.to_numeric(work[cols['packet_count']], errors='coerce')
    work['byte_count'] = pd.to_numeric(work[cols['byte_count']], errors='coerce')

    if cols.get('packet_count_per_second') in work.columns:
        work['packet_count_per_second'] = pd.to_numeric(
            work[cols['packet_count_per_second']], errors='coerce'
        )
    else:
        work['packet_count_per_second'] = work['packet_count'] / work['duration'].replace(0, np.nan)

    if cols.get('byte_count_per_second') in work.columns:
        work['byte_count_per_second'] = pd.to_numeric(
            work[cols['byte_count_per_second']], errors='coerce'
        )
    else:
        work['byte_count_per_second'] = work['byte_count'] / work['duration'].replace(0, np.nan)

    work['packet_count_per_second'] = work['packet_count_per_second'].fillna(
        work['packet_count'] / work['duration'].replace(0, np.nan)
    )
    work['byte_count_per_second'] = work['byte_count_per_second'].fillna(
        work['byte_count'] / work['duration'].replace(0, np.nan)
    )

    work = work.replace([np.inf, -np.inf], np.nan)

    required_cols = [
        'packet_count', 'byte_count', 'duration',
        'packet_count_per_second', 'byte_count_per_second', 'label'
    ]
    work = work.dropna(subset=required_cols)

    work = work[
        (work['duration'] > 0) &
        (work['packet_count'] >= 0) &
        (work['byte_count'] >= 0) &
        (work['packet_count_per_second'] >= 0) &
        (work['byte_count_per_second'] >= 0)
    ]

    clip_cols = [
        'packet_count',
        'byte_count',
        'packet_count_per_second',
        'byte_count_per_second'
    ]
    q_hi = work[clip_cols].quantile(0.999)
    for col in clip_cols:
        work[col] = work[col].clip(upper=q_hi[col])

    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    work.to_csv(OUTPUT_PATH, index=False)

    print('\nFinal dataset shape:', work.shape)
    print(work['label'].value_counts(dropna=False))
    print(f'\nSaved cleaned dataset to: {OUTPUT_PATH}')


if __name__ == '__main__':
    main()
