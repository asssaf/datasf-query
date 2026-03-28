import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { createMcpHandler } from "agents/mcp";
import { z } from "zod";
import { APIClient } from "./apiClient.js";
import {
  buildOrderByClause,
  buildSelectClause,
  buildWhereClause,
  QueryParams
} from "./queryBuilder.js";

const QuerySchema = z.object({
  roll_year: z.string().optional().describe("Filter by closed roll year (e.g., 2021)."),
  bedrooms: z.union([z.number(), z.string()]).optional().describe("Filter by number of bedrooms (e.g., 0, 1, 2)."),
  bathrooms: z.union([z.number(), z.string()]).optional().describe("Filter by number of bathrooms (e.g., 1, 1.5, 2)."),
  parcel_number: z.string().optional().describe("Filter by parcel number (e.g., 3776182)."),
  target_parcel_number: z.string().optional().describe("Compare results to this parcel number."),
  target_roll_year: z.string().optional().describe("Closed roll year for the target parcel."),
  area_min: z.union([z.number(), z.string()]).optional().describe("Minimum property area in square feet."),
  area_max: z.union([z.number(), z.string()]).optional().describe("Maximum property area in square feet."),
  date_start: z.string().optional().describe("Filter by sales date (YYYY-MM-DD) - Start."),
  date_end: z.string().optional().describe("Filter by sales date (YYYY-MM-DD) - End."),
  district: z.union([z.string(), z.array(z.string())]).optional().describe("Filter by assessor neighborhood district number."),
  neighborhood_code: z.union([z.string(), z.array(z.string())]).optional().describe("Filter by assessor neighborhood code (e.g., 9K)."),
  property_class_code: z.union([z.string(), z.array(z.string())]).optional().describe("Filter by property class code (e.g., D, E)."),
  fields: z.array(z.string()).optional().describe("Select specific fields to return."),
  limit: z.number().default(100).describe("Limit the number of results (default: 100)."),
  offset: z.number().default(0).describe("Offset the results (default: 0)."),
});

function createServer() {
  const server = new McpServer({
    name: "sf-property-data",
    version: "1.0.0",
  });

  server.tool(
    "query",
    "Execute a specialized property query against the SF Data API.",
    QuerySchema.shape,
    async (args) => {
      const client = new APIClient();
      const endpoint = "/resource/wv5m-vpq2.json";

      let targetPoint: [number, number] | null = null;
      let targetArea: number | null = null;
      let targetTotalAssessedValue: number | null = null;

      if (args.target_parcel_number) {
        if (!args.target_roll_year) {
          throw new Error("When target_parcel_number is provided, target_roll_year must also be specified.");
        }

        const lookupWhere = `parcel_number = '${args.target_parcel_number}' AND closed_roll_year = '${args.target_roll_year}'`;
        const lookupFields = "the_geom, property_area, assessed_improvement_value, assessed_land_value, assessed_fixtures_value";
        const lookupQuery = `SELECT ${lookupFields} WHERE ${lookupWhere} LIMIT 1`;

        const resp = await client.get(endpoint, { $query: lookupQuery });
        const data = await resp.json() as any[];

        if (!data || data.length === 0) {
          throw new Error(`Target parcel '${args.target_parcel_number}' not found.`);
        }

        const targetData = data[0];
        if (targetData.the_geom && targetData.the_geom.coordinates) {
          targetPoint = targetData.the_geom.coordinates;
        }

        if (targetData.property_area !== undefined) {
          targetArea = parseFloat(targetData.property_area);
          if (targetArea === 0) targetArea = null;
        }

        const toFloat = (val: any) => (val !== undefined && val !== null ? parseFloat(val) : 0);
        const improvement = toFloat(targetData.assessed_improvement_value);
        const land = toFloat(targetData.assessed_land_value);
        const fixtures = toFloat(targetData.assessed_fixtures_value);
        targetTotalAssessedValue = improvement + land + fixtures;
        if (targetTotalAssessedValue === 0) targetTotalAssessedValue = null;
      }

      const queryParams: QueryParams = {
        roll_year: args.roll_year,
        bedrooms: args.bedrooms,
        bathrooms: args.bathrooms,
        parcel_number: args.parcel_number,
        area_min: args.area_min,
        area_max: args.area_max,
        date_start: args.date_start,
        date_end: args.date_end,
        district: args.district,
        neighborhood_code: args.neighborhood_code,
        property_class_code: args.property_class_code,
      };

      const selectClause = buildSelectClause(targetPoint, targetArea, targetTotalAssessedValue, args.fields);
      const whereClause = buildWhereClause(queryParams);
      const orderByClause = buildOrderByClause(targetPoint, targetArea);

      let soqlQuery = `SELECT ${selectClause}`;
      if (whereClause) {
        soqlQuery += ` WHERE ${whereClause}`;
      }
      if (orderByClause) {
        soqlQuery += ` ORDER BY ${orderByClause}`;
      }
      soqlQuery += ` LIMIT ${args.limit} OFFSET ${args.offset}`;

      const response = await client.get(endpoint, { $query: soqlQuery });
      const results = await response.json();

      return {
        content: [{ type: "text", text: JSON.stringify(results, null, 2) }],
      };
    }
  );

  return server;
}

export default {
  async fetch(request: Request, env: any, ctx: any): Promise<Response> {
    const server = createServer();
    return createMcpHandler(server)(request, env, ctx);
  },
};
