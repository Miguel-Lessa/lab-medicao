import express from "express";
import { getPlayerById } from "./database.js";

export function parsePlayerId(rawId) {
  if (typeof rawId !== "string" || !/^[1-9]\d*$/.test(rawId)) {
    return null;
  }
  return Number(rawId);
}

export function createRestRouter(db) {
  const router = express.Router();

  router.get("/players/:id", (req, res) => {
    const id = parsePlayerId(req.params.id);
    if (id === null || !Number.isSafeInteger(id)) {
      return res.status(400).json({ error: "identificador invalido" });
    }

    const player = getPlayerById(db, id);
    if (!player) {
      return res.status(404).json({ error: "jogador nao encontrado" });
    }

    return res.status(200).json(player);
  });

  return router;
}
