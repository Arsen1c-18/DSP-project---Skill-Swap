import os

# Create project directories
dirs = [
    'data',
    'modules',
    'templates',
    'static',
    'static/css',
    'static/js'
]

for d in dirs:
    os.makedirs(d, exist_ok=True)
    print(f"✓ Created: {d}")

print("\n✓ Project structure ready!")
