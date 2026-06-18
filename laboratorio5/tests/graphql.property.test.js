import { afterAll, beforeAll, describe, expect, test } from "vitest";
import fc from "fast-check";
import { buildDatabase, STAT_FIELDS } from "../src/database.js";
import { createApolloServer } from "../src/graphqlApi.js";

const selectableFields = ["id", "nome", ...STAT_FIELDS];

describe("GraphQL API properties", () => {
  const db = buildDatabase();
  const apolloServer = createApolloServer(db);

  beforeAll(async () => {
    await apolloServer.start();
  });

  test("Feature: graphql-vs-rest-experiment, Property 5: GraphQL retorna exclusivamente os campos solicitados", async () => {
    await fc.assert(
      fc.asyncProperty(
        fc.integer({ min: 1, max: db.players.length }),
        fc.subarray(selectableFields, { minLength: 1 }),
        async (id, fields) => {
          const query = `query($id: Int!) { player(id: $id) { ${fields.join(" ")} } }`;
          const response = await apolloServer.executeOperation({ query, variables: { id } });
          expect(response.body.kind).toBe("single");
          expect(response.body.singleResult.errors).toBeUndefined();
          expect(Object.keys(response.body.singleResult.data.player).sort()).toEqual([...fields].sort());
        }
      ),
      { numRuns: 100 }
    );
  });

  test("Feature: graphql-vs-rest-experiment, Property 6: GraphQL retorna Jogador nulo e erro para identificador inexistente", async () => {
    await fc.assert(
      fc.asyncProperty(
        fc.integer({ min: db.players.length + 1, max: db.players.length + 1000 }),
        async (id) => {
          const response = await apolloServer.executeOperation({
            query: "query($id: Int!) { player(id: $id) { nome gols } }",
            variables: { id }
          });
          expect(response.body.kind).toBe("single");
          expect(response.body.singleResult.data.player).toBeNull();
          expect(response.body.singleResult.errors[0].message).toContain("jogador nao encontrado");
        }
      ),
      { numRuns: 100 }
    );
  });

  test("consulta nome e gols retorna exatamente esses campos", async () => {
    const response = await apolloServer.executeOperation({
      query: "query($id: Int!) { player(id: $id) { nome gols } }",
      variables: { id: 1 }
    });
    expect(Object.keys(response.body.singleResult.data.player).sort()).toEqual(["gols", "nome"]);
  });

  test("schema contem entidades e consulta player(id)", async () => {
    const response = await apolloServer.executeOperation({
      query: `{
        __schema {
          queryType { fields { name args { name type { kind name ofType { name kind } } } } }
          types { name fields { name } }
        }
      }`
    });
    const types = response.body.singleResult.data.__schema.types;
    const playerType = types.find((type) => type.name === "Player");
    const queryType = response.body.singleResult.data.__schema.queryType;

    expect(types.map((type) => type.name)).toEqual(expect.arrayContaining(["League", "Team", "Player"]));
    expect(playerType.fields.map((field) => field.name)).toEqual(
      expect.arrayContaining(["id", "nome", "gols", "assistencias", "cartoesAmarelos", "cartoesVermelhos"])
    );
    expect(playerType.fields.length).toBeGreaterThanOrEqual(12);
    expect(queryType.fields.some((field) => field.name === "player" && field.args[0].name === "id")).toBe(true);
  });

  afterAll(async () => {
    await apolloServer.stop();
  });
});
