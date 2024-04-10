import { writeFileSync } from "node:fs";
const data = { name: "Sample", description: "Demo", attributes: [] };
writeFileSync("examples/metadata/sample.json", JSON.stringify(data, null, 2));
