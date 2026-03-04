
$("#signupBtn").addEventListener("click", ()=>{
  const username = $("#username").value.trim();
  const pw1 = $("#password").value.trim();
  const pw2 = $("#password2").value.trim();
  const nick = $("#nickname").value.trim();

  if(!username || !pw1 || !pw2 || !nick){
    alert("모든 항목을 입력해주세요.");
    return;
  }
  if(pw1 !== pw2){
    alert("비밀번호가 일치하지 않습니다.");
    return;
  }

  const newId = Math.max(...MOCK.users.map(u=>u.id))+1;
  MOCK.users.push({ id:newId, username, nickname:nick, profile_img_path:"assets/img/avatar.jpg" });

  storage.set("token", "mock-token");
  storage.set("userId", newId);
  storage.set("nickname", nick);

  window.location.href = "index.html";
});
