"""Prevent private network identifiers from entering public examples."""
from ipaddress import ip_address, ip_network
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
ALLOWED = tuple(ip_network(x) for x in ('192.0.2.0/24', '198.51.100.0/24', '203.0.113.0/24'))
IP = re.compile(r'(?<![0-9.])(?:\d{1,3}\.){3}\d{1,3}(?![0-9.])')
MAC = re.compile(r'\b(?:[a-fA-F0-9]{2}:){5}[a-fA-F0-9]{2}\b')
SUFFIXES = {'.md', '.json', '.yaml', '.yml', '.py', '.svg', '.txt'}
problems = []
for path in ROOT.rglob('*'):
    if not path.is_file() or path.suffix.lower() not in SUFFIXES:
        continue
    if '.git' in path.parts:
        continue
    body = path.read_text(encoding='utf-8')
    for hit in IP.finditer(body):
        try:
            address = ip_address(hit.group())
        except ValueError:
            continue
        if address.is_private and not any(address in net for net in ALLOWED):
            problems.append(f'{path.relative_to(ROOT)}: private IPv4 address detected')
    if MAC.search(body):
        problems.append(f'{path.relative_to(ROOT)}: MAC address detected')
if problems:
    print('\n'.join(problems), file=sys.stderr)
    sys.exit(1)
print('Public example scan passed.')
