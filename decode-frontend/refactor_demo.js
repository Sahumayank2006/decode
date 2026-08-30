const fs = require('fs');
const path = require('path');

const filePath = path.resolve('c:/Users/licsa/Downloads/decode-main/decode-main/decode-frontend/src/components/demo/DemoWorkspace.tsx');
let content = fs.readFileSync(filePath, 'utf8');

// 1. Add import
content = content.replace(
  'import { normalizeCharts, type NormalizedChart } from "@/lib/canonicalNormalizer";\r\nimport {\r\n  useArtifactStore,',
  'import { normalizeCharts, type NormalizedChart } from "@/lib/canonicalNormalizer";\r\nimport LiveReconstructedPreview from "./LiveReconstructedPreview";\r\nimport {\r\n  useArtifactStore,'
);

// 2. Remove commonData and pieData
const removeRegex = /\/\/ commonData is derived directly from currentArtifact and shared across all chart modes[\s\S]*?}, \[currentArtifact\]\);\r\n/g;
content = content.replace(removeRegex, '// (Data calculation logic has been moved to LiveReconstructedPreview)\n');

// 3. Replace the massive chart block
const chartBlockStart = `                  {/* Live Recharts Canvas Container */}
                  <div
                    ref={chartContainerRef}
                    key={\`preview-canvas-\${currentArtifact.id}-\${renderMode}\`}
                    className="h-[380px] w-full bg-[#0f172a] rounded-2xl p-4 border border-slate-800 flex items-center justify-center relative overflow-hidden"
                  >`;

const chartBlockEnd = `                        </BarChart>
                      </ResponsiveContainer>
                    )}
                  </div>`;

const startIndex = content.indexOf('                  {/* Live Recharts Canvas Container */}');
const endIndex = content.indexOf('                  </div>', startIndex) + '                  </div>'.length;

if (startIndex !== -1 && endIndex !== -1) {
  const replacement = `                  {/* Live Recharts Canvas Container */}
                  <LiveReconstructedPreview
                    currentArtifact={currentArtifact}
                    renderMode={renderMode}
                    chartContainerRef={chartContainerRef}
                    key={\`preview-canvas-\${currentArtifact.id}-\${renderMode}\`}
                  />`;
  
  content = content.slice(0, startIndex) + replacement + content.slice(endIndex);
}

fs.writeFileSync(filePath, content, 'utf8');
console.log('Successfully refactored DemoWorkspace.tsx');
