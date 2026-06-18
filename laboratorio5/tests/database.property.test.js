import { describe, expect, test } from "vitest";
import fc from "fast-check";
import { STAT_FIELDS, buildDatabase } from "../src/database.js";

describe("database properties", () => {
  test("Feature: graphql-vs-rest-experiment, Property 1: Integridade estrutural da base de dados", () => {
    fc.assert(
      fc.property(fc.integer({ min: 50, max: 90 }), (playerCount) => {
        const db = buildDatabase(playerCount);
        const leagueIds = new Set(db.leagues.map((league) => league.id));
        const teamIds = new Set(db.teams.map((team) => team.id));
        const playerIds = db.players.map((player) => player.id);

        expect(db.leagues.length).toBeGreaterThanOrEqual(2);
        expect(db.teams.length).toBeGreaterThanOrEqual(5);
        expect(db.players.length).toBeGreaterThanOrEqual(50);
        expect(db.teams.every((team) => leagueIds.has(team.leagueId))).toBe(true);
        expect(db.players.every((player) => teamIds.has(player.teamId))).toBe(true);
        expect(playerIds).toEqual(Array.from({ length: db.players.length }, (_, index) => index + 1));
      }),
      { numRuns: 100 }
    );
  });

  test("Feature: graphql-vs-rest-experiment, Property 2: Atributos estatisticos dos Jogadores", () => {
    fc.assert(
      fc.property(fc.integer({ min: 50, max: 90 }), (playerCount) => {
        const db = buildDatabase(playerCount);
        expect(
          db.players.every((player) =>
            STAT_FIELDS.every((field) => typeof player[field] === "number" && player[field] >= 0)
          )
        ).toBe(true);
      }),
      { numRuns: 100 }
    );
  });
});
