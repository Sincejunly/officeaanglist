

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
const id = document.querySelector('#id');
const SettingsC = document.querySelector('#SettingsC');
const PDFC = document.querySelector('#PDFC');
const pdfSetting = document.querySelector('#pdfSetting');
//const PDFDO = document.querySelector('#PDFDO');

const rotate = document.querySelector('#rotate');
const distort = document.querySelector('#distort');
const PDFmetadata = document.querySelector('#PDFmetadata');
const PDFCPU = document.querySelector('#PDFCPU');
const pdfType = document.querySelector('#pdfType');
let user;
const fileName = await getDomain('fileName');
const AListPath = await getDomain('AListPath');
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
    await getMyProfile(user);
  } catch (error) {
    console.error(error);
  }
}
SettingsC.addEventListener('click', async function() {
  window.location.href = serverAddress+'/user';
});
async function viewer() {
  isSubmitClicked = true;
  overlay.classList.remove('show-overlay');
  overlay.classList.add('hide-overlay');
  background.classList.add('background-fadeOut');
  await inDocEditor();
}

async function hideMode(){
    isSubmitClicked = true;
    overlay.classList.remove('show-overlay');
    overlay.classList.add('hide-overlay');
    background.classList.add('background-fadeOut');
    manageButton.style.display = 'block';
}
officeC.addEventListener('click',hideMode);
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

      if (!user['empty'] && !('username' in user)) {
        overlay.classList.remove('hide-overlay');
        overlay.classList.add('show-overlay');
        await showLogin();
      }
      else if( 'username' in user){
        if(user['disabled'] == 0){
          overlay.classList.remove('hide-overlay');
          overlay.classList.add('show-overlay');

          // if (fileName!=''){
          //   await viewer();
          // }
          if (user['username']!='guest')
          {
            await showUser();
          }
          else{
            await showLogin();
          }
          
          
        }else{
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
    var body = {'username':username,'password':password,'type':'distrust'};
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

    PDFC.style.display = 'block';
    //await getEventTypes(loginB,true);
    //loginB.addEventListener('click',loginOut);
    loginB.style.display = 'none';
    logOutB.style.display = 'block';
    logOutB.style.justifyContent = 'center';
    countB.style.display = 'none';
    registerB.style.display = 'none';
    countBox.style.display = 'none';

    
    if (user['id'] == 1){
      SettingsC.style.display = 'block';
    }
    // if (await getDomain('fileName')!=''){
    //   await viewer();
    // }

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

captchaImage.addEventListener('click',async () => {
  captchaImage.src = serverAddress+'/generate_code?' + "&timestamp=" + new Date().getTime();
});

async function isArabicNumber(value) {

  var regex = /^[0-9]+$/;
  
  return regex.test(value);
}

async function upPDF(event) {
  event.preventDefault();

  if(pdfSetting.style.display == 'none' || pdfSetting.style.display == ''){
    pdfSetting.style.display = 'inline-block';
    PDFC.textContent = 'UP';
  }
  else{
    pdfSetting.style.display = 'none';
    PDFC.textContent = 'PDF';

    const rotatec = rotate.checked ? ' --rotate-pages ': '';
    const distortc = distort.checked ? ' --deskew ': '';
    const PDFmetadatac = PDFmetadata.value ? ` --title ${PDFmetadata.value}`: '';
    const PDFCPUc = isArabicNumber(PDFCPU.value) ? ` --jobs ${PDFCPU.value}`: '';
    const pdfTypec = pdfType.value ? ` --output-type ${pdfType.value}`: '';
    const fileType = pdfTypec ? '.pdfa' : '.pdf';
    const cmd = rotatec + distortc + PDFmetadatac + PDFCPUc + pdfTypec;



    const ret = await sendRequest(serverAddress+'/orc','POST',{'id':user['id'],'fileName':fileName,
    'AListPath':AListPath,'fileType':fileType,'cmd':cmd});
      if ('Error' in ret){
        message.style.display = 'block';
        message.textContent = ret['Error'];
      }
      else{
        message.style.display = 'block';
        message.textContent = '转换成功';
      }
  }
}

PDFC.addEventListener('click',upPDF);
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