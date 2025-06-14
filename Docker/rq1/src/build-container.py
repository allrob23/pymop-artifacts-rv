import subprocess

try:
    subprocess.run(["docker", "build", "-t", "denini/pymop-experiment", "."], check=True)
except subprocess.CalledProcessError as e:
    print(f"Error building Docker image: {e}")
