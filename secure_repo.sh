echo "====================================================="
echo " 🛡️ PURGING SENSITIVE FILES FROM GIT HISTORY & LOCAL SETUP"
echo "====================================================="

# 1. Ensure we are in the repo root
cd /home/LavetoLab

# 2. Update .gitignore to permanently ignore sensitive files
cat << 'GITIGNORE' >> .gitignore
google_key.json
credentials.json
.env
*.json
*.env
GITIGNORE

# 3. Completely remove sensitive files from Git index (if tracked)
git rm --cached --ignore-unmatch google_key.json credentials.json .env 2>/dev/null

# 4. Purge sensitive files from all historical git commits
echo "Scrubbing Git history across all commits..."
git filter-branch --force --index-filter \
  "git rm --cached --ignore-unmatch google_key.json credentials.json .env" \
  --prune-empty --tag-name-filter cat -- --all

# 5. Clean up git reflogs and garbage collect to shrink repo and purge objects
echo "Cleaning git object database..."
rm -rf .git/refs/original/
git reflog expire --expire=now --all
git gc --prune=now --aggressive

echo "✓ Git history successfully purged of exposed credentials."
echo "====================================================="
