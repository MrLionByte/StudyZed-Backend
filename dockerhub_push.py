import subprocess

#Add Your docker-hub username
DOCKER_USER = "mrlionbyte" 

#add image with image id as key and service name as value 
IMAGES = {
    "eee0bcd942df": "session_and_task_management",
    "9fdb94dc0c2f": "payment_management",
    "e3b741605588": "messages_management"
}

print("Logging in to Docker Hub...")
subprocess.run(["docker", "login", "-u", DOCKER_USER], check=True)

# 1st Approach
# tag_version = ["v1.2.0","v1.0.0","v1.2.0"]
# 2nd Approach
  = "v1.2.0"

# If 1st approach is being used use this for correct tagging with index
tag_index = 0


for image_id, repo_name in IMAGES.items():
    # tag = f"{DOCKER_USER}/{repo_name}:{tag_version[tag_index]}"
    tag = f"{DOCKER_USER}/{repo_name}:{tag_version}"
    
    # tag_index += 1
    
    print(f"Tagging image {image_id} as {tag}...")
    subprocess.run(["docker", "tag", image_id, tag], check=True)
    
    print(f"Pushing {tag} to Docker Hub...")
    subprocess.run(["docker", "push", tag], check=True)

print("All images have been pushed to Docker Hub!")
