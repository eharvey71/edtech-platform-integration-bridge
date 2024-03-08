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

export function sendForm(form, action, endpoint, callback) {
  
  const currentProtocol = window.location.protocol; // 'http:' or 'https:'
  const baseUrl = `${currentProtocol}//${window.location.host}`;
  const fullUrl = `${baseUrl}${endpoint}`;
  
  console.log("sendForm - Full URL", fullUrl);
  
  const formData = new FormData(form);
  const dataJSON = JSON.stringify(Object.fromEntries(formData));

  const request = new XMLHttpRequest();
  request.onreadystatechange = () => {
    if (request.readyState === 4) {
      callback(request.response, form);
    }
  };
  request.open(action, fullUrl);
  request.setRequestHeader("Content-Type", "application/json");
  request.send(dataJSON);
}

export function updateData(data, endpoint, callback) {
  const currentProtocol = window.location.protocol; // 'http:' or 'https:'
  const baseUrl = `${currentProtocol}//${window.location.host}`;
  const fullUrl = `${baseUrl}${endpoint}`;
  
  console.log("updateData - Full URL", fullUrl);

  const dataJSON = JSON.stringify(data);
  
  const request = new XMLHttpRequest();
  request.onreadystatechange = () => {
    if (request.readyState === 4) {
      //callback(request.response);
      console.log("updateData readystate and response", request.readyState, request.response);
    }
  };
  
  request.open("PUT", fullUrl);

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

          console.log(`Sending JSON request to ${endpoint}`);
          request.send(JSON.stringify(jsonBody));
      } else {
          // Convert form data into query parameters for URL
          const queryParams = new URLSearchParams(formData).toString();
          const urlWithParams = `${endpoint}?${queryParams}`;
          
          console.log(`Sending query parameter request to ${urlWithParams}`);
          // No need to set Content-Type for query parameter requests
          request.send();
      }
  });
}

function getAuthToken() {
  return fetch('/auth')
      .then(response => response.json())
      .then(data => data.token);
}