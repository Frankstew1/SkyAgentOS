/**
 * SkyAgentOS OpenClaw skill.
 * Trigger from WhatsApp/Telegram and enqueue via orchestrator HTTP API.
 */

const http = require("node:http");

function postJson(url, payload) {
  return new Promise((resolve, reject) => {
    const target = new URL(url);
    const req = http.request(
      {
        protocol: target.protocol,
        hostname: target.hostname,
        port: target.port,
        path: target.pathname,
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
      },
      (res) => {
        let body = "";
        res.on("data", (c) => (body += c.toString()));
        res.on("end", () => {
          if (res.statusCode >= 400) {
            reject(new Error(`orchestrator api error ${res.statusCode}: ${body}`));
            return;
          }
          resolve(body ? JSON.parse(body) : {});
        });
      }
    );
    req.on("error", reject);
    req.write(JSON.stringify(payload));
    req.end();
  });
}

module.exports = {
  name: "skyagentos_orchestrator_trigger",
  description: "Trigger SkyAgentOS orchestrator API from OpenClaw events",
  version: "2.0.0",

  async run(context) {
    const objective = context?.message?.text || "Run default SkyAgentOS mission";
    const channel = context?.channel || "unknown";
    const endpoint = process.env.ORCHESTRATOR_API_URL || "http://orchestrator:8787/missions";

    const response = await postJson(endpoint, {
      objective,
      metadata: {
        trigger_channel: channel,
        user_id: context?.user?.id || null,
      },
    });

    return {
      status: "accepted",
      objective,
      endpoint,
      response,
      telemetry: {
        otel_migration: "v2",
        trigger_channel: channel,
      },
    };
  },
};
