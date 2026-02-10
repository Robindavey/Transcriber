#!/bin/bash

MODEL="llama2:7b"
UNMPARSEDTEXT="raw_text/raw_text.txt"

PODCAST="podcastscripts/script.txt"
cat prompts/podcast-script.txt $UNMPARSEDTEXT | \
ollama run $MODEL  --keepalive 0 > $PODCAST
echo "Done. Ollama unloaded."
