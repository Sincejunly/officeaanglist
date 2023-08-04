

async function submit(body) {
 

  try {
    const response = await fetch("http://127.0.0.1:5000/login", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(body)
    });

    const result = await response.json();
    console.log(result.message);
  } catch (error) {
    console.error("Error inserting data: ", error);
  }
}

async function deleteData(name) {
  try {
    const response = await fetch(`http://localhost:3000/office/delete/${name}`, {
      method: "DELETE"
    });

    const result = await response.json();
    console.log(result.message);
    // 执行成功后的操作
  } catch (error) {
    console.error("Error deleting data: ", error);
    // 处理错误情况
  }
}
async function queryData(value){
  try{
    const datas = {'table':'x_user','column':'name','value':value};
    const response = await sendRequest('http://localhost:5000/query','POST',datas);
    //const data = await response.json();
    console.log(response);
    return response['value'];
  }catch (error) {
    console.error('Error:', error);
  }
}
// async function queryData(tables, column, value) {
//   try {
//     const response = await fetch(`http://localhost:3000/office/query/${tables}/${column}/${value}`);
//     const data = await response.json();
//     if (data.length > 0) {
//       const value = data[0].value;
//       return value;
//     } else {
//       console.log("Value key not found");
//       return null;
//     }
//   } catch (error) {
//     console.error("Error querying value: ", error);
//     throw error;
//   }
// }
async function handleStatusCode(response) {
  let statusCode;
  let statusMessage;

  switch (response.status) {
    case 502:
      statusCode = "502 Bad Gateway";
      statusMessage = "Something went wrong on the server's end.";
      break;
    case 401:
      statusCode = "401 Unauthorized";
      statusMessage = "Something went wrong on the server's end.";
      break;
    // Add other cases for different status codes here...

    default:
      statusCode = "Unknown Error";
      statusMessage = "An unexpected error occurred.";
      break;
  }

  const result = `<h1>${statusCode}</h1><p>${statusMessage}</p>`;
  document.open();
  document.write(result);
  document.close();
}

async function sendRequest(url, methods, data = "", headers = {'Content-Type': 'application/json'}, needjson = true) {
  try {
    const requestOptions = {
      method: methods,
      headers: headers,
    };
    if (data !== "") {
      requestOptions.body = JSON.stringify(data);
    }
    const response = await fetch(url, requestOptions);

    if (!response.ok) {
      throw new Error('请求失败，状态码：' + response.status);
    }
  
    if (response.redirected) {
      window.location.href = response.url;
    } else {
      const contentType = response.headers.get('content-type');
      if (contentType && contentType.includes('text/html')) {
        const result = await response.text();
        document.open();
        document.write(result);
        document.close();
      } else {
        if (needjson) {
          const result = await response.json();
          return result;
        }
        return response;
      }
    }

  } catch (error) {
    console.error('错误:', error);
  }
}



async function loadCaptchaImage() {
  return new Promise(function(resolve, reject) {
    var captchaImage = document.getElementById("captchaImage");

    var xhr = new XMLHttpRequest();
    xhr.open("GET", serverAddress + "/generate_code", true);
    xhr.responseType = "blob";

    xhr.onload = function() {
      if (xhr.status === 200) {
        var blob = xhr.response;
        var imageUrl = URL.createObjectURL(blob);
        captchaImage.src = imageUrl;
        resolve();
      } else {
        reject(new Error("Failed to load captcha image"));
      }
    };

    xhr.onerror = function() {
      reject(new Error("Failed to send captcha image request"));
    };

    xhr.send();
  });
}
