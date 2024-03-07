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
  const formData = new FormData(form);
  const dataJSON = JSON.stringify(Object.fromEntries(formData));

  const request = new XMLHttpRequest();
  request.onreadystatechange = () => {
    if (request.readyState === 4) {
      callback(request.response, form);
    }
  };
  request.open(action, endpoint);
  request.setRequestHeader("Content-Type", "application/json");
  request.send(dataJSON);
}

export function updateData(data, endpoint, callback) {
  const currentProtocol = window.location.protocol; // 'http:' or 'https:'
  const baseUrl = `${currentProtocol}//${window.location.host}`;
  const fullUrl = `${baseUrl}${endpoint}`;
  
  console.log("Full URL", fullUrl);

  const dataJSON = JSON.stringify(data);
  
  const request = new XMLHttpRequest();
  request.onreadystatechange = () => {
    if (request.readyState === 4) {
      //callback(request.response);
      console.log("updateData readystate and response", request.readyState, request.response);
    }
  };
  
  request.open("PUT", fullUrl);
  request.setRequestHeader("Content-Type", "application/json");
  request.send(dataJSON);
}
