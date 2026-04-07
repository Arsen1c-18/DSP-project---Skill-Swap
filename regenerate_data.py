import subprocess
import sys

print("Regenerating data with expanded skill set...")
print("=" * 60)

try:
    result = subprocess.run([sys.executable, 'setup_project.py'], 
                          capture_output=True, 
                          text=True, 
                          check=True)
    print(result.stdout)
    print("\n✅ Data regeneration complete!")
except subprocess.CalledProcessError as e:
    print(f"Error: {e.stderr}")
    print("\nPlease run manually: python setup_project.py")
