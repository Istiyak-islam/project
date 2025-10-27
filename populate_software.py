import json
from app import db, Software

# Load config.json
with open('config.json', 'r') as f:
    data = json.load(f)

softwares = data.get('softwares', [])

for s in softwares:
    # Check if software already exists
    existing = Software.query.filter_by(name=s['name']).first()
    if existing:
        continue

    software = Software(
        name=s['name'],
        path_windows=s.get('path_windows'),
        cmd=s.get('cmd'),
        type=s.get('type'),
        url=s.get('url')
    )
    db.session.add(software)

db.session.commit()
print("Software table populated successfully!")
