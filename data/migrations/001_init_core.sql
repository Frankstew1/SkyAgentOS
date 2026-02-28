-- SkyAgentOS v2 core relational schema (Postgres target)
CREATE TABLE IF NOT EXISTS users (
  id TEXT PRIMARY KEY,
  email TEXT UNIQUE NOT NULL,
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS projects (
  id TEXT PRIMARY KEY,
  owner_user_id TEXT NOT NULL REFERENCES users(id),
  name TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS missions (
  id TEXT PRIMARY KEY,
  project_id TEXT NOT NULL REFERENCES projects(id),
  objective TEXT NOT NULL,
  state TEXT NOT NULL,
  policy_profile TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS runs (
  id TEXT PRIMARY KEY,
  mission_id TEXT NOT NULL REFERENCES missions(id),
  state TEXT NOT NULL,
  runtime TEXT,
  started_at TIMESTAMPTZ,
  finished_at TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS steps (
  id TEXT PRIMARY KEY,
  run_id TEXT NOT NULL REFERENCES runs(id),
  attempt INTEGER NOT NULL DEFAULT 1,
  runtime TEXT NOT NULL,
  action TEXT NOT NULL,
  status TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS tool_calls (
  id TEXT PRIMARY KEY,
  step_id TEXT NOT NULL REFERENCES steps(id),
  tool_name TEXT NOT NULL,
  input JSONB NOT NULL,
  output JSONB,
  status TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS artifacts (
  id TEXT PRIMARY KEY,
  run_id TEXT NOT NULL REFERENCES runs(id),
  step_id TEXT,
  kind TEXT NOT NULL,
  uri TEXT NOT NULL,
  metadata JSONB NOT NULL DEFAULT '{}'::jsonb,
  created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS approvals (
  id TEXT PRIMARY KEY,
  run_id TEXT NOT NULL REFERENCES runs(id),
  step_id TEXT,
  decision TEXT NOT NULL,
  reviewer TEXT,
  created_at TIMESTAMPTZ DEFAULT now()
);
