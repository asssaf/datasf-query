export interface APIResponse {
  [key: string]: any;
}

export class APIClient {
  private static readonly DEFAULT_BASE_URL = "https://data.sfgov.org";
  private static readonly DEFAULT_ENDPOINT = "/resource/wv5m-vpq2.json";

  private baseUrl: string;
  private defaultEndpoint: string;

  constructor(baseUrl?: string, defaultEndpoint?: string) {
    this.baseUrl = (baseUrl || APIClient.DEFAULT_BASE_URL).replace(/\/$/, "");
    this.defaultEndpoint = defaultEndpoint || APIClient.DEFAULT_ENDPOINT;
  }

  async get(endpoint?: string, params?: Record<string, string>): Promise<Response> {
    const targetEndpoint = endpoint || this.defaultEndpoint;
    const url = new URL(`${this.baseUrl}/${targetEndpoint.replace(/^\//, "")}`);

    if (params) {
      for (const [key, value] of Object.entries(params)) {
        url.searchParams.append(key, value);
      }
    }

    const response = await fetch(url.toString(), {
      headers: {
        "Accept": "application/json"
      }
    });

    if (!response.ok) {
      const errorText = await response.text();
      throw new Error(`API Request failed with status ${response.status}: ${errorText}`);
    }

    return response;
  }
}
