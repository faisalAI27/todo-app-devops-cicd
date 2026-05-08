const express = require("express");
const db = require("../db");

const router = express.Router();

router.get("/", async (_req, res, next) => {
  try {
    const result = await db.query(
      "SELECT id, title, completed, created_at FROM todos ORDER BY created_at DESC, id DESC",
    );
    res.json(result.rows);
  } catch (error) {
    next(error);
  }
});

router.post("/", async (req, res, next) => {
  const title = typeof req.body.title === "string" ? req.body.title.trim() : "";

  if (!title) {
    return res.status(400).json({ error: "Title is required" });
  }

  try {
    const result = await db.query(
      "INSERT INTO todos (title) VALUES ($1) RETURNING id, title, completed, created_at",
      [title],
    );
    return res.status(201).json(result.rows[0]);
  } catch (error) {
    return next(error);
  }
});

router.put("/:id", async (req, res, next) => {
  const { id } = req.params;
  const fields = [];
  const values = [];

  if (Object.prototype.hasOwnProperty.call(req.body, "title")) {
    const title = typeof req.body.title === "string" ? req.body.title.trim() : "";
    if (!title) {
      return res.status(400).json({ error: "Title cannot be empty" });
    }
    values.push(title);
    fields.push(`title = $${values.length}`);
  }

  if (Object.prototype.hasOwnProperty.call(req.body, "completed")) {
    if (typeof req.body.completed !== "boolean") {
      return res.status(400).json({ error: "Completed must be a boolean" });
    }
    values.push(req.body.completed);
    fields.push(`completed = $${values.length}`);
  }

  if (!fields.length) {
    return res.status(400).json({ error: "Provide title or completed to update" });
  }

  values.push(id);

  try {
    const result = await db.query(
      `UPDATE todos
       SET ${fields.join(", ")}
       WHERE id = $${values.length}
       RETURNING id, title, completed, created_at`,
      values,
    );

    if (!result.rowCount) {
      return res.status(404).json({ error: "Todo not found" });
    }

    return res.json(result.rows[0]);
  } catch (error) {
    return next(error);
  }
});

router.delete("/:id", async (req, res, next) => {
  try {
    const result = await db.query(
      "DELETE FROM todos WHERE id = $1 RETURNING id",
      [req.params.id],
    );

    if (!result.rowCount) {
      return res.status(404).json({ error: "Todo not found" });
    }

    return res.status(204).send();
  } catch (error) {
    return next(error);
  }
});

module.exports = router;
