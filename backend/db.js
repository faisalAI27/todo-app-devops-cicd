const { Pool } = require("pg");

const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  host: process.env.PGHOST,
  port: process.env.PGPORT ? Number(process.env.PGPORT) : 5432,
  user: process.env.PGUSER,
  password: process.env.PGPASSWORD,
  database: process.env.PGDATABASE,
});

const wait = (ms) => new Promise((resolve) => {
  setTimeout(resolve, ms);
});

async function initDb(retries = 10) {
  for (let attempt = 1; attempt <= retries; attempt += 1) {
    try {
      await pool.query(`
        CREATE TABLE IF NOT EXISTS todos (
          id SERIAL PRIMARY KEY,
          title TEXT NOT NULL,
          completed BOOLEAN DEFAULT false,
          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
      `);
      return;
    } catch (error) {
      if (attempt === retries) {
        throw error;
      }
      console.log(`Database not ready, retrying (${attempt}/${retries})...`);
      await wait(2000);
    }
  }
}

module.exports = {
  initDb,
  pool,
  query: (text, params) => pool.query(text, params),
};
