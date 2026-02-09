#!/bin/bash

MODEL="llama2:7b"
UNMPARSEDTEXT="raw_text/raw_text.txt"
FULLDOC="GoodFiles/fullNotes.txt"
NOTES="GoodFiles/ShortendNotes.txt"
cat prompts/reconstruct_prompt.txt $UNMPARSEDTEXT | \
ollama run $MODEL --temperature 0 --keepalive 0 > $FULLDOC

cat prompts/notes_prompt.txt $UNMPARSEDTEXT | \
ollama run $MODEL --temperature 0 --keepalive 0 > $NOTES

echo "Done. Ollama unloaded."
