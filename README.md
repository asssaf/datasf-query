# SF Property Data MCP Server

This project provides a Model Context Protocol (MCP) server for querying San Francisco property data via the SF Data API (Socrata). It is designed to be deployed as a Cloudflare Worker and can be consumed by any MCP-compliant client (e.g., Claude Desktop, Cursor, or the Cloudflare AI Playground).

## Features
- **Query Tool**: Execute complex property searches with filters for roll year, bedrooms, bathrooms, districts, neighborhood codes, and more.
- **Target Comparison**: Provide a `target_parcel_number` to calculate relative distances and property area/value ratios.
- **Modern Stack**: Built with TypeScript 6, Zod 4, and Cloudflare Workers (using the `agents` library).
- **Streamable HTTP**: Uses the latest MCP Streamable HTTP transport for robust remote communication.

## Getting Started

### Prerequisites
- Node.js and npm installed.
- (Optional) [Wrangler](https://developers.cloudflare.com/workers/wrangler/install-and-update/) for deployment.

### Installation
```bash
npm install --legacy-peer-deps
```
*Note: `--legacy-peer-deps` is required to resolve version conflicts between Zod and other dependencies.*

### Local Development
To run the server locally for testing:
```bash
npm start
```
By default, the MCP endpoint will be available at `http://localhost:8787/mcp`.

### Deployment
To deploy your MCP server to Cloudflare Workers:
```bash
npm run deploy
```
Once deployed, your server will be available at `https://<your-worker-name>.<your-subdomain>.workers.dev/mcp`.

## MCP Configuration

To connect this server to an MCP client like Claude Desktop, add the following to your MCP configuration:

```json
{
  "mcpServers": {
    "sf-property-data": {
      "command": "npx",
      "args": [
        "mcp-remote",
        "https://<your-worker-name>.<your-subdomain>.workers.dev/mcp"
      ]
    }
  }
}
```

## Project Structure
- `src/index.ts`: Entry point, defines the MCP server and `SFPropertyMCP` agent.
- `src/apiClient.ts`: Socrata API communication layer.
- `src/queryBuilder.ts`: SoQL (Socrata Query Language) construction logic.
- `wrangler.jsonc`: Cloudflare Worker configuration.

## License
MIT
