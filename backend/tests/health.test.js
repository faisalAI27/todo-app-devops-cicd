const request = require("supertest");
const app = require("../server");

describe("GET /api/health", () => {
  it("returns backend health status", async () => {
    const response = await request(app).get("/api/health");

    expect(response.status).toBe(200);
    expect(response.body).toEqual({
      status: "ok",
      message: "Backend is running",
    });
  });
});
