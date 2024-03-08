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

export function sendQuery(form, action, endpoint, callback) {
  // Convert form data into query parameters
  const formData = new FormData(form);
  const queryParams = new URLSearchParams(formData).toString();

  // Prepare the endpoint URL with query parameters
  const urlWithParams = `${endpoint}?${queryParams}`;

  getAuthToken().then(token => {
      const request = new XMLHttpRequest();
      request.onreadystatechange = () => {
          if (request.readyState === 4) {
              callback(request.response, form);
          }
      };
      request.open(action, urlWithParams, true);
      request.setRequestHeader("Authorization", "Basic " + token);

      // Since you're not sending a request body, there's no need to set Content-Type here
      // Send the request without a body
      request.send();
  });
}

function getAuthToken() {
  return fetch('/get_auth_token')
      .then(response => response.json())
      .then(data => data.token);
}