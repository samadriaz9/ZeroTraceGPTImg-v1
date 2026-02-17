#!/bin/bash
if [ -f CHATGPT_INTEGRATION.md ]; then
    sed -i 's/sk-proj[^`]*/YOUR_API_KEY_HERE/g' CHATGPT_INTEGRATION.md
fi
