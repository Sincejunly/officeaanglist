async function generateDocumentKey(url) {
  const allowedChars = '0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ-_';
  const fileName = url.substring(url.lastIndexOf('/') + 1);
  const timestamp = Date.now().toString();
  const inputString = fileName + '_' + timestamp;

  // Generate SHA-256 hash using a built-in browser function
  const hashBuffer = await crypto.subtle.digest('SHA-256', new TextEncoder().encode(inputString));
  const hashArray = Array.from(new Uint8Array(hashBuffer));
  const hashHex = hashArray.map(byte => byte.toString(16).padStart(2, '0')).join('');

  // Convert the hash to a fixed-length alphanumeric string
  const key = hashHex.split('').filter(char => allowedChars.includes(char)).join('').slice(0, 20);

  return key;
}




async function getMyProfile(user) {
      const fileName = await getDomain('fileName');
      const AListPath = await getDomain('AListPath');
      const fileExtension = fileName.split('.').pop();
      const body = {
        "username": user['username'],
        "AListPath": AListPath,
        'fileName': fileName,
      }
      //await sendRequest(serverAddress+'/query','POST',{'table':inPut,'Domain':input.value})
      let permission;
      if(user['id'] != 1)
      {
        if (user['permission'] == 0){
          permission = false;
        }
        else{
          permission = await isin(user['permission']);
        }
        
      }
  
      
    await sendRequest(serverAddress+'/AListPath','POST',body);

      
    let url = await getDomain('url');


     const docEditor = new DocsAPI.DocEditor("placeholder", {
          "document": {
              "fileType": fileExtension,
              "permissions": {
                  "edit": user['id'] == 1 || permission ? true:false,
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
              "mode" : "edit" ,
              "callbackUrl": serverAddress+'/callback/',
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
              },
          },
          "height": "1080px",
          "type": "desktop",
      }
      );
}

