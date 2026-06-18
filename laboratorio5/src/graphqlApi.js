import { ApolloServer } from "@apollo/server";
import { GraphQLError } from "graphql";
import { getLeagueById, getPlayerById, getTeamById } from "./database.js";

export const typeDefs = `#graphql
  type League {
    id: Int!
    name: String!
    teams: [Team!]!
  }

  type Team {
    id: Int!
    name: String!
    league: League!
    players: [Player!]!
  }

  type Player {
    id: Int!
    nome: String!
    team: Team!
    gols: Int!
    assistencias: Int!
    cartoesAmarelos: Int!
    cartoesVermelhos: Int!
    passesCertos: Int!
    desarmes: Int!
    kmPercorridos: Float!
    finalizacoesNoGol: Int!
    faltasCometidas: Int!
    defesas: Int!
    interceptacoes: Int!
    cruzamentosCertos: Int!
    driblesCompletos: Int!
    duelosGanhos: Int!
    minutosJogados: Int!
  }

  type Query {
    player(id: Int!): Player
    league(id: Int!): League
    team(id: Int!): Team
  }
`;

export function createResolvers(db) {
  return {
    Query: {
      player: (_, { id }) => {
        const player = getPlayerById(db, id);
        if (!player) {
          throw new GraphQLError("jogador nao encontrado", {
            extensions: { code: "PLAYER_NOT_FOUND" }
          });
        }
        return player;
      },
      league: (_, { id }) => getLeagueById(db, id),
      team: (_, { id }) => getTeamById(db, id)
    },
    Player: {
      team: (player) => getTeamById(db, player.teamId)
    },
    Team: {
      league: (team) => getLeagueById(db, team.leagueId),
      players: (team) => db.players.filter((player) => player.teamId === team.id)
    },
    League: {
      teams: (league) => db.teams.filter((team) => team.leagueId === league.id)
    }
  };
}

export function createApolloServer(db) {
  return new ApolloServer({
    typeDefs,
    resolvers: createResolvers(db)
  });
}
