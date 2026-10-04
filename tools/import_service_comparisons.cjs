const fs = require('fs');
const path = require('path');
const crypto = require('crypto');
const assert = require('assert/strict');
const sharp = require('C:/Users/yasoj/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/sharp');

const root = path.resolve(__dirname, '..');
const dataPath = path.join(root, 'source/service-pages/service-comparisons.json');
const site = path.join(root, 'source/site');
const records = fs.existsSync(dataPath) ? JSON.parse(fs.readFileSync(dataPath, 'utf8')) : {};

(async () => {
  for (const input of JSON.parse(fs.readFileSync(process.argv[2], 'utf8'))) {
    const {scene, state, generatedOriginal, prompt} = input;
    assert(/^[a-z-]+$/.test(scene) && ['before', 'after'].includes(state));
    const reference = `/assets/images/service-scenes/${scene}.webp`;
    const asset = `/assets/images/service-scenes/${scene}-${state}.webp`;
    const output = path.join(site, asset);
    assert(!fs.existsSync(output), `Asset already exists: ${asset}`);
    const metadata = await sharp(generatedOriginal).metadata();
    assert.equal(metadata.width, 1536);
    assert.equal(metadata.height, 1024);
    await sharp(generatedOriginal).webp({quality: 92}).toFile(output);
    records[scene] = {
      before: state === 'before' ? asset : reference,
      after: state === 'after' ? asset : reference,
      mode: 'built-in image_gen edit',
      editState: state,
      reference,
      generatedOriginal,
      prompt,
      sha256: crypto.createHash('sha256').update(fs.readFileSync(output)).digest('hex'),
      size: [metadata.width, metadata.height],
    };
  }
  fs.writeFileSync(dataPath, JSON.stringify(records, null, 2) + '\n');
  console.log(JSON.stringify({comparisons: Object.keys(records).length}));
})().catch(error => {console.error(error); process.exitCode = 1;});
