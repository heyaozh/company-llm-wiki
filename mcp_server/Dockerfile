# MCP server for the CCPRM wiki — deploy to Cloud Run.
FROM python:3.11-slim

WORKDIR /app

# Tools needed by the write path (propose_document opens PRs).
RUN apt-get update && apt-get install -y --no-install-recommends git \
    && rm -rf /var/lib/apt/lists/*

COPY mcp_server/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# The wiki content is mounted/cloned at runtime into /data; WIKI_ROOT points to it.
COPY mcp_server/ ./mcp_server/
COPY tools/ ./tools/

ENV MCP_TRANSPORT=sse \
    WIKI_ROOT=/data/company-llm-wiki \
    PORT=8080

# On start, clone/refresh the wiki, then run the server.
CMD ["sh", "-c", "git clone --depth 1 \"$WIKI_REPO_URL\" \"$WIKI_ROOT\" 2>/dev/null || git -C \"$WIKI_ROOT\" pull; python mcp_server/server.py"]
