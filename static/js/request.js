// static/js/request.js

export function getData(endpoint, callback) {
  const request = new XMLHttpRequest();
  request.onreadystatechange = () => {
    if (request.readyState === 4) {
      callback(request.response);
    }
  };
  request.open("GET", endpoint);
  request.send();
}

export function updateData(data, endpoint, callback) {

  const dataJSON = JSON.stringify(data);
  
  getAuthToken().then(token => {
    const request = new XMLHttpRequest();
    request.onreadystatechange = () => {
      if (request.readyState === 4) {
        //callback(request.response);
        //console.log("updateData readystate and response", request.readyState, request.response);
        console.log("updateData readystate 4")
      }
    };
    
    request.open("PUT", endpoint);
    request.setRequestHeader("Authorization", "Bearer " + token);
    request.setRequestHeader("Content-Type", "application/json");
    request.send(dataJSON);
  });
}

export function sendSecureQuery(form, action, endpoint, isJsonRequest, callback) {
  const formData = new FormData(form);

  getAuthToken().then(token => {
      const request = new XMLHttpRequest();
      request.onreadystatechange = () => {
          if (request.readyState === 4) {
              callback(request.response, form);
          }
      };

      request.open(action, endpoint, true);
      request.setRequestHeader("Authorization", "Bearer " + token);

      if (isJsonRequest) {
          // Convert form data to a JSON object
          const jsonBody = Object.fromEntries(formData.entries());
          request.setRequestHeader("Content-Type", "application/json");
          request.send(JSON.stringify(jsonBody));
      } else {
          // Convert form data into query parameters for URL
          const queryParams = new URLSearchParams(formData).toString();
          const urlWithParams = `${endpoint}?${queryParams}`;
          request.send();
      }
  });
}

function getAuthToken() {
  return fetch('/auth/token')
      .then(response => response.json())
      .then(data => data.token);
}