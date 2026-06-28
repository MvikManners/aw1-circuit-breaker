import tarfile, os

def create_full_snapshot():
    snapshot_name = "LAVETO_DESIGN_SNAPSHOT.tar.gz"
    # Directories/Files that define your OS DNA
    sources = ['templates', 'static', 'core', 'app.py', '.env', 'vault_sync.py']
    
    with tarfile.open(snapshot_name, "w:gz") as tar:
        for source in sources:
            if os.path.exists(source):
                tar.add(source)
    print(f"✅ Design snapshot secured: {snapshot_name}")

if __name__ == "__main__":
    create_full_snapshot()
