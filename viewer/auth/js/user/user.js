let activeList = document.getElementById('list1'); // Initially set activeList to list1
let activeButton = null;
const button1 = document.getElementById('button1');
button1.classList.toggle('active');
const logOut = document.getElementById('logOut');
activeButton = button1;


async function toggleList(listId, buttonId) {
  const button = document.getElementById(buttonId);
  
  if (activeButton !== null && activeButton !== button) {
    activeButton.classList.remove('active');
  }

  button.classList.toggle('active');
  activeButton = button;

  const list = document.getElementById(listId);
  if (activeList === list) {
    return;
  }
 
  if (activeList !== null) {
    activeList.style.display = "none";
  }
  if (activeList !== list) {
    list.style.display = "flex";
    activeList = list;
  } 
  else {
    activeList = null;
  }
}
async function loadAdmin(){
  user = await sendRequest(window.serverAddress+'/check','POST');

  if ('id' in user){
    if (user['id'] !== 1){
      window.location.href = serverAddress+'/viewer/';
    }
  }else{
    window.location.href = serverAddress+'/viewer/';
  }
}
loadAdmin();
logOut.addEventListener('click',async function(event){
  await sendRequest(window.serverAddress+'/logout','POST',{});
  window.location.href = serverAddress+'/viewer/';
});
async function addRow(listId,inPut,type=0,database=null,init=false) {

  const list = document.getElementById(listId)
  const input = document.getElementById(inPut);
  
  const newItem = document.createElement("div");
  var password;
  var confirmPassword;
  if(!input.value && !init){
    return;
  }
  if((inPut === 'x_domain')||(inPut === 'x_domaind')){
    inPut = 'x_domain';
  }

  if(!init){
    if (inPut === 'x_domain'){
      database = await sendRequest(window.serverAddress+'/query','POST',{'table':inPut,'Domain':input.value})
      if (database !== null){
        alert('Domain already exists');
        return;
      }
    }else if (inPut === 'x_user'){
      password = document.getElementById('new-username').value;
      confirmPassword = document.getElementById("confirm-password").value;

      if (password !== confirmPassword){
        alert('Passwords do not match');
        return;
      }
      database = await sendRequest(window.serverAddress+'/query','POST',{'table':inPut,'username':input.value})
      if (database !== null){
        alert('User already exists');
        return;
      }
    }


  }
  
  var id = await sendRequest(window.serverAddress+'/query','POST',{'table':inPut, 'id':1})
  if (id === null){
    id = 1;
  }

  if (database === null && inPut === 'x_domain'){
    
    database = {
      'id':id + 1,
      'Domain':input.value,
      'type':type
    }

    await sendRequest(window.serverAddress+'/update','POST',{'table':'x_domain','Domain':database})

  }else if (database === null && inPut === 'x_user'){

    database = {
      'id':id + 1,
      'username':input.value,
      'password':password,
      'role':parseInt(type),
      'disabled':0,
      'permission':8,
      'otp_secret': '', 
      'sso_id': '',
      'showViewer':false
    }
  
    database = await sendRequest(window.serverAddress+'/ChangeUser','POST',database)
    
  }
 
  if (inPut === 'x_domain'){
 
    const editButton = `<button class='smallB' data-user-id="${database['id']}" onclick="toggleDetails(this,'Domain')">Edit</button>`;
    const userDetails = `
      <div class="Domain" id="Domain${database['id']}" style="display: none;">
          <form>
              <label for="x_domain-${database['id']}">newDomain:</label>
              <input class='input' type="text" id="x_domain_input${database['id']}" name="x_domain">
              <button class='smallS' type="button" data-user-id="${database['id']}" data-type="${database['type']}" onclick="saveDetails(this,'x_domain')">Save</button>
          </form>
      </div>
    `;
    const deleteButton = `<button class="btn btn-reject" data-user-id="${database['id']}" onclick="Delete(this,'x_domain')" >Delete</button>`;
    newItem.innerHTML = `
      <div>
          <strong>DOMAIN:</strong> <span class="Domain" id="x_domain${database['id']}">${database['Domain']}</span>
          ${editButton}${database['id'] !== 1 ? deleteButton : ''}
          ${userDetails}
      </div>
      `;
  }else{

    let disabledChecked='';
    let disabledC='';
    let combinations='';

    let permissiondChecked='';

    let permissiondC='';
    let showViewerChecked='';
    const deleteButton = `<button class="btn btn-reject" data-user-id="${database['id']}" onclick="Delete(this,'x_user')" >Delete</button>`;
    if(database['id'] === 1 && database['role'] === 2){
      disabledC = 'dropPorS';
      permissiondC = 'dropPorS';
    }else{
      disabledChecked = database['disabled'] === 0 ? 'checked' : ''
      disabledC = disabledChecked === '' ? 'dropPorD' : 'dropPorS'
      if (database['permission'] != 0){
        combinations = await find_combination(database['permission']) 

        permissiondChecked = combinations.some(combination => combination.includes(8)) ? 'checked' : ''
    
        permissiondC = permissiondChecked === '' ? 'dropPorD' : 'dropPorS'
      }else{
        permissiondC = 'dropPorD'

      }

    }


    const userPorBox = `
    <div class="userPorBox">
        <label for="disabled${database['id']}">
        启用账号
        <input type="checkbox" id="disabled${database['id']}" ${disabledChecked}>
        </label>
        <label for="editFile${database['id']}">
        可编辑文件
        <input type="checkbox" id="editFile${database['id']}" ${permissiondChecked}>
        </label>
    </div>`;

    newItem.innerHTML = `
        <div class="user-container">
          <strong>User ID:</strong> <span class="user-id" id='user-${database['id']}'>${database['id']}</span>
          <strong>Username:</strong> <span id='username-${database['id']}'>${database['username']}</span>
          <strong>Password:</strong> <div id="password-${database['id']}" 
          data-username="${database['username']}" 
          onmouseover="showPassword(this)" onmouseout="hidePassword(this)" 
          style="display: inline-block; vertical-align: middle;">${"*".repeat(database['password'].length)}</div>
        </div>
        <button class="smallB" data-user-id="${database['id']}" onclick="toggleDetails(this,'x_user')">Edit</button>
        <div class="porContainer">
          <div class="${disabledC}" id="disabledC${database['id']}"></div>
          <div class="${permissiondC}" id="permissiondC${database['id']}"></div>
        </div>
        ${database['id'] !== 1 && database['username'] !== 'guest' ? deleteButton : ''}
        <div class="user-details" id="x_user${database['id']}" style="display: none;">
            <form>
                <label for="username${database['id']}">New Username:</label>
                <input class='input' type="text" id="username${database['id']}" name="username">

                <label for="password${database['id']}">New Password:</label>
                <input class='input' type="password" id="password${database['id']}" name="password">

                <label for="confirmPassword${database['id']}">Confirm Password:</label>
                <input class='input' type="password" id="confirmPassword${database['id']}" name="confirmPassword">

                ${database['id'] !== 1 ? userPorBox : ''}
                <button class='smallS' type="button" data-user-id="${database['id']}" data-role="${database['role']}" onclick="saveDetails(this,'x_user')">Save</button>
            </form>
            <div class="userPer" id="userPer${database['id']}">

            </div>
        </div>

    `;
  }
  
  list.appendChild(newItem);
}

// async function passUser(button) {
//   var userId = button.dataset.userId;
//   button.remove(); 
//   await sendRequest(window.serverAddress+'/update','POST',
//   {'table':'x_user','valueName':'type','value':'believe','columnName':'id','columnValue':userId})
  
// }

async function init(){
  data = await sendRequest(window.serverAddress+'/query','POST',{'table':'x_domain'});

  for (let i = 0; i < data.length; i++) {
    if (data[i]['type'] === 'believe'){
      await addRow('list1','x_domain','',data[i],true);
    }
    else if (data[i]['type'] === 'distrust'){
      await addRow('list2','x_domaind','',data[i],true);
    }
  }

  data = await sendRequest(window.serverAddress+'/query','POST',{'table':'x_user'});
  delete data.farewell;

  for(let i = 0; i < data.length; i++){
    await addRow('list3','x_user','',data[i],true);
  }
}
init();
async function Delete(button,inPut) {
  var userId = button.dataset.userId;
  const rowToDelete = button.parentNode;
  const dataUserId = button.dataset.user_id;
  rowToDelete.parentNode.removeChild(rowToDelete);
  await sendRequest(window.serverAddress+'/delete','POST',{'table':inPut,'id':userId})
}



async function getUserId(button) {
  var userRow = button.closest(".user-row");
  var userIdElement = userRow.querySelector(".user-id");
  var userId = userIdElement ? userIdElement.textContent : null;
  return userId;
}

async function toggleDetails(container,inPut,id = null) {
  if(id)
  {
    var userId = id;
  }
  else{
    var userId = container.dataset.userId;
  }

  if (userId !== null) {

      var userDetails = document.getElementById(inPut + userId);
      var computedStyle = window.getComputedStyle(userDetails);

      if (computedStyle.display === "none") {
          userDetails.style.display = "block";
      } else {
          userDetails.style.display = "none";
      }
  }
}

async function saveDetails(container,inPut) {
  var userId = container.dataset.userId;
  let database = null;
  if (inPut === 'x_domain'){
    var type = container.dataset.type;
    var newDomain = document.getElementById("x_domain_input" + userId).value;
    if (!newDomain){
      alert('Domain cannot be empty');
      return;
    }
    database = await sendRequest(window.serverAddress+'/query','POST',{'table':inPut,'Domain':newDomain})
    if (database !== null){
      alert('Domain already exists');
      return;
    }
    await sendRequest(window.serverAddress+'/update','POST',{'table':inPut,'valueName':'id','value':userId,'columnName':'Domain','columnValue':newDomain})

    document.getElementById("x_domain" + userId).textContent = newDomain;
    toggleDetails(null,'Domain',userId);
  }else if (inPut === 'x_user'){
    
    var role = container.dataset.role;
    let username = document.getElementById("username" + userId).value;
    let password = document.getElementById("password" + userId).value;
    const confirmPassword = document.getElementById("confirmPassword" + userId).value;

    database = await sendRequest(window.serverAddress+'/query','POST',{'table':inPut,'username':username})
    if (database !== null){

      if (database['id'] != userId)
      {
        alert('User already exists');
        return;
      }
      
    }
    else{

      database = await sendRequest(window.serverAddress+'/query','POST',{'table':inPut,'id':userId,'username':username})
      
    }
 
    let permissionDA;
    let permissiond;
    let disabled;

    if(userId ==1){
      disabledd = false;
      permissiond = false;
      permissionDA = false;
      
    }
    else{
      disabled = document.getElementById("disabled" + userId).checked == true ? 0 : 1;

      const combinations = await find_combination(database['permission'])

      permissionDA = database['permission'] == 0 ? false:combinations.some(combination => combination.includes(8));
      
      const editFil = document.getElementById("editFile" + userId).checked
      
      permissiond = editFil == permissionDA ? false: true;

      disabledd = database['disabled'] == disabled ? false:true
    }


    
    let permissionI;
    if(permissiond && permissionDA){
      permissionI = database['permission'] - 8;
    }
    else if (permissiond && !permissionDA){
      permissionI = database['permission'] + 8;
    }
    else{
      permissionI = database['permission'];
    }

    if (password !== confirmPassword){
      alert('Passwords do not match');
      return;
    }

    if (!username && !permissiond && !disabledd){
     
        alert('Username cannot be empty');
        return;
      
    }
    if (!password && !permissiond && !disabledd){
     
        alert('Password cannot be empty');
        return;
    
    }

    // database['id'] = userId;
    // database['username'] = username;
    // database['password'] = password;
    // database['role'] = role;
    // database['disabled'] = disabled;
    // database['NoCaptcha'] = true;
    // database['otp_secret'] = '';
    // database['sso_id'] = '';
    // database['reset']='';

    database = {
      'id':userId,
      'username':username,
      'password':password,
      'role':parseInt(role),
      'disabled':disabled,
      'permission':permissionI,
      'otp_secret': '', 
      'sso_id': '',
      'reset':''
    }
  
    database = await sendRequest(window.serverAddress+'/ChangeUser','POST',
    database)
    
    document.getElementById("password-" + userId).textContent = "*".repeat(database['password'].length);
    document.getElementById("username-" + userId).textContent = database['username'];
    document.getElementById("user-" + userId).textContent = database['id'];
    if (database['id'] != 1)
    {
      document.getElementById("disabledC" + userId).className = disabled == 0 ? 'dropPorS' : 'dropPorD';
      document.getElementById("permissiondC" + userId).className = permissionI == 0 ? 'dropPorD' : 'dropPorS';
    }

    toggleDetails(null,inPut,userId);
  }

}


async function showPassword(container) {
  var username = container.dataset.username;

  var user = await sendRequest(window.serverAddress+'/query','POST',{'table':'x_user','username':username})

  container.textContent = user['password'];
}

async function hidePassword(container) {
  var username = container.dataset.username;
  var user = await sendRequest(window.serverAddress+'/query','POST',{'table':'x_user','username':username})

  var hiddenPassword = "*".repeat(user['password'].length);
  container.textContent = hiddenPassword;
}

