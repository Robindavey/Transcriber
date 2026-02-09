#!/bin/bash

MODEL="llama2:7b"
UNMPARSEDTEXT="raw_text/raw_text.txt"
FULLDOC="GoodFiles/fullNotes.txt"
NOTES="GoodFiles/ShortendNotes.txt"
PODCAST="podcastscripts/script.txt"
cat prompts/reconstruct_prompt.txt $UNMPARSEDTEXT | \
ollama run $MODEL --temperature 0 --keepalive 0 > $FULLDOC

cat prompts/notes_prompt.txt $UNMPARSEDTEXT | \
ollama run $MODEL --temperature 0 --keepalive 0 > $NOTES

cat prompts/podcast-script.txt $UNMPARSEDTEXT | \
ollama run $MODEL --temperature 0 --keepalive 0 > $PODCAST
echo "Done. Ollama unloaded."
