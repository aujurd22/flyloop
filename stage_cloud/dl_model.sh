#!/bin/bash
# pre-download the MiniLM model via hf-mirror, then verify
export HF_ENDPOINT=https://hf-mirror.com
/root/miniconda3/bin/python - << 'EOF'
from sentence_transformers import SentenceTransformer
m = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
print("MODEL_READY", m.get_sentence_embedding_dimension())
EOF
echo "DL_RC=$?"
