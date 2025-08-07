### ===============================
### tools/data_stats.py
### ===============================

import json
from collections import defaultdict

with open("data/intents.json", 'r', encoding='utf-8') as f:
    data = json.load(f)

intent_counts = defaultdict(int)
for intent in data['intents']:
    tag = intent['tag']
    patterns = intent.get('patterns', [])
    intent_counts[tag] = len(patterns)

print("\n📊 Intent Statistics Report")
print("==========================")
print(f"Total Intents: {len(intent_counts)}")
for tag, count in intent_counts.items():
    print(f"- {tag}: {count} patterns")

# Warn about imbalance
min_count = min(intent_counts.values())
max_count = max(intent_counts.values())
if min_count < 5:
    print("\n⚠️  Warning: Some intents have fewer than 5 examples.")
if max_count > min_count * 5:
    print("⚠️  Warning: Significant class imbalance detected.")



