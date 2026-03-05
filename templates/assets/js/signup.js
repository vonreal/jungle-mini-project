
$("#signupBtn").addEventListener("click", ()=>{
  const username = $("#username").value.trim();
  const pw1 = $("#password").value.trim();
  const pw2 = $("#password2").value.trim();
  const nick = $("#nickname").value.trim();

  const usernameMsg = $("#username-msg");
  const nicknameMsg = $("#nickname-msg");

  if(usernameMsg){ usernameMsg.textContent = ""; usernameMsg.className = "msg"; }
  if(nicknameMsg){ nicknameMsg.textContent = ""; nicknameMsg.className = "msg"; }

  if(!username || !pw1 || !pw2 || !nick){
    alert("모든 항목을 입력해주세요.");
    return;
  }
  if(pw1 !== pw2){
    alert("비밀번호가 일치하지 않습니다.");
    return;
  }

  const usernameExists = MOCK.users.some(u => u.username === username);
  if(usernameExists){
    if(usernameMsg){
      usernameMsg.textContent = "이미 사용중인 아이디입니다.";
      usernameMsg.className = "msg error";
    }
  }else{
    if(usernameMsg){
      usernameMsg.textContent = "사용 가능한 아이디입니다.";
      usernameMsg.className = "msg success";
    }
  }

  const nicknameExists = MOCK.users.some(u => u.nickname === nick);
  if(nicknameExists){
    if(nicknameMsg){
      nicknameMsg.textContent = "이미 사용중인 닉네임입니다.";
      nicknameMsg.className = "msg error";
    }
  }else{
    if(nicknameMsg){
      nicknameMsg.textContent = "사용 가능한 닉네임입니다.";
      nicknameMsg.className = "msg success";
    }
  }

  if(usernameExists || nicknameExists){
    return;
  }

  const newId = Math.max(...MOCK.users.map(u=>u.id))+1;
  MOCK.users.push({ id:newId, username, nickname:nick, profile_img_path:"assets/img/avatar.jpg" });

  storage.set("token", "mock-token");
  storage.set("userId", newId);
  storage.set("nickname", nick);

  window.location.href = "index.html";
});
