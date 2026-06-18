export const STAT_FIELDS = [
  "gols",
  "assistencias",
  "cartoesAmarelos",
  "cartoesVermelhos",
  "passesCertos",
  "desarmes",
  "kmPercorridos",
  "finalizacoesNoGol",
  "faltasCometidas",
  "defesas",
  "interceptacoes",
  "cruzamentosCertos",
  "driblesCompletos",
  "duelosGanhos",
  "minutosJogados"
];

const firstNames = [
  "Miguel",
  "Arthur",
  "Heitor",
  "Gael",
  "Theo",
  "Davi",
  "Gabriel",
  "Bernardo",
  "Samuel",
  "Joao",
  "Pedro",
  "Lucas"
];

const lastNames = [
  "Silva",
  "Santos",
  "Oliveira",
  "Souza",
  "Lima",
  "Pereira",
  "Costa",
  "Ferreira",
  "Almeida",
  "Ribeiro"
];

export function buildDatabase(playerCount = 60) {
  if (!Number.isInteger(playerCount) || playerCount < 50) {
    throw new Error("playerCount deve ser um inteiro maior ou igual a 50");
  }

  const leagues = [
    { id: 1, name: "Liga Nacional" },
    { id: 2, name: "Liga Continental" }
  ];

  const teams = [
    { id: 1, name: "Azuis FC", leagueId: 1 },
    { id: 2, name: "Rubro AC", leagueId: 1 },
    { id: 3, name: "Verdes EC", leagueId: 1 },
    { id: 4, name: "Estrela SC", leagueId: 2 },
    { id: 5, name: "Capital United", leagueId: 2 },
    { id: 6, name: "Porto Real", leagueId: 2 }
  ];

  const players = Array.from({ length: playerCount }, (_, index) => {
    const id = index + 1;
    const team = teams[index % teams.length];
    const base = id * 7;

    return {
      id,
      nome: `${firstNames[index % firstNames.length]} ${lastNames[index % lastNames.length]}`,
      teamId: team.id,
      gols: base % 35,
      assistencias: (base + 3) % 28,
      cartoesAmarelos: (base + 1) % 10,
      cartoesVermelhos: (base + 2) % 3,
      passesCertos: 250 + base * 9,
      desarmes: 15 + (base % 90),
      kmPercorridos: Number((75 + (base % 180) / 2).toFixed(1)),
      finalizacoesNoGol: 5 + (base % 80),
      faltasCometidas: base % 45,
      defesas: team.id % 3 === 0 ? base % 120 : 0,
      interceptacoes: 4 + (base % 70),
      cruzamentosCertos: base % 55,
      driblesCompletos: base % 65,
      duelosGanhos: 20 + (base % 110),
      minutosJogados: 900 + base * 13
    };
  });

  return { leagues, teams, players };
}

export function getPlayerById(db, id) {
  return db.players.find((player) => player.id === id) ?? null;
}

export function getTeamById(db, id) {
  return db.teams.find((team) => team.id === id) ?? null;
}

export function getLeagueById(db, id) {
  return db.leagues.find((league) => league.id === id) ?? null;
}

export function getPlayerCount(db) {
  return db.players.length;
}

export function isCompletePlayer(player) {
  return Boolean(player?.id && player?.nome && STAT_FIELDS.every((field) => field in player));
}
