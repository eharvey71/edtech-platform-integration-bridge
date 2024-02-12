// static/js/notes.js

import { sendForm } from "./request.js";

export class Notes {
  constructor() {
    this.allNoteLists = document.querySelectorAll(".note-list");
    this.allNotes = document.querySelectorAll(".note-card");
    this.activateAllCreateForms();
  }

  activateAllCreateForms() {
    this.allNoteLists.forEach((noteList) => {
      const tokenCard = noteList.closest(".token-card");
      const tokenID = tokenCard.getAttribute("data-token-id");
      new NoteCreateForm(noteList, tokenID);
    });
  }
}

export class NoteCreateForm {
  constructor(noteList, tokenID) {
    this.noteList = noteList;
    this.tokenID = tokenID;
    this.form = this.noteList.querySelector(".note-create-card form");
    this.createButton = this.form.querySelector(
      "button[data-action='create']"
    );
    this.createButton.addEventListener(
      "click",
      this.handleCreateClick.bind(this)
    );
    this.connectToken();
  }

  connectToken() {
    let fieldTokenID = this.form.querySelector("input[name='kaltura_token_id']");
    fieldTokenID.setAttribute("value", this.tokenID);
  }

  handleCreateClick(event) {
    event.preventDefault();
    if (this.form.querySelector("input[name='content']").value.length > 0) {
      sendForm(this.form, "POST", "/api/notes", this.addNoteToList);
    }
    this.form.reset();
  }

  addNoteToList(rawData) {
    const data = JSON.parse(rawData);
    const noteList = document
      .querySelector("[data-token-id= '" + data.kaltura_token_id + "']")
      .querySelector(".note-list");
    const newNoteCard = document.querySelector(".note-card").cloneNode(true);
    newNoteCard.querySelector(".card-body").textContent = data.content;
    newNoteCard.setAttribute("data-note-id", data.id);
    noteList.insertBefore(newNoteCard, noteList.children[1]);
  }
}