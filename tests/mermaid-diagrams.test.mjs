import assert from "node:assert/strict";
import { readFile, readdir } from "node:fs/promises";
import test from "node:test";

const root = new URL("../", import.meta.url);
const skillRoot = ".agents/skills/mermaid-diagrams/";
const read = (path) => readFile(new URL(path, root), "utf8");
const json = async (path) => JSON.parse(await read(path));

// Static package checks only; these do not simulate model routing or Mermaid rendering.
test("Mermaid has one default shared install and a source-only capability profile", async () => {
  const components = await json("manifests/rose-aili.components.json");
  const entries = components.components.skills.filter(({ name }) => name === "mermaid-diagrams");
  assert.equal(entries.length, 1);
  assert.equal(entries[0].path, skillRoot.slice(0, -1));
  assert.equal(entries[0].defaultInstalled, true);
  assert.equal(entries[0].repositoryManaged, true);
  assert.deepEqual(entries[0].installTargets, [{ kind: "shared", path: skillRoot.slice(0, -1) }]);

  const capabilities = await json("manifests/skill-capabilities.json");
  const assignments = capabilities.assignments.filter(({ skills }) => skills.includes("mermaid-diagrams"));
  assert.equal(assignments.length, 1);
  const profile = capabilities.profiles[assignments[0].profile];
  assert.deepEqual(profile.requiredCapabilities, []);
  assert.deepEqual(profile.optionalCapabilities, ["repo.read", "repo.write", "artifact.transform", "web.fetch"]);
  assert.match(profile.missingBehavior, /BLOCKED/);
  assert.match(profile.missingBehavior, /Unverified/);
});

test("Mermaid ships only its entry and directly linked maintained references", async () => {
  const skill = await read(`${skillRoot}SKILL.md`);
  assert.match(skill, /^---\nname: mermaid-diagrams\ndescription: /);
  assert.deepEqual((await readdir(new URL(skillRoot, root))).sort(), ["SKILL.md", "references"]);
  const general = ["diagram-types.md", "output-and-editing.md", "readability-and-theme.md", "syntax-pitfalls.md", "validation.md"];
  const types = ["architecture.md", "class.md", "er.md", "flowchart.md", "mindmap.md", "sequence.md", "state.md", "timeline.md"];
  assert.deepEqual((await readdir(new URL(`${skillRoot}references/`, root))).sort(), [...general, "types"].sort());
  assert.deepEqual((await readdir(new URL(`${skillRoot}references/types/`, root))).sort(), types);
  for (const ref of [...general, ...types.map((name) => `types/${name}`)]) {
    assert.ok(skill.includes(`](references/${ref})`), `missing direct reference: ${ref}`);
    const body = await read(`${skillRoot}references/${ref}`);
    assert.ok(body.trim().length > 0);
    if (ref.startsWith("types/")) {
      assert.match(body, /Fictional/);
      assert.match(body, /indispensable/);
      assert.match(body, /```mermaid\n/);
      assert.match(body, /https:\/\/mermaid\.js\.org\/syntax\//);
    }
  }
});

test("Mermaid routing fixtures retain positive, near-miss, and capability-limit cases", async () => {
  const fixture = await json("docs/harness/fixtures/skill-routing-fixtures.yaml");
  const cases = fixture.cases.filter(({ skill }) => skill === "mermaid-diagrams");
  const byId = new Map(cases.map((entry) => [entry.id, entry]));
  assert.equal(byId.size, cases.length);
  for (const suffix of ["conversation-branches", "proactive-clarity", "sequence", "edit-one-block", "standalone-source", "fix-parser", "explain-existing", "missing-renderer", "denied-write", "export-timeout", "unknown-proposed", "narrow-screen"]) {
    const entry = byId.get(`mermaid-${suffix}`);
    assert.equal(entry?.expected, "trigger", suffix);
    assert.ok(entry.expected_handoff, suffix);
  }
  for (const suffix of ["status", "one-fact", "data-chart", "marketing-slides"]) {
    assert.equal(byId.get(`mermaid-${suffix}`)?.expected, "non-trigger", suffix);
  }
});
