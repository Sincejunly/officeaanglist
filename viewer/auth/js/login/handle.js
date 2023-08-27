

// 获取所需的元素
const overlay = document.getElementById('overlay');
const manageButton = document.getElementById('manage-button');
const usernameInput = document.getElementById('username-input');
const passwordInput = document.getElementById('password-input');
const confirmPasswordInput = document.getElementById('confirm-password-input');

const loginB = document.getElementById('loginB');
const registerB = document.getElementById('registerB');
const countB = document.getElementById('countB');
const logOutB = document.getElementById('logOutB');

const placeholder = document.getElementById('placeholder');
const registerC = document.getElementById('registerC');
const loginC = document.getElementById('loginC');
var loginForm = document.getElementById('login-form');

let isSubmitClicked = false;
let manageButtonClicked = false;
var turnpassword;
var password;
const titleElement = document.querySelector('#overlay-content h2');
const background = document.querySelector('.background-image')
const message = document.querySelector('#message');
const captchaInput = document.querySelector('#captchaInput');
const captchaImage = document.querySelector('#captchaImage');
const forgotC = document.querySelector('#forgotC');
const AriaNgC = document.querySelector('#AriaNgC');
const officeC = document.querySelector('#OfficeC');
const textPassword = document.querySelector('#textPassword');
const countBox = document.querySelector('#countBox');
const Commd = document.querySelector('#Commd');

const SettingsC = document.querySelector('#SettingsC');
const PDFC = document.querySelector('#PDFC');
const pdfSetting = document.querySelector('#pdfSetting');
const upPDFC = document.querySelector('#upPDFC');

const rotate = document.querySelector('#rotate');
const distort = document.querySelector('#distort');
const PDFmetadata = document.querySelector('#PDFmetadata');
const PDFCPU = document.querySelector('#PDFCPU');
const pdfType = document.querySelector('#pdfType');
const showViewerBox = document.querySelector('#showViewerBox');
const showViewerCB = document.querySelector('#showViewerCB');
let user;
let fileName = '';
let fileExtension = '';
let key = '';
//var closebButton = document.querySelector('.close-button');

// var xPath = document.getElementById('x');

// const mysqlAddress = serverAddress+':3306'
// const redisAddress = serverAddress+':6379'

// xPath.addEventListener('mouseover', function() {
//   xPath.style.fill = 'white'; 
// });

// xPath.addEventListener('mouseout', function() {
//   xPath.style.fill = 'black'; 
// });


async function inDocEditor(){
  try {
    placeholder.classList.add('placeholder-fadeIn');
    //console.log(user,fileName,fileExtension,key);
    await getMyProfile(user,fileName,fileExtension,key);
  } catch (error) {
    console.error(error);
  }
}
SettingsC.addEventListener('click', async function() {
  window.location.href = serverAddress+'/user';
});
async function viewer() {
  isSubmitClicked = true;
  if(fileName == ""){
    alert("没有文件呀！")
    return 1;
  }

  overlay.classList.remove('show-overlay');
  overlay.classList.add('hide-overlay');
  background.classList.add('background-fadeOut');
  manageButton.style.display = 'block';
  await inDocEditor();
}


officeC.addEventListener('click',viewer);
// xPath.addEventListener('click', async function() {
//     isSubmitClicked = true;
//     overlay.classList.remove('show-overlay');
//     overlay.classList.add('hide-overlay');
//     background.classList.add('background-fadeOut');
//     await inDocEditor();
// });

document.addEventListener("DOMContentLoaded", async function() {
    await fetchData();
    //xPath.style.display = 'none';
});



async function fetchData() {
    try {
      user = await sendRequest(serverAddress+'/check','GET');
      fileName = await getDomain('fileName');
      if(fileName != ''){
        const AListPath = await getDomain('AListPath');
        fileExtension = fileName.split('.').pop();
        const body = {
          "username": user['username'],
          "AListPath": AListPath,
          'fileName': fileName,
        }
        
        key = await sendRequest(serverAddress+'/AListPath','POST',body);
        key = key['key'];
        
    }
    
    if (!user['empty'] && !('username' in user)) {
        overlay.classList.remove('hide-overlay');
        overlay.classList.add('show-overlay');
        await showLogin();
      }
      else if( 'username' in user){
        if(user['disabled'] == 0){
          overlay.classList.remove('hide-overlay');
          overlay.classList.add('show-overlay');
          
          if (user['username']!='guest' && !user['showViewer'])
          {
       
            await showUser();
          }
          else if(user['showViewer'] && fileName){
            
            await showLogin();
            await viewer();
          }
          else{
            overlay.classList.remove('hide-overlay');
            overlay.classList.add('show-overlay');
            await showLogin();
          }
          
          
        }else{
          overlay.classList.remove('hide-overlay');
          overlay.classList.add('show-overlay');
          await showLogin();
        }
   
      }
      else{
        overlay.classList.remove('hide-overlay');
        overlay.classList.add('show-overlay');
        await showRegister();
      }
    } catch (error) {
      overlay.classList.remove('hide-overlay');
      overlay.classList.add('show-overlay');
      console.error('Error:', error);
    }
}

async function register(event) {
  try {
    event.preventDefault();
    password = passwordInput.value;
    const confirmPassword = confirmPasswordInput.value;
    const username = usernameInput.value;
    const captcha = captchaInput.value;
    if (password !== confirmPassword) {
      message.style.display = 'block';
      message.textContent = '两次密码不一致';
      return;
    }
    const msg = await sendRequest(serverAddress+'/checkUser','POST',{'username':username});
    if(msg['whether'] == true){
      alert('用户已存在！');
      return;
    }
    var id = await sendRequest(window.serverAddress+'/checkUser','POST',{'id':1})
    if (id === null){
      id = 1;
    }
    else{
      id = id['id']
    }

    var body = {
    'id':id+1,
    'username':username,
    'password':password,
    'role':0,
    'disabled':1,
    'permission':0,
    'otp_secret':'',
    'sso_id':'',
    'showViewer':File
    };
 
    if (captcha){
      body['Captcha'] = captcha;
    }
    else{
 
      message.style.display = 'block';
      message.textContent = '请输入验证码';
      return;
    }
  
    user = await sendRequest(serverAddress+'/register','POST',body);
    
    if('id' in user)
    {
      alert('注册成功');
      captchaInput.value = '';
      await showLogin();
    }
    else{
      message.style.display = 'block';
      message.textContent = user['Error'];
    }
  } catch (error) {
    console.error('Error:', error);
  }
}
async function getEventListeners(element) {
  if (!element.__eventListeners) {
    element.__eventListeners = {};
  }
  return element.__eventListeners;
}

async function getEventTypes(element,remove=false) {
  var eventTypes = [];
  var events = await getEventListeners(element);
  
  for (var eventType in events) {
    eventTypes.push(eventType);
    if (remove) {
      element.removeEventListener(eventType, null);
    }
  }
  
  return eventTypes;
}


async function showRegister(){

  try {
    //await getEventTypes(loginB,true);
    //loginB.removeEventListener('click',login);
    //loginB.addEventListener('click',register);
    loginB.style.display = 'none';
    registerB.style.display = 'block';
    //registerB.style.justifyContent = 'center';
    countB.style.display = 'none';
    logOutB.style.display = 'none';
    countBox.style.display = 'none';

    confirmPasswordInput.style.display = 'block';
    forgotC.style.display = 'none';
    loginB.textContent = '注册';
    registerC.style.display = 'none';
    loginC.style.display = 'block';
    captchaInput.style.display = 'block';
    captchaImage.style.display = 'block';
    message.style.display = 'none';
    //textPassword.style.display = 'none';
    captchaImage.src = serverAddress+'/generate_code?' + "&timestamp=" + new Date().getTime();
  } catch (error) {
    console.error('Error:', error);
  }
}
loginB.addEventListener('click',login);
registerB.addEventListener('click',register);
countB.addEventListener('click',count);
logOutB.addEventListener('click',loginOut);

async function showLogin(){

  try {
    //await getEventTypes(loginB,true);
    

    loginB.style.display = 'block';
    logOutB.style.justifyContent = 'center';
    logOutB.style.display = 'none';
    countB.style.display = 'none';
    registerB.style.display = 'none';
    countBox.style.display = 'none';

    confirmPasswordInput.style.display = 'none';
    titleElement.textContent = 'Homura🍇';
    id.style.display = 'none';

    loginB.textContent = '验证';
    forgotC.style.display = 'block';
    registerC.style.display = 'block';
    passwordInput.style.display = 'block';
    usernameInput.style.display = 'block';
    message.style.display = 'none';

    loginC.style.display = 'none';
    captchaInput.style.display = 'none';
    captchaImage.style.display = 'none';
    showViewerBox.style.display = 'none';
  }
  catch (error) {
    console.error('Error:', error);
  }

}

async function count(event){
  try {
    event.preventDefault();
    
    const username = usernameInput.value;
    const password = passwordInput.value;
    
    const has = await sendRequest(serverAddress+'/count','POST',{'password':password});
    const coomd = `sudo docker exec officeaanglist python3 init.py -u ${username} -p ${has}`;
    Commd.style.display = 'block';
    Commd.textContent = coomd;
  }
  catch (error) {
  }
}

async function showForgot(){
  //loginB.removeEventListener('click',login);
  //await getEventTypes(loginB,true);
  //loginB.addEventListener('click',count);

  loginB.style.display = 'none';
  logOutB.style.display = 'none';
  countB.style.display = 'block';
  registerB.style.display = 'none';
  countBox.style.display = 'none';
  message.style.display = 'none';

  usernameInput.style.display = 'block';
  passwordInput.style.display = 'block';
  loginB.textContent = '计算';
  //textPassword.style.display = 'block';
  forgotC.style.display = 'none';
  registerC.style.display = 'block';
  loginC.style.display = 'block';
  confirmPasswordInput.style.display = 'none';
  countBox.style.display = 'block';
}

async function showUser() {
  try {
    passwordInput.style.display = 'none';
    confirmPasswordInput.style.display = 'none';
    //xPath.style.display = 'block';
    usernameInput.style.display = 'none';
    captchaImage.style.display = 'none';
    captchaInput.style.display = 'none';
    registerC.style.display = 'none';
    titleElement.textContent = user['username']+' 欢迎回来！';
    id.style.display = 'block';
    id.textContent = 'ID: '+ user['id'];

    forgotC.style.display = 'none';
    message.style.display = 'none';
    loginC.style.display = 'none';
    AriaNgC.style.display = 'block';
    officeC.style.display = 'block';
    loginB.textContent = '登出';

    
    //await getEventTypes(loginB,true);
    //loginB.addEventListener('click',loginOut);
    loginB.style.display = 'none';
    logOutB.style.display = 'block';
    logOutB.style.justifyContent = 'center';
    countB.style.display = 'none';
    registerB.style.display = 'none';
    countBox.style.display = 'none';
    showViewerBox.style.display= 'inline-block'
    console.log(user);
    if (user['showViewer']){
      showViewerCB.checked = true;
    }


    if (user['id'] == 1){
      SettingsC.style.display = 'block';
      PDFC.style.display = 'block';
    }


    //xPath.style.display = 'block';
  } catch (error) {
    console.error('Error:', error);
  }
}

  manageButton.addEventListener('click',async () => {
    placeholder.style.backgroundColor = 'rgb(176, 196, 222)';
    overlay.style.backgroundColor = 'rgb(176, 196, 222)';
    background.classList.remove('background-fadeOut');
    manageButtonClicked = true;
    overlay.classList.remove('hide-overlay');
    overlay.classList.add('show-overlay');
    
});
showViewerCB.addEventListener('click',async () =>{
  if(showViewerCB.checked){
    const body = {
      'id':user['id'],
      'username':'',
      'reset':true,
      'showViewer':true
    }
    await sendRequest(serverAddress+'/ChangeUser','POST',body);
  }
  else{
    const body = {
      'id':user['id'],
      'username':'',
      'reset':true,
      'showViewer':false
    }
    await sendRequest(serverAddress+'/ChangeUser','POST',body);

  }
});
captchaImage.addEventListener('click',async () => {
  captchaImage.src = serverAddress+'/generate_code?' + "&timestamp=" + new Date().getTime();
});

async function isArabicNumber(value) {

  var regex = /^[0-9]+$/;
  
  return regex.test(value);
}

async function connectWebSocket(body) {
    const socket = new WebSocket(webSocketAddress+'/orc');
    message.style.display='block';
    socket.onopen = async () => {
        //const dataToSend = { command: "install", package: "torch" };
        socket.send(JSON.stringify(body));
        //message.textContent="开始转换！"
    };
    socket.onmessage = async event => {
        const msg = event.data;

        if (msg instanceof Blob) {
            const text = await blobToText(msg);
            message.textContent = text;
        } else if (typeof msg === "string") {
            message.textContent = msg;
        } else {
            console.error("Unknown message type:", msg);
        }
    };
    socket.onclose = () => {
      message.textContent="完成！"
    };

    async function blobToText(blob) {
        const reader = new FileReader();

        return new Promise((resolve, reject) => {
            reader.onload = () => resolve(reader.result);
            reader.onerror = reject;
            reader.readAsText(blob);
        });
    }

    // function appendToOutput(text) {
    //     message.textContent = text;
    //     // const newLine = document.createElement("p");
    //     // newLine.textContent = text;
    //     // outputDiv.appendChild(newLine);
    // }

    // socket.onclose = () => {
    //     // const newLine = document.createElement("p");
    //     // newLine.textContent = "WebSocket closed.";
    //     // outputDiv.appendChild(newLine);
    // };
}
async function upPDF(event){
    event.preventDefault();
    pdfSetting.style.display = 'none';
    PDFC.textContent = 'PDF';
    const fileName = await getDomain('fileName');
    const AListPath = await getDomain('AListPath');
    const rotatec = rotate.checked ? ' --rotate-pages ': '';
    const distortc = distort.checked ? ' --deskew ': '';
    const PDFmetadatac = PDFmetadata.value ? ` --title ${PDFmetadata.value}`: '';
    const PDFCPUc = await isArabicNumber(PDFCPU.value) ? ` --jobs ${PDFCPU.value}`: '';
    const pdfTypec = pdfType.value ? ` --output-type ${pdfType.value}`: '';
    const fileType = pdfTypec ? '.pdfa' : '.pdf';
    const cmd = rotatec + distortc + PDFmetadatac + PDFCPUc + pdfTypec + '--skip-text';

    const body = {'id':user['id'],'fileName':fileName,
    'AListPath':AListPath,'fileType':fileType,'cmd':cmd}
    
    await connectWebSocket(body);
    
}

upPDFC.addEventListener('click',upPDF);

async function showPDFSetting(event) {
  event.preventDefault();
  console.log(pdfSetting.style.display);
  if(pdfSetting.style.display == 'none' || pdfSetting.style.display == ''){
    pdfSetting.style.display = 'inline-block';
    PDFC.textContent = '取消捏';
  }
  else{
    pdfSetting.style.display = 'none';
    PDFC.textContent = 'PDF';
    
  }
}

PDFC.addEventListener('click',showPDFSetting);
//PDFDO.addEventListener('click',upPDF);

async function login(event) {
    try {
      event.preventDefault();
      // turnpassword = await queryData(value='password');
      password = passwordInput.value;
      const confirmPassword = confirmPasswordInput.value;
      const username = usernameInput.value;
      const captcha = captchaInput.value;
      var body = {'username':username,'password':password,'userAgent':navigator.userAgent};
      if (captcha){
        body['Captcha'] = captcha;
      }
      user = await sendRequest(serverAddress+'/login','POST',body);

      if ('Captcha' in user) {
        captchaInput.style.display = 'block';
        captchaImage.style.display = 'block';
        captchaImage.src = serverAddress+'/generate_code?' + "&timestamp=" + new Date().getTime();
      }

      if('Error' in user){
        message.style.display = 'block';
        message.textContent = user['Error'];
      }
      else{
        await showUser();
      }
  } catch (error) {
      console.error('Error:', error);
  }
}
async function loginOut(event) {
  event.preventDefault();
  //alert('登出成功');
  await sendRequest(serverAddress+'/logout','POST',{});
  location.reload();
  await getEventTypes(loginB,true);
  loginB.addEventListener('click',login);
  await showLogin();
}
loginB.addEventListener('click',login);