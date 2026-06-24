# MCP server for the CCPRM wiki — a self-contained container for the platform's MCP slot.
# Lives at the repo root so the build context IS the repo (the wiki content gets baked in).
# Build:  docker build -t ccprm-wiki-mcp .
FROM python:3.11-slim

WORKDIR /app

COPY mcp_server/requirements.txt mcp_server/requirements.txt
RUN pip install --no-cache-dir -r mcp_server/requirements.txt

# Bake the wiki content + server into the image (POC snapshot — rebuild to refresh content).
COPY . .

ENV WIKI_ROOT=/app \
    MCP_TRANSPORT=streamable-http \
    MCP_READONLY=1 \
    PORT=8080

EXPOSE 8080
CMD ["python", "mcp_server/server.py"]
