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




async function getMyProfile(user,fileName,fileExtension,key) {

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

      
    let url = await getDomain('url');

     var onDownloadAs = async function (event) {
        var url = event.data.url;
        var body = {
          'url':url,
          'status':10
        }
        await sendRequest(serverAddress+'/callback/','POST',body);
        //console.log("ONLYOFFICE Document Editor create file: " + url);
      };
    var onDocumentStateChange = function (event) {
        if (event.data) {
          var fileType = event.data.fileType;
          docEditor.downloadAs(fileType);
        } else {
            console.log("Changes are collected on document editing service");
        }
    };
     const docEditor = new DocsAPI.DocEditor("placeholder", {
          "events":{
            "onDownloadAs": onDownloadAs,
            "onDocumentStateChange": onDocumentStateChange,
          },
          "lang": "zh-CN",
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
              "key": key
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
                "id": String(user['id']),
                "name": user['username']
              },
          },
          "height": "1080px",
          "type": "desktop",
      }
      );
      
      const AListPath = await getDomain('AListPath');
      fileExtension = fileName.split('.').pop();
      const body = {
          "username": user['username'],
          "AListPath": AListPath,
          'fileName': fileName,
          'key':key
      }
      await sendRequest(serverAddress+'/savePath','POST',body);
      
}

