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
  const dataJSON = JSON.stringify(data);

  function sendRequest(url) {
    const request = new XMLHttpRequest();
    request.onreadystatechange = () => {
      if (request.readyState === 4) {
        //callback(request.response);
        console.log("updateData readystate and response", request.readyState, request.response);
      }
    };
    request.onerror = () => {
      console.error("Request failed. Retrying with HTTP if HTTPS was used.");
      if (url.startsWith("https://")) {
        sendRequest(url.replace("https://", "http://"));
      }
    };
    request.open("PUT", endpoint);
    request.setRequestHeader("Content-Type", "application/json");
    request.send(dataJSON);
  }

  /* This will need to be determined from a Flask env open or endpoint */
  /* Until then, make sure that the HTTP fallback only happens in dev */
  const isDevelopment = false;
  const protocol = isDevelopment ? "http://" : "https://";
  const secureEndpoint = endpoint.replace(/^https?:\/\//i, protocol);
 
  sendRequest(secureEndpoint);
}
