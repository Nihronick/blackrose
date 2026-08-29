#!/usr/bin/env bash
# ==============================================================================
# BlackRose Database Automated Backup Script
# Dumps PostgreSQL database from Neon.tech, compresses with gzip,
# and pushes to Hugging Face Datasets or local storage.
# ==============================================================================

set -euo pipefail

BACKUP_DIR="${BACKUP_DIR:-./backups}"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
FILENAME="blackrose_backup_${TIMESTAMP}.sql.gz"
FILEPATH="${BACKUP_DIR}/${FILENAME}"

mkdir -p "${BACKUP_DIR}"

if [ -z "${DATABASE_URL:-}" ]; then
  echo "❌ Error: DATABASE_URL environment variable is required."
  exit 1
fi

echo "🚀 Starting database backup for BlackRose..."
echo "📦 Output file: ${FILEPATH}"

# Dump and compress
pg_dump "${DATABASE_URL}" \
  --no-owner \
  --no-acl \
  --clean \
  --if-exists \
  | gzip -9 > "${FILEPATH}"

FILESIZE=$(du -h "${FILEPATH}" | cut -f1)
echo "✅ Database dump completed successfully (${FILESIZE})."

# Optional: Upload to Hugging Face Datasets if HF_TOKEN is present
if [ -n "${HF_TOKEN:-}" ] && [ -n "${HF_DATASET_REPO:-}" ]; then
  echo "📤 Uploading backup to Hugging Face Dataset: ${HF_DATASET_REPO}..."
  python3 -c "
import os
from huggingface_hub import HfApi
api = HfApi(token=os.environ['HF_TOKEN'])
api.upload_file(
    path_or_fileobj='${FILEPATH}',
    path_in_repo='backups/${FILENAME}',
    repo_id=os.environ['HF_DATASET_REPO'],
    repo_type='dataset',
)
print('✅ Uploaded to HF Datasets!')
"
fi

echo "🎉 Backup process finished."
