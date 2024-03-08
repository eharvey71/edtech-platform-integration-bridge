import { sendForm, getData, updateData } from "./request.js";

export class AddToken {
  constructor() {
    this.getTokenInfo = document.querySelector(".form-check-input");
    this.addExistingToken = document.querySelector(".add-existing-token");
    this.activateAddExistingForm();
    console.log("constructor. Get Token info checked?", this.getTokenInfo.checked);
    //this.activateAddNewForm();
  }

  activateAddExistingForm() {
    const existingTokenForm = document.querySelector(
      ".add-existing-token form"
    );
    new tokenAddExistingForm(existingTokenForm);
  }
}

class tokenAddExistingForm {
  constructor(el) {
    this.form = el;
    this.createButton = el.querySelector("button[data-action='add-token']");
    this.createButton.addEventListener(
      "click",
      this.handleCreateClick.bind(this)
    );

    this.createCheck = el.querySelector("input[type='checkbox']");
    this.createCheck.addEventListener(
      "change",
      this.handleCreateCheck.bind(this)
    );
  }

  handleCreateClick(event) {
    event.preventDefault();

    const tokenStatus = document.querySelector(".confirm-add-existing");
    const tokenStatusError = document.querySelector(".error-add-existing");
    tokenStatus.textContent = '';
    tokenStatusError.textContent = '';

    // If the checkbox is checked, attempt Kaltura connection to retrieve token info
    if (this.createCheck.checked) {
      this.getKalturaToken();
    }

    if (this.validateAddTokenForm()) {
      // Create the new token in the database via local API
      try {
        const response = sendForm(
          this.form,
          "POST",
          "/api/tokens",
          this.addTokenConfirm
        );
      } catch (error) {
        console.log("Error submitting form:", error);
      }
      this.form.reset();
    } else {
      alert("Please fill out all required fields");
    }
  }

  handleCreateCheck(event) {
    event.preventDefault();
    console.log("handleCreateCheck", this.createCheck.checked);
  }

  addTokenConfirm(rawData) {
    const data = JSON.parse(rawData);
    console.log("local add token confirm:", data);
    const tokenStatus = document.querySelector(".confirm-add-existing");
    
    if (data.kaltura_token_id != '') {
      tokenStatus.textContent = "Token with ID "
        + data.kaltura_token_id + " added...\n\n";
    }

  }

  getKalturaToken() {
    // If exists, get the KS from the form
    this.currentKS = document.querySelector(".ks-token").value;
    console.log("handleCreateClick", this.currentKS);

    // Run a query using GetData from request.js
    const endpoint = "https://www.kaltura.com/api_v3/service/apptoken/action/get?ks=" 
      + this.currentKS
      + "&format=1"
      + "&id=" + this.form.kaltura_token_id.value;

    getData(endpoint, this.updateTokenConfirm);
  }

  updateTokenConfirm(rawData) { 
    const data = JSON.parse(rawData);
    console.log("updateTokenConfirm:", data);
    if (data.objectType == "KalturaAPIException") {
      console.log ("Kaltura exception: ", data.message)
      const tokenStatus = document.querySelector(".error-add-existing");
      tokenStatus.textContent = "There was a problem retrieving Kaltura data: " + data.message
    } else {
      // Update the token if kaltura response is valid
      // post an update to the local API
      updateData(
        data,
        "/api/tokens",
        console.log("update token confirm:", data)
      );
    }
  }

  validateAddTokenForm() {
    if (document.querySelector("input[name='kaltura_token_id']").value == '' 
      || document.querySelector("input[name='token']").value == '') {
      return false;
    } else {
      return true;
    }
  }
}