/**
 * node handlebars.js template data
 */
const Handlebars = require('handlebars');

const args = process.argv.slice(2);

if(args.length !== 2) {
  console.error('Error: Should provide two arguments, "template" and "data"')
  console.error("Usage: node handlebars.js template data");
  process.exit(1);
}

try {
  const template = args[0]
  const data = JSON.parse(args[1]);
  const out = Handlebars.compile(template)(data);
  process.stdout.write(out);
} catch (err) {
  console.error(err);
  process.exit(1);
}

process.exit(0);