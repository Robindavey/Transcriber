#!/bin/bash

MODEL="qwen2.5:14b"
UNMPARSEDTEXT="raw_text/raw_text.txt"

PODCAST="podcastscripts/script.txt"
cat prompts/podcast-script.txt $UNMPARSEDTEXT | \
ollama run $MODEL --temperature 0 --keepalive 0 > $PODCAST
echo "Done. Ollama unloaded."
