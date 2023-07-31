
async function getUserNames(url,Authorization) {
  try{
    const userAgent = navigator.userAgent;
    const methods = 'GET'; 
    const headers= {
      'User-Agent': userAgent,
      'Authorization': Authorization
    };
    const response = await sendRequest(url, "", methods, headers);
    return response;
  }catch (error) {
    console.error('Error:', error);
  }
}

async function getMyProfile(user) {
    //let username;
    //let id;
    const fileName = await getDomain('fileName');
    const AListPath = await getDomain('AListPath');
    const fileExtension = fileName.split('.').pop();
    const body = {
      "AListPath": AListPath + '/' + fileName,
      "fileName": fileName,
    }
    //await sendRequest(serverAddress+'/query','POST',{'table':inPut,'Domain':input.value})
    await sendRequest(serverAddress+'/AListPath',body,'POST');
    try {
      // const DomainFront = await getDomain('front');
      // api = DomainFront + '/api/me'

      // const data = await getUserNames(api,Authorization);
      // username = data.data.username;
      //id = data.data.id;


      const initConfig = {
        "document": {
          "fileType": fileExtension,
          "permissions": {
            "edit": true,
            "comment": true,
            "download": true,
            "print": true,
            "fillForms": true,
          },
          "title": fileName,
          "url": url,
          "key": generateDocumentKey(url)
        },
        "editorConfig": {
          "lang": "zh-CN",
          "mode": "edit",
          "callbackUrl": serverAddress+"/save",
          "customization": {
            "chat": false,
            "comments": false,
            "toolbar": {
              "hideEditButton": false
            }
          },
          "user": {
            "id": user['id'],
            "name": user['username']
          }
        },
        "height": "1080px",
        "type": "desktop",
      };
      //loadClassInFunction(Domain+'/web-apps/apps/api/documents/api.js', 'DocsAPI.DocEditor', DocsAPI => {
        const docEditor = new DocsAPI.DocEditor("placeholder", initConfig);
      //});

    } catch (error) {
      console.error('There was a problem with the fetch operation:', error);
    }
}

function generateDocumentKey(url) {
    const allowedChars = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-._=';
    const fileName = url.substring(url.lastIndexOf('/') + 1);
    const timestamp = new Date().toISOString();
    let key = fileName + timestamp;
    key = encodeURIComponent(key).substr(0, 20);
    key = key.split('').filter(char => allowedChars.includes(char)).join('');
    return key;
}
