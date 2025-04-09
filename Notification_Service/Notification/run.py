import subprocess
import sys

def main():
    try:
        # Run migrations
        print("Running migrations...")
        subprocess.run(
            ["python", "manage.py", "migrate"],
            check=True,
            capture_output=True,
            text=True
        )
        
        # Start server
        print("Starting Django development server...")
        subprocess.run(
            ["python", "manage.py", "runserver", "0.0.0.0:8007"],
            check=True
        )
        
    except subprocess.CalledProcessError as e:
        print(f"Error running migrations: {e.stderr}")
        sys.exit(1)

if __name__ == "__main__":
    main()