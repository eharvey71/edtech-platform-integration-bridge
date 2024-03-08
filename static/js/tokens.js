// static/js/tokens.js

import { sendSecureQuery } from "./request.js";

export class Tokens {
    constructor() {
      this.allTokenCards = document.querySelectorAll(".token-card");
      this.activateAllControls();
    }

    activateAllControls() {
      this.allTokenCards.forEach((tokenCard) => {
        new TokenControl(tokenCard);
      });
    }
  }

  class TokenControl {
    constructor(tokenCard) {
      this.tokenCard = tokenCard;
      this.tokenElement = this.tokenCard.querySelector(".token-content");
      this.tokenControl = this.tokenCard.querySelector(".token-control");
      this.tokenID = this.tokenCard.getAttribute("data-token-id");
      this.form = this.tokenCard.querySelector("form");
  
      this.editBtn = this.tokenCard.querySelector(".toggle-control");
      this.editBtn.addEventListener("click", this.handleEditClick.bind(this));
      this.cancelBtn = this.tokenCard.querySelector("[data-action='cancel']");
      this.cancelBtn.addEventListener("click", this.handleCancelClick.bind(this));
      this.deleteBtn = this.tokenCard.querySelector("[data-action='delete']");
      this.deleteBtn.addEventListener("click", this.handleDeleteClick.bind(this));
    }
  
    handleEditClick(event) {
      event.preventDefault();
      this.tokenCard
        .querySelector(".token-control-card")
        .classList.add("editing");
      this.tokenElement.classList.add("hidden");
      this.editBtn.classList.add("hidden");
      this.tokenControl.classList.remove("hidden");
    }
  
    handleCancelClick(event) {
      event.preventDefault();
      this.tokenCard
        .querySelector(".token-control-card")
        .classList.remove("editing");
      this.tokenElement.classList.remove("hidden");
      this.editBtn.classList.remove("hidden");
      this.tokenControl.classList.add("hidden");
    }
  
    handleDeleteClick(event) {
      event.preventDefault();
      const endpoint = "/api/token/" + this.tokenID;
      if (window.confirm("Do you really want to remove this token?")) {
        sendSecureQuery(this.form, "DELETE", endpoint, false, (data, inputForm) => {
          let tokenCard = inputForm.closest(".token-card");
          tokenCard.remove();
        });
      }
    }
  
    handleUpdateClick(event) {
      event.preventDefault();
      const endpoint = "/api/token/" + this.tokenID;
      sendSecureQuery(this.form, "PUT", endpoint, true, this.updateTokenInList);
      this.cancelBtn.click();
    }
  
    updateTokenInList(rawData, inputForm) {
      const data = JSON.parse(rawData);
      const tokenCard = inputForm.closest(".token-card");
    }
  }