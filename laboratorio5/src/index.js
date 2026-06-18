import { startServer } from "./server.js";

startServer(4000).catch((error) => {
  console.error(`Falha ao iniciar o servidor: ${error.message}`);
  process.exit(1);
});
