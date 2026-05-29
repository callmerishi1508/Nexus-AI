const fs = require('fs');
const content = fs.readFileSync('C:\\Web Hackathon\\nexus-frontend\\app\\page.tsx', 'utf-8');
const divsOpen = (content.match(/<div/g) || []).length;
const divsClose = (content.match(/<\/div>/g) || []).length;
console.log('divsOpen:', divsOpen);
console.log('divsClose:', divsClose);
