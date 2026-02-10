#!/bin/bash

MODEL="llama2:7b"
UNMPARSEDTEXT="raw_text/raw_text.txt"
FULLDOC="GoodFiles/fullNotes.txt"
NOTES="GoodFiles/ShortendNotes.txt"
PODCAST="podcastscripts/script.txt"
cat prompts/reconstruction_prompt.txt $UNMPARSEDTEXT | \
ollama run $MODEL --keepalive 0 > $FULLDOC

cat prompts/notes_prompt.txt $UNMPARSEDTEXT | \
ollama run $MODEL --keepalive 0 > $NOTES

echo "Done. Ollama unloaded."
