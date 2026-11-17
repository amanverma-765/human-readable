#!/usr/bin/env node

/**
 * Human-Readable CLI & Skill Installer
 * Allows single-command installation via `npx human-readable install`
 * and direct verification via `npx human-readable <args>`.
 */

const fs = require("fs");
const path = require("path");
const os = require("os");
const { spawn } = require("child_process");

const ROOT_DIR = path.resolve(__dirname, "..");
const SKILL_SOURCE = path.join(ROOT_DIR, "skills", "human-readable", "SKILL.md");

const AGENT_GLOBAL_PATHS = {
  claude: path.join(os.homedir(), ".claude", "skills", "human-readable"),
  antigravity: path.join(os.homedir(), ".gemini", "antigravity-cli", "skills", "human-readable"),
  cursor: path.join(os.homedir(), ".cursor", "skills", "human-readable"),
  opencode: path.join(os.homedir(), ".opencode", "skills", "human-readable"),
};

function printHelp() {
  console.log(`
Human-Readable: Psycholinguistic Readability Linter & Agent Skill

Usage:
  npx human-readable install [options]   Install the skill into your coding agent
  npx human-readable [options] [paths]   Run the deterministic readability verifier
  npx readable [options] [paths]         Run the verifier directly

Installer Options:
  --global, -g           Install globally for detected agents (Claude Code, Antigravity, Cursor, etc.)
  --agent <name>         Install only for specific agent (claude | antigravity | cursor | opencode)
  --dir <path>           Install into custom directory (e.g. .agents/skills/human-readable)

Verifier Options:
  -s, --string <text>    Verify inline string directly
  --strict               Treat warnings as errors (exit code 1 on any violation)
  --format <fmt>         Output format: human (default), json, github
  --help, -h             Show this help message

Examples:
  npx human-readable install                  # Install to current workspace (.agents/skills)
  npx human-readable install --global         # Install to all detected coding agents
  npx human-readable -s "The check forgot str." # Check sentence
  npx human-readable docs/                    # Check directory
`);
}

function copyFile(src, dest) {
  const destDir = path.dirname(dest);
  if (!fs.existsSync(destDir)) {
    fs.mkdirSync(destDir, { recursive: true });
  }
  fs.copyFileSync(src, dest);
}

function handleInstall(args) {
  if (!fs.existsSync(SKILL_SOURCE)) {
    console.error(`Error: Source skill not found at ${SKILL_SOURCE}`);
    process.exit(1);
  }

  const isGlobal = args.includes("--global") || args.includes("-g");
  const agentIdx = args.indexOf("--agent");
  const targetAgent = agentIdx !== -1 ? args[agentIdx + 1] : null;
  const dirIdx = args.indexOf("--dir");
  const customDir = dirIdx !== -1 ? args[dirIdx + 1] : null;

  const installedLocations = [];

  if (customDir) {
    const dest = path.join(path.resolve(customDir), "SKILL.md");
    copyFile(SKILL_SOURCE, dest);
    installedLocations.push(dest);
  } else if (isGlobal) {
    for (const [name, targetDir] of Object.entries(AGENT_GLOBAL_PATHS)) {
      if (targetAgent && targetAgent.toLowerCase() !== name) {
        continue;
      }
      const dest = path.join(targetDir, "SKILL.md");
      try {
        copyFile(SKILL_SOURCE, dest);
        installedLocations.push(`${name} -> ${dest}`);
      } catch (err) {
        // Skip inaccessible agent dirs
      }
    }
  } else {
    // Default: Install into current project (.agents/skills/human-readable & skills/human-readable)
    const localAgentDest = path.join(process.cwd(), ".agents", "skills", "human-readable", "SKILL.md");
    const localSkillDest = path.join(process.cwd(), "skills", "human-readable", "SKILL.md");
    copyFile(SKILL_SOURCE, localAgentDest);
    copyFile(SKILL_SOURCE, localSkillDest);
    installedLocations.push(localAgentDest);
    installedLocations.push(localSkillDest);
  }

  console.log("\x1b[32m✔ Successfully installed human-readable skill!\x1b[0m\n");
  console.log("Installed to:");
  installedLocations.forEach((loc) => console.log(`  - ${loc}`));
  console.log("\nYour coding agent will now enforce human-readable prose and verify output.");
  console.log("To verify text anytime, run: npx human-readable -s \"your sentence here\"");
}

function handleVerify(args) {
  const pythonBin = process.platform === "win32" ? "python" : "python3";
  const pythonScript = path.join(ROOT_DIR, "readable", "cli.py");

  const child = spawn(pythonBin, [pythonScript, ...args], {
    stdio: "inherit",
    env: {
      ...process.env,
      PYTHONPATH: ROOT_DIR,
    },
  });

  child.on("error", (err) => {
    if (err.code === "ENOENT") {
      console.error("\x1b[31mError: python3 was not found in your PATH.\x1b[0m");
      console.error("Please ensure Python 3.8+ is installed to run verification.");
    } else {
      console.error(`Error running readable: ${err.message}`);
    }
    process.exit(1);
  });

  child.on("close", (code) => {
    process.exit(code ?? 0);
  });
}

function main() {
  const args = process.argv.slice(2);

  if (args.length === 0 || args.includes("-h") || args.includes("--help")) {
    printHelp();
    process.exit(0);
  }

  if (args[0] === "install") {
    handleInstall(args.slice(1));
  } else {
    handleVerify(args);
  }
}

main();
