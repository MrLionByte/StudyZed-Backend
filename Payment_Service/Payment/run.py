import subprocess
import sys
import time

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
        server_process = subprocess.run(
            ["python", "manage.py", "runserver", "0.0.0.0:8008"],
            check=True
        )
        
        time.sleep(5)
        
        print("Starting Consuming messages...")
        consumer_process = subprocess.run(
            ["python", "manage.py", "consume_messages"],
            stdout=sys.stdout,
            stderr=sys.stderr
        )
        
        server_process.wait()
        consumer_process.wait()
        
    except subprocess.CalledProcessError as e:
        print(f"Error running : {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()