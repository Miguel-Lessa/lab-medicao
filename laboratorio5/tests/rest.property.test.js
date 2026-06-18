import { afterAll, beforeAll, describe, expect, test } from "vitest";
import fc from "fast-check";
import request from "supertest";
import { buildDatabase, STAT_FIELDS } from "../src/database.js";
import { createApp } from "../src/server.js";

describe("REST API properties", () => {
  const db = buildDatabase();
  let app;
  let apolloServer;

  beforeAll(async () => {
    const created = await createApp(db);
    app = created.app;
    apolloServer = created.apolloServer;
  });

  test("Feature: graphql-vs-rest-experiment, Property 3: REST retorna o Jogador completo para identificador existente", async () => {
    await fc.assert(
      fc.asyncProperty(fc.integer({ min: 1, max: db.players.length }), async (id) => {
        const response = await request(app).get(`/rest/players/${id}`).expect(200);
        const player = db.players[id - 1];

        expect(response.body.id).toBe(player.id);
        expect(response.body.nome).toBe(player.nome);
        for (const field of STAT_FIELDS) {
          expect(response.body[field]).toBe(player[field]);
        }
      }),
      { numRuns: 100 }
    );
  });

  test("Feature: graphql-vs-rest-experiment, Property 4: REST sinaliza erro sem dados de Jogador para identificadores nao atendiveis", async () => {
    await fc.assert(
      fc.asyncProperty(
        fc.oneof(
          fc.integer({ min: db.players.length + 1, max: db.players.length + 1000 }).map(String),
          fc.string().filter((value) => value.length > 0 && !value.includes("/") && !/^[1-9]\d*$/.test(value))
        ),
        async (rawId) => {
          const response = await request(app).get(`/rest/players/${encodeURIComponent(rawId)}`);
          const numeric = /^[1-9]\d*$/.test(rawId);
          expect(response.status).toBe(numeric ? 404 : 400);
          expect(response.body.error).toBeTruthy();
          expect(response.body.nome).toBeUndefined();
          expect(response.body.gols).toBeUndefined();
        }
      ),
      { numRuns: 100 }
    );
  });

  test("respostas REST usam JSON em sucesso e erro", async () => {
    await request(app).get("/rest/players/1").expect("Content-Type", /json/).expect(200);
    await request(app).get("/rest/players/abc").expect("Content-Type", /json/).expect(400);
  });

  afterAll(async () => {
    await apolloServer.stop();
  });
});
