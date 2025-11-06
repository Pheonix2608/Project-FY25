import subprocess
import os

# ===== CONFIG =====
REMOTE_URL = "https://github.com/Pheonix2608/Project-FY25.git"
BRANCH = "main"  # or 'dev', 'feature/chatbot-ui'
COMMIT_MESSAGE = "Auto-sync from Python script"
# ==================

def run(cmd):
    """Run shell command safely and print output."""
    print(f"🧩 Running: {cmd}")
    result = subprocess.run(cmd, shell=True, text=True, capture_output=True)
    if result.stdout:
        print(result.stdout.strip())
    if result.stderr:
        print(result.stderr.strip())
    return result.returncode

def git_push_existing_branch():
    # 1️⃣ Initialize repo
    if not os.path.exists(".git"):
        print("🚀 Initializing new git repository...")
        run("git init")
    else:
        print("✅ Git repo already initialized.")

    # 2️⃣ Add remote if not exists
    remotes = subprocess.run("git remote", shell=True, text=True, capture_output=True).stdout.strip()
    if "origin" not in remotes:
        print("📦 Adding remote origin...")
        run(f"git remote add origin {REMOTE_URL}")
    else:
        print("✅ Remote 'origin' already exists.")

    # 3️⃣ Set branch
    print(f"🧭 Setting current branch to '{BRANCH}'...")
    run(f"git branch -M {BRANCH}")

    # 4️⃣ Fetch and pull
    print(f"📥 Fetching from origin/{BRANCH}...")
    run(f"git fetch origin {BRANCH}")
    print(f"📥 Pulling latest changes (if any)...")
    run(f"git pull origin {BRANCH} --allow-unrelated-histories")

    # 5️⃣ Add, commit, push
    print("🧹 Staging all changes...")
    run("git add .")

    print("📝 Committing changes...")
    commit_status = run(f'git commit -m "{COMMIT_MESSAGE}"')
    if commit_status != 0:
        print("✅ Nothing new to commit, continuing...")

    print(f"🚢 Pushing changes to '{BRANCH}'...")
    run(f"git push -u origin {BRANCH}")

    print("🎉 Done! Local repo synced with remote successfully.")

if __name__ == "__main__":
    git_push_existing_branch()
