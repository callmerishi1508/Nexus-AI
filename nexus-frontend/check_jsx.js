const fs = require('fs');
const babel = require('@babel/core');

try {
  let code = fs.readFileSync('C:\\Web Hackathon\\nexus-frontend\\app\\page.tsx', 'utf-8');
  babel.parseSync(code, {
    presets: ['@babel/preset-react', '@babel/preset-typescript'],
    filename: 'page.tsx'
  });
  console.log("Syntax is valid!");
} catch (e) {
  console.error("Syntax Error:", e.message);
}
