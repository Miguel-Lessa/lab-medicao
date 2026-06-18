import { afterEach, describe, expect, test, vi } from "vitest";
import { startServer } from "../src/server.js";

describe("unified server integration", () => {
  const started = [];

  afterEach(async () => {
    while (started.length) {
      const current = started.pop();
      await new Promise((resolve) => current.server.close(resolve));
      await current.apolloServer.stop();
    }
    vi.restoreAllMocks();
  });

  test("health check REST e GraphQL, CORS e log de disponibilidade", async () => {
    const logSpy = vi.spyOn(console, "log").mockImplementation(() => {});
    const instance = await startServer(0, { exitOnError: false });
    started.push(instance);
    const baseUrl = `http://127.0.0.1:${instance.port}`;

    const rest = await fetch(`${baseUrl}/rest/players/1`, { headers: { Origin: "http://localhost" } });
    const graphql = await fetch(`${baseUrl}/graphql`, {
      method: "POST",
      headers: { "Content-Type": "application/json", Origin: "http://localhost" },
      body: JSON.stringify({ query: "query($id: Int!) { player(id: $id) { nome gols } }", variables: { id: 1 } })
    });
    const graphqlBody = await graphql.json();

    expect(rest.status).toBe(200);
    expect(rest.headers.get("access-control-allow-origin")).toBe("*");
    expect(graphql.status).toBe(200);
    expect(graphql.headers.get("access-control-allow-origin")).toBe("*");
    expect(graphqlBody.errors).toBeUndefined();
    expect(logSpy).toHaveBeenCalledWith(expect.stringContaining("Servidor API disponivel na porta"));
  });

  test("porta ocupada gera erro descritivo", async () => {
    vi.spyOn(console, "log").mockImplementation(() => {});
    const errorSpy = vi.spyOn(console, "error").mockImplementation(() => {});
    const instance = await startServer(0, { exitOnError: false });
    started.push(instance);

    await expect(startServer(instance.port, { exitOnError: false })).rejects.toMatchObject({ code: "EADDRINUSE" });
    expect(errorSpy).toHaveBeenCalledWith(expect.stringContaining(`Porta ${instance.port} ja esta em uso`));
  });
});
