/**
 * SkyAgentOS OpenClaw skill.
 * Trigger from WhatsApp/Telegram events and launch orchestrator.
 */

const { spawn } = require("node:child_process");

function runCommand(bin, args, env) {
  return new Promise((resolve, reject) => {
    const proc = spawn(bin, args, {
      cwd: "/workspace/app",
      env,
    });

    let stdout = "";
    let stderr = "";

    proc.stdout.on("data", (chunk) => {
      stdout += chunk.toString();
    });

    proc.stderr.on("data", (chunk) => {
      stderr += chunk.toString();
    });

    proc.on("close", (code) => {
      if (code !== 0) {
        reject(new Error(`${bin} failed (${code}): ${stderr}`));
        return;
      }
      resolve(stdout.trim());
    });
  });
}

module.exports = {
  name: "skyagentos_orchestrator_trigger",
  description: "Trigger CrewAI orchestrator from OpenClaw events",
  version: "1.1.0",

  async run(context) {
    const objective = context?.message?.text || "Run default SkyAgentOS mission";
    const env = {
      ...process.env,
      SKYAGENT_OBJECTIVE: objective,
      OPENCLAW_TRIGGER_CHANNEL: context?.channel || "unknown",
    };

    let output;
    try {
      output = await runCommand("codex", ["exec", "python", "main_orchestrator.py"], env);
    } catch (_) {
      output = await runCommand("python", ["main_orchestrator.py"], env);
    }

    return {
      status: "ok",
      objective,
      output,
      telemetry: {
        otel_migration: "v2",
        trigger_channel: context?.channel || "unknown",
      },
    };
  },
};
