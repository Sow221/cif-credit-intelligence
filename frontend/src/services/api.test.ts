import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { ApiError, api, clearToken, getToken, request, setToken } from "./api";
import { API_BASE_URL } from "@/utils/constants";

function jsonResponse(body: unknown, status = 200): Response {
  return {
    ok: status >= 200 && status < 300,
    status,
    json: async () => body,
  } as unknown as Response;
}

const emptyResponse: Response = { ok: true, status: 204 } as unknown as Response;

describe("token helpers", () => {
  beforeEach(() => localStorage.clear());

  it("round-trips the access token", () => {
    expect(getToken()).toBeNull();
    setToken("jwt-123");
    expect(getToken()).toBe("jwt-123");
    clearToken();
    expect(getToken()).toBeNull();
  });
});

describe("request", () => {
  const fetchMock = vi.fn();

  beforeEach(() => {
    localStorage.clear();
    fetchMock.mockReset();
    vi.stubGlobal("fetch", fetchMock);
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("performs a GET against the API base url", async () => {
    fetchMock.mockResolvedValue(jsonResponse({ ok: true }, 200));
    const result = await request<{ ok: boolean }>("/health");
    expect(result.ok).toBe(true);
    const [url, init] = fetchMock.mock.calls[0] as [string, RequestInit];
    expect(url).toBe(`${API_BASE_URL}/health`);
    expect(init.method).toBe("GET");
    expect(init.headers).toEqual({ Accept: "application/json" });
  });

  it("adds the bearer token from storage", async () => {
    setToken("tok");
    fetchMock.mockResolvedValue(jsonResponse({}, 200));
    await request("/x");
    const [, init] = fetchMock.mock.calls[0] as [string, RequestInit];
    const headers = init.headers as Record<string, string>;
    expect(headers.Authorization).toBe("Bearer tok");
  });

  it("serializes body and sets content type", async () => {
    fetchMock.mockResolvedValue(jsonResponse({}, 200));
    await request("/x", { method: "POST", body: { a: 1 } });
    const [, init] = fetchMock.mock.calls[0] as [string, RequestInit];
    const headers = init.headers as Record<string, string>;
    expect(headers["Content-Type"]).toBe("application/json");
    expect(init.body).toBe(JSON.stringify({ a: 1 }));
  });

  it("forwards custom headers and idempotency key", async () => {
    fetchMock.mockResolvedValue(jsonResponse({}, 200));
    await request("/x", { headers: { "X-Custom": "v" }, idempotencyKey: "key-1" });
    const [, init] = fetchMock.mock.calls[0] as [string, RequestInit];
    const headers = init.headers as Record<string, string>;
    expect(headers["X-Custom"]).toBe("v");
    expect(headers["Idempotency-Key"]).toBe("key-1");
  });

  it("returns undefined for 204 responses", async () => {
    fetchMock.mockResolvedValue(emptyResponse);
    const result = await request("/x");
    expect(result).toBeUndefined();
  });

  it("throws ApiError with error envelope", async () => {
    fetchMock.mockResolvedValue(
      jsonResponse({ error: { code: "TOKEN_EXPIRED", message: "Session expired" } }, 401),
    );
    await expect(request("/x")).rejects.toMatchObject({
      name: "ApiError",
      status: 401,
      code: "TOKEN_EXPIRED",
      message: "Session expired",
      details: undefined,
    });
  });

  it("parses pydantic-style detail messages", async () => {
    fetchMock.mockResolvedValue(jsonResponse({ detail: "Not found" }, 404));
    await expect(request("/missing")).rejects.toMatchObject({
      code: "HTTP_404",
      message: "Not found",
    });
  });

  it("parses message-style errors", async () => {
    fetchMock.mockResolvedValue(jsonResponse({ message: "Broken" }, 400));
    await expect(request("/x")).rejects.toMatchObject({ message: "Broken" });
  });

  it("keeps defaults when the body is not JSON", async () => {
    fetchMock.mockResolvedValue({
      ok: false,
      status: 502,
      json: async () => {
        throw new Error("invalid json");
      },
    } as unknown as Response);
    await expect(request("/x")).rejects.toMatchObject({
      code: "HTTP_502",
      message: "Request failed with status 502",
    });
  });
});

describe("api helpers", () => {
  const fetchMock = vi.fn();

  beforeEach(() => {
    fetchMock.mockReset();
    vi.stubGlobal("fetch", fetchMock);
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("api.get", async () => {
    fetchMock.mockResolvedValue(jsonResponse({ n: 1 }, 200));
    await expect(api.get<{ n: number }>("/clients")).resolves.toEqual({ n: 1 });
  });

  it("api.post", async () => {
    fetchMock.mockResolvedValue(jsonResponse({ id: "a" }, 201));
    await expect(
      api.post<{ id: string }>("/clients", { name: "x" }, { idempotencyKey: "k" }),
    ).resolves.toEqual({ id: "a" });
  });

  it("api.patch", async () => {
    fetchMock.mockResolvedValue(jsonResponse({ ok: true }, 200));
    await expect(api.patch("/clients/c1", { status: "x" })).resolves.toEqual({ ok: true });
  });

  it("api.delete", async () => {
    fetchMock.mockResolvedValue(jsonResponse({}, 200));
    await expect(api.delete("/clients/c1")).resolves.toEqual({});
  });
});

describe("ApiError", () => {
  it("exposes status, code and details", () => {
    const err = new ApiError(500, "SERVER_ERROR", "boom", { extra: 1 });
    expect(err).toBeInstanceOf(Error);
    expect(err.status).toBe(500);
    expect(err.code).toBe("SERVER_ERROR");
    expect(err.details).toEqual({ extra: 1 });
    expect(err.name).toBe("ApiError");
  });
});
