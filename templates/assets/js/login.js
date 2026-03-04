
$("#loginBtn").addEventListener("click", ()=>{
  const username = $("#username").value.trim();
  const password = $("#password").value.trim();

  const u = MOCK.users.find(x=>x.username === username) || MOCK.users[1];
  if(!username || !password){
    alert("아이디/비밀번호를 입력해주세요.");
    return;
  }

  storage.set("token", "mock-token");
  storage.set("userId", u.id);
  storage.set("nickname", u.nickname);

  window.location.href = "index.html";
});
