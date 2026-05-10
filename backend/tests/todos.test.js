const request = require("supertest");

jest.mock("../db", () => ({
  query: jest.fn(),
  initDb: jest.fn(),
}));

const db = require("../db");
const app = require("../server");

describe("Todo API routes", () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it("gets all todos", async () => {
    const todos = [
      {
        id: 1,
        title: "Study DevOps",
        completed: false,
        created_at: "2026-05-09T10:00:00.000Z",
      },
    ];

    db.query.mockResolvedValue({ rows: todos });

    const response = await request(app).get("/api/todos");

    expect(response.status).toBe(200);
    expect(response.body).toEqual(todos);
    expect(db.query).toHaveBeenCalledTimes(1);
  });

  it("adds a new todo", async () => {
    const newTodo = {
      id: 1,
      title: "Complete CI/CD assignment",
      completed: false,
      created_at: "2026-05-09T10:00:00.000Z",
    };

    db.query.mockResolvedValue({ rows: [newTodo] });

    const response = await request(app)
      .post("/api/todos")
      .send({ title: "  Complete CI/CD assignment  " });

    expect(response.status).toBe(201);
    expect(response.body).toEqual(newTodo);
    expect(db.query).toHaveBeenCalledWith(
      expect.stringContaining("INSERT INTO todos"),
      ["Complete CI/CD assignment"],
    );
  });

  it("rejects empty todo title", async () => {
    const response = await request(app)
      .post("/api/todos")
      .send({ title: "   " });

    expect(response.status).toBe(400);
    expect(response.body).toEqual({ error: "Title is required" });
    expect(db.query).not.toHaveBeenCalled();
  });

  it("marks a todo as complete", async () => {
    const updatedTodo = {
      id: 1,
      title: "Complete CI/CD assignment",
      completed: true,
      created_at: "2026-05-09T10:00:00.000Z",
    };

    db.query.mockResolvedValue({
      rowCount: 1,
      rows: [updatedTodo],
    });

    const response = await request(app)
      .put("/api/todos/1")
      .send({ completed: true });

    expect(response.status).toBe(200);
    expect(response.body).toEqual(updatedTodo);
    expect(db.query).toHaveBeenCalledWith(
      expect.stringContaining("UPDATE todos"),
      [true, "1"],
    );
  });

  it("deletes a todo", async () => {
    db.query.mockResolvedValue({
      rowCount: 1,
      rows: [{ id: 1 }],
    });

    const response = await request(app).delete("/api/todos/1");

    expect(response.status).toBe(204);
    expect(db.query).toHaveBeenCalledWith(
      "DELETE FROM todos WHERE id = $1 RETURNING id",
      ["1"],
    );
  });
});
