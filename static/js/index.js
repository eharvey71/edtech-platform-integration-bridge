// static/js/index.js

import { Notes } from "./notes.js";
import { Tokens } from "./tokens.js";
import { AddToken } from "./addtoken.js";

function main() {
  new Notes();
  new Tokens();
  if (document.querySelector(".add-existing-token")) {
    console.log("add existing token form found")
    new AddToken();
  }
}

main();