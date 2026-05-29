const fs = require('fs');
const content = fs.readFileSync('C:\\Web Hackathon\\nexus-frontend\\app\\page.tsx', 'utf-8');
const lines = content.split('\n');

let stack = [];
for (let i = 0; i < lines.length; i++) {
  let line = lines[i];
  
  // ignore comments
  line = line.replace(/\/\/.*/, '');
  line = line.replace(/\{\/\*.*?\*\/\}/g, '');

  const opens = (line.match(/<div(?=[\s>])/g) || []).length;
  const closes = (line.match(/<\/div>/g) || []).length;
  
  for(let o=0; o<opens; o++) {
     stack.push(i+1);
  }
  for(let c=0; c<closes; c++) {
     if(stack.length > 0) stack.pop();
  }
}

console.log("Unclosed divs opened at lines:", stack);
