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
  user = await sendRequest(window.serverAddress+'/check','POST',{});

  if ('id' in user){
    if (user['id'] !== 1){
      window.location.href = serverAddress+'/viewer/';
    }
  }
}
loadAdmin();
logOut.addEventListener('click',async function(event){
  await sendRequest(window.serverAddress+'/logout','POST',{});
  window.location.href = serverAddress+'/viewer/';
});
async function addRow(listId,inPut,type,database=null,init=false) {

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
      'type':type,
      'NoCaptcha':true,
    }
 
    database = await sendRequest(window.serverAddress+'/register','POST',database)
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
          ${editButton}
          ${userDetails}
          ${database['id'] !== 1 ? deleteButton : ''}
      </div>
      `;
  }else{

    
    const deleteButton = `<button class="btn btn-reject" data-user-id="${database['id']}" onclick="Delete(this,'x_user')" >Delete</button>`;
    const passButton = `<button class="btn btn-approve" data-user-id="${database['id']}" onclick="passUser(this)">Pass</button>`;

    newItem.innerHTML = `
        <div>
          <strong>User ID:</strong> <span class="user-id" id='user-${database['id']}'>${database['id']}</span>
          <strong>Username:</strong> <span id='username-${database['id']}'>${database['username']}</span>
          <strong>Password:</strong> <div id="password-${database['id']}" 
          data-username="${database['username']}" 
          onmouseover="showPassword(this)" onmouseout="hidePassword(this)" 
          style="display: inline-block; vertical-align: middle;">***********</div>
        </div>
        <button class="smallB" data-user-id="${database['id']}" onclick="toggleDetails(this,'x_user')">Edit</button>
        ${database['type'] !== "believe" ? passButton : ''}
        ${database['id'] !== 1 ? deleteButton : ''}
        <div class="user-details" id="x_user${database['id']}" style="display: none;">
            <form>
                <label for="username${database['id']}">New Username:</label>
                <input class='input' type="text" id="username${database['id']}" name="username">

                <label for="password${database['id']}">New Password:</label>
                <input class='input' type="password" id="password${database['id']}" name="password">

                <label for="confirmPassword${database['id']}">Confirm Password:</label>
                <input class='input' type="password" id="confirmPassword${database['id']}" name="confirmPassword">

                <button class='smallS' type="button" data-user-id="${database['id']}" data-type="${database['type']}" onclick="saveDetails(this,'x_user')">Save</button>
            </form>
        </div>

    `;
  }
  
  list.appendChild(newItem);
}

async function passUser(button) {
  var userId = button.dataset.userId;
  button.remove(); 
  await sendRequest(window.serverAddress+'/update','POST',
  {'table':'x_user','valueName':'type','value':'believe','columnName':'id','columnValue':userId})
  
}

async function init(){
  data = await sendRequest(window.serverAddress+'/query','POST',{'table':'x_domain'});
  delete data.farewell;

  for (let i = 0; i < data.length; i++) {
    if (data[i]['type'] === 'believe'){
      await addRow('list1','x_domain',data[i]['type'],data[i],true);
    }
    else if (data[i]['type'] === 'distrust'){
      await addRow('list2','x_domaind',data[i]['type'],data[i],true);
    }
  }

  data = await sendRequest(window.serverAddress+'/query','POST',{'table':'x_user'});
  delete data.farewell;
  for(let i = 0; i < data.length; i++){
    await addRow('list3','x_user',data[i]['type'],data[i],true);
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

async function saveDetails(container,inPut,type) {
  var userId = container.dataset.userId;
  var type = container.dataset.type;
  if (inPut === 'x_domain'){
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
    await sendRequest(window.serverAddress+'/update','POST',{'table':inPut,data:{'id':userId,'Domain':newDomain,'type':type}})
    document.getElementById("x_domain" + userId).textContent = newDomain;
    toggleDetails(null,'Domain',userId);
  }else if (inPut === 'x_user'){

    const username = document.getElementById("username" + userId).value;
    const password = document.getElementById("password" + userId).value;
    const confirmPassword = document.getElementById("confirmPassword" + userId).value;
    if (!username){
      alert('Username cannot be empty');
      return;
    }
    if (!password){
      alert('Password cannot be empty');
      return;
    }
    if (password !== confirmPassword){
      alert('Passwords do not match');
      return;
    }
    database = await sendRequest(window.serverAddress+'/query','POST',{'table':inPut,'username':username})

    if (database !== null){
      console.log(database['id'] == userId);
      if (database['id'] != userId)
      {
        alert('User already exists');
        return;
      }
    }
    await sendRequest(window.serverAddress+'/register','POST',
    {'id':userId,'username':username,'password':password,'type':type,'reset':true,'NoCaptcha':true})
    document.getElementById("password-" + userId).textContent = "*".repeat(password.length);
    document.getElementById("username-" + userId).textContent = username;
    document.getElementById("user-" + userId).textContent = userId;
    toggleDetails(null,inPut,userId);
  }

}


async function showPassword(container) {
  var username = container.dataset.username;
  console.log(username);
  var user = await sendRequest(window.serverAddress+'/query','POST',{'table':'x_user','username':username})

  container.textContent = user['password'];
}

async function hidePassword(container) {
  var username = container.dataset.username;
  var user = await sendRequest(window.serverAddress+'/query','POST',{'table':'x_user','username':username})

  var hiddenPassword = "*".repeat(user['password'].length);
  container.textContent = hiddenPassword;
}