import cors from "cors";
import express from "express";
import { expressMiddleware } from "@apollo/server/express4";
import { buildDatabase } from "./database.js";
import { createApolloServer } from "./graphqlApi.js";
import { createRestRouter } from "./restApi.js";

export async function createApp(db = buildDatabase()) {
  const app = express();
  const apolloServer = createApolloServer(db);
  await apolloServer.start();

  app.use(cors({ methods: ["GET", "POST"], allowedHeaders: ["Content-Type"] }));
  app.use(express.json());
  app.use("/rest", createRestRouter(db));
  app.use("/graphql", expressMiddleware(apolloServer));
  app.use((err, _req, res, _next) => {
    res.status(500).json({ error: err.message ?? "erro interno" });
  });

  return { app, db, apolloServer };
}

export async function startServer(port = 4000, options = {}) {
  const { app, db, apolloServer } = await createApp(options.db);
  const exitOnError = options.exitOnError ?? port === 4000;

  return new Promise((resolve, reject) => {
    const server = app.listen(port);

    server.once("listening", () => {
      const address = server.address();
      const actualPort = typeof address === "object" && address ? address.port : port;
      console.log(`Servidor API disponivel na porta ${actualPort}`);
      resolve({ server, app, db, apolloServer, port: actualPort });
    });

    server.once("error", (error) => {
      if (error.code === "EADDRINUSE") {
        console.error(`Porta ${port} ja esta em uso. Encerre o processo existente e tente novamente.`);
        if (exitOnError) {
          process.exit(1);
        }
      }
      reject(error);
    });
  });
}
