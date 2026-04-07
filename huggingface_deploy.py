import os
from huggingface_hub import HfApi, create_repo

# --- CONFIGURATION ---
# Users should set these environment variables or fill them in below
HF_TOKEN = os.environ.get("HF_TOKEN")
REPO_ID = os.environ.get("REPO_ID") # Format: "username/space-name"

def deploy():
    if not HF_TOKEN or not REPO_ID:
        print("ERROR: HF_TOKEN and REPO_ID environment variables must be set.")
        print("Example Usage:")
        print('  $env:HF_TOKEN="your_token_here"')
        print('  $env:REPO_ID="username/food-safety-dashboard"')
        print('  python huggingface_deploy.py')
        return

    api = HfApi()

    try:
        # 1. Create the Space (Docker SDK)
        print(f"Creating/Updating Space: {REPO_ID}...")
        create_repo(
            repo_id=REPO_ID,
            token=HF_TOKEN,
            repo_type="space",
            space_sdk="docker",
            exist_ok=True
        )

        # 2. Upload all files
        # We upload everything in the current directory, respecting .gitignore (manually filtered)
        print("Uploading files to Hugging Face...")
        api.upload_folder(
            folder_path=".",
            repo_id=REPO_ID,
            repo_type="space",
            token=HF_TOKEN,
            ignore_patterns=[".git/", "__pycache__/", "*.pyc", ".env"]
        )

        print("\n" + "="*40)
        print("SUCCESS! Deployment initiated.")
        print(f"Space URL: https://huggingface.co/spaces/{REPO_ID}")
        print("="*40)
        print("You can monitor the build status at the URL above.")

    except Exception as e:
        print(f"Deployment failed: {e}")

if __name__ == "__main__":
    deploy()
