


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
var count = 0;
 var onDownloadAs = async function (event) {
    var url = event.data.url;
    var body = {
      'url':url,
      'status':10
    }
    count = count + 1;
    if(count == 10)
    {
      count = 0;
      await sendRequest(serverAddress+'/callback/','POST',body);
    }
    
    //console.log("ONLYOFFICE Document Editor create file: " + url);
  };
var onDocumentStateChange = async function (event) {
    if (event.data) {
      var fileType = event.data.fileType;
      docEditor.downloadAs(fileType);
    } else {
        console.log("Changes are collected on document editing service");
    }
};
var onAppReady = async function () {
    const iframe = document.querySelector('iframe[name="frameEditor"]');
    iframe.style.height = window.innerHeight + 'px';
    iframe.style.width = window.innerWidth + 'px';
};

 const docEditor = new DocsAPI.DocEditor("placeholder", {
      "events":{
        "onDownloadAs": onDownloadAs,
        "onDocumentStateChange": onDocumentStateChange,
        "onAppReady": onAppReady,
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
      "type": "desktop",
  }
  );

  async function resizeIframe() {
    const iframe = document.querySelector('iframe[name="frameEditor"]');
    iframe.style.height = window.innerHeight + 'px';
    iframe.style.width = window.innerWidth + 'px';
  }
  
  // 在窗口大小变化时调用 resizeIframe 函数
  window.addEventListener('resize', resizeIframe);

  const AListPath = await getDomain('AListPath');
  const AAListPath = await getDomain('AAListPath');
  fileExtension = fileName.split('.').pop();
  const body = {
      "username": user['username'],
      "AListPath": AListPath,
      'AAListPath':AAListPath,
      'fileName': fileName,
      'key':key
  }
  await sendRequest(serverAddress+'/savePath','POST',body);
  
}

