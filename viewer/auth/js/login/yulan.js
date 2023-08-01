async function generateDocumentKey(url) {
  const allowedChars = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-._=';
  const fileName = url.substring(url.lastIndexOf('/') + 1);
  const timestamp = new Date().toISOString();
  let key = fileName + timestamp;
  key = encodeURIComponent(key).substr(0, 20);
  key = key.split('').filter(char => allowedChars.includes(char)).join('');
  return key;
}

async function getMyProfile(user) {
    //let username;
    //let id;
    const fileName = await getDomain('fileName');
    const AListPath = await getDomain('AListPath');
    const fileExtension = fileName.split('.').pop();
    const body = {
      "username": user['username'],
      "AListPath": AListPath,
      'fileName': fileName,
    }
    //await sendRequest(serverAddress+'/query','POST',{'table':inPut,'Domain':input.value})
    await sendRequest(serverAddress+'/AListPath','POST',body);
    let url = await getDomain('url');
    try {

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
          "key": await generateDocumentKey(url)
        },
        "editorConfig": {
          "lang": "zh-CN",
          "mode": "edit",
          "callbackUrl": `${await isin(user['permission']) ? serverAddress : ""}/save`,
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

