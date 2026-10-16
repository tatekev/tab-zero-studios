# Unpack

Turns a confusing letter or bill into: what it is, what to do, and by when.

Part of **Tab Zero Studio** — *Tools for Atypical Thinkers, Everywhere.*

## Run
```
pip install -r ../requirements.txt
python server.py        # MCP server over stdio
python -m pytest -q     # tests
```
MCP client config: `{"command":"python","args":["server.py"],"cwd":"unpack"}`

## Tools
- `unpack_letter(text)`: structured result (what, actions, deadline, urgency, first tiny step)
- `unpack_letter_markdown(text)`: short brain-friendly card

## Privacy and limits
Runs fully offline. Stores nothing and sends nothing. Use sample or pasted text only; never full SSNs or card numbers. Not legal, tax, or financial advice.
