import { useArtifactStore } from "./src/store/useArtifactStore.ts";

function assert(condition, message) {
  if (!condition) {
    console.error("FAIL:", message);
    process.exit(1);
  } else {
    console.log("PASS:", message);
  }
}

console.log("Running Single Source of Truth Store Verification...\n");

// Step 1: Initial Selection & Compliance
const state1 = useArtifactStore.getState();
const artAId = state1.selectedArtifactId;
assert(artAId === "benchmark-resnet-accuracy", "Initial selected artifact is benchmark-resnet-accuracy");

const artA = state1.artifacts[artAId];
assert(artA.categories.length === 4, "Artifact A has 4 categories (ResNet-50, ViT-Base, etc.)");
assert(artA.series[0].values[0] === 78.4, "Artifact A series 0 val 0 is 78.4");
assert(artA.compliance.overall_score === 42, "Artifact A compliance score is 42%");
assert(artA.compliance.ssim_score === 38, "Artifact A SSIM score is 38%");
assert(artA.compliance.color_similarity === 94, "Artifact A Color similarity is 94%");

// Step 2: Switch Render Mode (Line -> Pie -> Bar)
useArtifactStore.getState().setRenderMode("line");
const state2a = useArtifactStore.getState();
assert(state2a.renderMode === "line", "Render mode switched to line");
assert(state2a.artifacts[artAId].series[0].values[0] === 78.4, "Values remain identical on Line mode");

useArtifactStore.getState().setRenderMode("pie");
const state2b = useArtifactStore.getState();
assert(state2b.renderMode === "pie", "Render mode switched to pie");
assert(state2b.artifacts[artAId].series[0].values[0] === 78.4, "Values remain identical on Pie mode");

useArtifactStore.getState().setRenderMode("bar");
assert(useArtifactStore.getState().renderMode === "bar", "Render mode switched back to bar");

// Step 3: Select Artifact B (Loss progression)
const artBId = "benchmark-loss-progression";
useArtifactStore.getState().setSelectedArtifact(artBId);
const state3 = useArtifactStore.getState();
assert(state3.selectedArtifactId === artBId, "Selected artifact switched to Artifact B");
const artB = state3.artifacts[artBId];
assert(artB.title.includes("Loss Curve"), "Artifact B title is Loss Curve");
assert(artB.categories[0] === "Epoch 10", "Artifact B first category is Epoch 10");
assert(artB.series[0].values[0] === 0.82, "Artifact B first value is 0.82");
assert(artB.compliance.overall_score === 35, "Artifact B compliance score is 35%");
assert(artB.compliance.ssim_score === 31, "Artifact B SSIM score is 31%");

// Step 4: Reselect Artifact A (Verify Determinism)
useArtifactStore.getState().setSelectedArtifact(artAId);
const state4 = useArtifactStore.getState();
const artAReselected = state4.artifacts[artAId];
assert(artAReselected.compliance.overall_score === 42, "Artifact A reselected compliance score is STILL 42%");
assert(artAReselected.compliance.ssim_score === 38, "Artifact A reselected SSIM score is STILL 38%");
assert(artAReselected.compliance.color_similarity === 94, "Artifact A reselected Color similarity is STILL 94%");

// Step 5: Edit a Cell in the Table
useArtifactStore.getState().updateCell(artAId, 0, 0, 99.9);
const state5 = useArtifactStore.getState();
assert(state5.artifacts[artAId].series[0].values[0] === 99.9, "Artifact A cell [0][0] updated to 99.9 in the single source of truth");

console.log("\nALL 5 ACCEPTANCE TESTS PASSED SUCCESSFULLY!");
