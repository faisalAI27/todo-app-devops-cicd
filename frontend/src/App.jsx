import { useCallback, useEffect, useMemo, useState } from "react";

const configuredApiUrl = import.meta.env.VITE_API_URL || "http://localhost:5000";
const normalizedApiUrl = configuredApiUrl.replace(/\/$/, "");
const apiBaseUrl = normalizedApiUrl.endsWith("/api")
  ? normalizedApiUrl
  : `${normalizedApiUrl}/api`;

const apiUrl = (path) => `${apiBaseUrl}${path}`;

async function requestJson(path, options = {}) {
  const response = await fetch(apiUrl(path), {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
  });

  if (response.status === 204) {
    return null;
  }

  const data = await response.json().catch(() => null);

  if (!response.ok) {
    throw new Error(data?.error || `Request failed with status ${response.status}`);
  }

  return data;
}

function formatDate(value) {
  if (!value) {
    return "";
  }

  return new Date(value).toLocaleString(undefined, {
    dateStyle: "medium",
    timeStyle: "short",
  });
}

export default function App() {
  const [todos, setTodos] = useState([]);
  const [title, setTitle] = useState("");
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");
  const [isDarkMode, setIsDarkMode] = useState(false);

  useEffect(() => {
    if (isDarkMode) {
      document.documentElement.classList.add("dark");
    } else {
      document.documentElement.classList.remove("dark");
    }
  }, [isDarkMode]);

  const loadTodos = useCallback(async () => {
    setLoading(true);
    setError("");

    try {
      const data = await requestJson("/todos");
      setTodos(data);
    } catch (err) {
      setError(err.message || "Unable to reach backend API");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadTodos();
  }, [loadTodos]);

  const stats = useMemo(() => {
    const completed = todos.filter((todo) => todo.completed).length;

    return {
      total: todos.length,
      completed,
      pending: todos.length - completed,
    };
  }, [todos]);

  const addTodo = async (event) => {
    event.preventDefault();

    if (!title.trim()) {
      setError("Todo title is required.");
      return;
    }

    setSaving(true);
    setError("");

    try {
      const created = await requestJson("/todos", {
        method: "POST",
        body: JSON.stringify({ title }),
      });
      setTodos((current) => [created, ...current]);
      setTitle("");
    } catch (err) {
      setError(err.message || "Unable to create todo");
    } finally {
      setSaving(false);
    }
  };

  const toggleTodo = async (todo) => {
    setSaving(true);
    setError("");

    try {
      const updated = await requestJson(`/todos/${todo.id}`, {
        method: "PUT",
        body: JSON.stringify({ completed: !todo.completed }),
      });
      setTodos((current) => (
        current.map((item) => (item.id === updated.id ? updated : item))
      ));
    } catch (err) {
      setError(err.message || "Unable to update todo");
    } finally {
      setSaving(false);
    }
  };

  const deleteTodo = async (todoId) => {
    setSaving(true);
    setError("");

    try {
      await requestJson(`/todos/${todoId}`, {
        method: "DELETE",
      });
      setTodos((current) => current.filter((todo) => todo.id !== todoId));
    } catch (err) {
      setError(err.message || "Unable to delete todo");
    } finally {
      setSaving(false);
    }
  };

  return (
    <main className="min-h-screen bg-slate-100 text-slate-950 dark:bg-slate-950 dark:text-slate-100 transition-colors duration-200">
      <div className="mx-auto flex min-h-screen w-full max-w-5xl flex-col px-4 py-8 sm:px-6 lg:px-8">
        <header className="mb-8 flex flex-col gap-4 border-b border-slate-200 dark:border-slate-800 pb-6 sm:flex-row sm:items-end sm:justify-between transition-colors duration-200">
          <div>
            <p className="text-sm font-semibold uppercase tracking-wide text-indigo-700 dark:text-indigo-400 object-colors duration-200">
              DevOps Todo
            </p>
            <h1 className="mt-2 text-3xl font-semibold tracking-normal text-slate-950 dark:text-slate-100 transition-colors duration-200">
              Task board
            </h1>
          </div>

          <div className="flex gap-3">
            <button
              className="rounded-md border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 px-4 py-2 text-sm font-medium text-slate-800 dark:text-slate-200 shadow-sm transition hover:border-slate-400 dark:hover:border-slate-600 disabled:cursor-not-allowed disabled:opacity-60"
              onClick={() => setIsDarkMode(!isDarkMode)}
            >
              {isDarkMode ? "Light Mode" : "Dark Mode"}
            </button>
            <button
              className="rounded-md border border-slate-300 dark:border-slate-700 bg-white dark:bg-slate-800 px-4 py-2 text-sm font-medium text-slate-800 dark:text-slate-200 shadow-sm transition hover:border-slate-400 dark:hover:border-slate-600 disabled:cursor-not-allowed disabled:opacity-60"
              onClick={loadTodos}
              disabled={loading || saving}
            >
              Refresh
            </button>
          </div>
        </header>

        <section className="mb-6 grid gap-3 sm:grid-cols-3">
          <div className="rounded-md border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-4 shadow-sm transition-colors duration-200">
            <p className="text-sm text-slate-500 dark:text-slate-400 transition-colors duration-200">Total</p>
            <p className="mt-1 text-2xl font-semibold text-slate-950 dark:text-slate-100 transition-colors duration-200">{stats.total}</p>
          </div>
          <div className="rounded-md border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-4 shadow-sm transition-colors duration-200">
            <p className="text-sm text-slate-500 dark:text-slate-400 transition-colors duration-200">Pending</p>
            <p className="mt-1 text-2xl font-semibold text-amber-700 dark:text-amber-500 transition-colors duration-200">
              {stats.pending}
            </p>
          </div>
          <div className="rounded-md border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-4 shadow-sm transition-colors duration-200">
            <p className="text-sm text-slate-500 dark:text-slate-400 transition-colors duration-200">Completed</p>
            <p className="mt-1 text-2xl font-semibold text-emerald-700 dark:text-emerald-500 transition-colors duration-200">
              {stats.completed}
            </p>
          </div>
        </section>

        <form
          className="mb-6 flex flex-col gap-3 rounded-md border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 p-4 shadow-sm transition-colors duration-200 sm:flex-row"
          onSubmit={addTodo}
        >
          <input
            className="min-w-0 flex-1 rounded-md border border-slate-300 dark:border-slate-700 bg-transparent px-3 py-2 text-slate-950 dark:text-slate-100 outline-none transition placeholder:text-slate-400 dark:placeholder:text-slate-500 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-200 dark:focus:ring-indigo-800"
            placeholder="Add a todo"
            value={title}
            onChange={(event) => setTitle(event.target.value)}
            disabled={saving}
          />
          <button
            className="rounded-md bg-indigo-600 dark:bg-indigo-500 px-5 py-2 font-semibold text-white shadow-sm transition hover:bg-indigo-700 dark:hover:bg-indigo-400 disabled:cursor-not-allowed disabled:opacity-60"
            type="submit"
            disabled={saving}
          >
            {saving ? "Saving..." : "Add"}
          </button>
        </form>

        {error ? (
          <div className="mb-6 rounded-md border border-red-200 dark:border-red-900/50 bg-red-50 dark:bg-red-900/20 px-4 py-3 text-sm text-red-800 dark:text-red-400 transition-colors duration-200">
            {error}
          </div>
        ) : null}

        <section className="flex-1 rounded-md border border-slate-200 dark:border-slate-800 bg-white dark:bg-slate-900 shadow-sm transition-colors duration-200">
          <div className="border-b border-slate-200 dark:border-slate-800 px-4 py-3 transition-colors duration-200">
            <h2 className="font-semibold text-slate-900 dark:text-slate-100 transition-colors duration-200">Todos</h2>
          </div>

          {loading ? (
            <p className="px-4 py-8 text-center text-sm text-slate-500 dark:text-slate-400 transition-colors duration-200">
              Loading todos...
            </p>
          ) : todos.length === 0 ? (
            <p className="px-4 py-8 text-center text-sm text-slate-500 dark:text-slate-400 transition-colors duration-200">
              No todos yet.
            </p>
          ) : (
            <ul className="divide-y divide-slate-200 dark:divide-slate-800 transition-colors duration-200">
              {todos.map((todo) => (
                <li
                  className="flex flex-col gap-3 px-4 py-4 sm:flex-row sm:items-center sm:justify-between hover:bg-slate-50 dark:hover:bg-slate-800/50 transition-colors duration-150"
                  key={todo.id}
                >
                  <label className="flex min-w-0 flex-1 items-start gap-3">
                    <input
                      className="mt-1 h-4 w-4 rounded border-slate-300 dark:border-slate-600 bg-transparent text-indigo-600 focus:ring-indigo-500 dark:focus:ring-indigo-400 focus:ring-offset-0 transition-colors duration-200"
                      type="checkbox"
                      checked={todo.completed}
                      onChange={() => toggleTodo(todo)}
                      disabled={saving}
                    />
                    <span className="min-w-0">
                      <span
                        className={`block break-words font-medium transition-colors duration-200 ${
                          todo.completed
                            ? "text-slate-400 dark:text-slate-600 line-through"
                            : "text-slate-950 dark:text-slate-100"
                        }`}
                      >
                        {todo.title}
                      </span>
                      <span className="mt-1 block text-xs text-slate-500 dark:text-slate-400 transition-colors duration-200">
                        Created {formatDate(todo.created_at)}
                      </span>
                    </span>
                  </label>

                  <button
                    className="self-start rounded-md border border-red-200 dark:border-red-900/50 px-3 py-2 text-sm font-medium text-red-700 dark:text-red-400 transition hover:bg-red-50 dark:hover:bg-red-900/20 disabled:cursor-not-allowed disabled:opacity-60 sm:self-center"
                    onClick={() => deleteTodo(todo.id)}
                    type="button"
                    disabled={saving}
                  >
                    Delete
                  </button>
                </li>
              ))}
            </ul>
          )}
        </section>
      </div>
    </main>
  );
}
