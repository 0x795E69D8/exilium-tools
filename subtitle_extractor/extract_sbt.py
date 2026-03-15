"""
USM @SBT Subtitle Extractor

Subtitle ID mapping:
  0 = Translation IDs
  1 = Japanese
  2 = Korean

Payload structure per stream chunk (after the 24-byte chunk payload header):
  Offset  Size  Description
  0       4     Subtitle ID (uint32 LE)
  4       4     Time unit (uint32 LE) — typically 1000 (milliseconds)
  8       4     Start time in time_units (uint32 LE)
  12      4     Duration in time_units (uint32 LE)
  16      4     String byte length incl. null terminator (uint32 LE)
  20      N     UTF-8 string (null-terminated)

Usage: python extract_sbt.py input.usm [base_output] [--single]
  --single      Write everything to one .srt instead of splitting by language
"""

import struct
import sys
import os

LANG_MAP = {
    0: 'TID',
    1: 'JP',
    2: 'KR',
}


def extract_sbt(path):
    with open(path, 'rb') as f:
        data = f.read()

    entries = []
    i = 0

    while i < len(data) - 8:
        ident = data[i:i+4]
        chunk_size = struct.unpack_from('>I', data, i + 4)[0]
        if chunk_size == 0:
            i += 8
            continue

        if ident == b'@SBT':
            payload_type = data[i + 8 + 7]

            if payload_type == 0:  # stream chunk
                payload_offset = data[i + 8 + 1]
                p = i + 8 + payload_offset

                if p + 20 <= len(data):
                    sub_id    = struct.unpack_from('<I', data, p)[0]
                    time_unit = struct.unpack_from('<I', data, p + 4)[0]
                    start_tu  = struct.unpack_from('<I', data, p + 8)[0]
                    dur_tu    = struct.unpack_from('<I', data, p + 12)[0]
                    str_len   = struct.unpack_from('<I', data, p + 16)[0]

                    if time_unit > 0 and str_len > 0 and p + 20 + str_len <= len(data):
                        raw  = data[p + 20: p + 20 + str_len].rstrip(b'\x00')
                        text = raw.decode('utf-8', errors='replace').strip()

                        start_sec = start_tu / time_unit
                        end_sec   = start_sec + (dur_tu / time_unit)
                        lang      = LANG_MAP.get(sub_id, f'id{sub_id}')

                        entries.append({
                            'id':    sub_id,
                            'lang':  lang,
                            'start': start_sec,
                            'end':   end_sec,
                            'text':  text,
                        })

        i += 8 + chunk_size

    return entries


def fmt_time(s):
    h   = int(s) // 3600
    m   = (int(s) % 3600) // 60
    sec = int(s) % 60
    ms  = int(round((s % 1) * 1000))
    if ms == 1000:
        sec += 1
        ms = 0
    return f"{h:02}:{m:02}:{sec:02},{ms:03}"


def to_srt(entries):
    lines = []
    for n, e in enumerate(entries, 1):
        lines.append(f"{n}\n{fmt_time(e['start'])} --> {fmt_time(e['end'])}\n{e['text']}\n")
    return '\n'.join(lines)


def write_srt(entries, path):
    with open(path, 'w', encoding='utf-8') as f:
        f.write(to_srt(entries))
    print(f"  Wrote {len(entries):3} entries -> {path}")


def main():
    if len(sys.argv) < 2:
        print("Usage: python extract_sbt.py input.usm [base_output] [--single]")
        sys.exit(1)

    input_path  = sys.argv[1]
    single_file = '--single'    in sys.argv
    output_args = [a for a in sys.argv[2:] if not a.startswith('--')]
    base        = output_args[0] if output_args else os.path.splitext(input_path)[0]

    if not os.path.exists(input_path):
        print(f"Error: file not found: {input_path}")
        sys.exit(1)

    print(f"Scanning {input_path} for @SBT chunks...")
    entries = extract_sbt(input_path)

    if not entries:
        print("No subtitle entries found.")
        sys.exit(1)

    from collections import Counter
    counts = Counter(e['lang'] for e in entries)
    print(f"Found {len(entries)} total entries: { dict(counts) }\n")

    for e in entries:
        tag = f"[{e['lang']}]"
        print(f"  {tag:5} id={e['id']}  {fmt_time(e['start'])} --> {fmt_time(e['end'])}  {e['text']}")

    print()

    if single_file:
        write_srt(entries, base + '.srt')
    else:
        for lang in ['JP', 'KR']:
            subset = [e for e in entries if e['lang'] == lang]
            if subset:
                write_srt(subset, f"{base}_{lang}.srt")
        other = [e for e in entries if e['lang'] not in ('TID', 'JP', 'KR')]
        if other:
            write_srt(other, f"{base}_other.srt")
        ids = [e for e in entries if e['lang'] == 'TID']
        if ids:
            write_srt(ids, f"{base}.srt")


if __name__ == '__main__':
    main()
