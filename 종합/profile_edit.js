
if(!requireAuth("login.html")) throw new Error("auth required");
ensureSeedLogin();

const u = currentUser() || MOCK.users[1];
const nickInput = $("#nickname");
const avatarPrev = $("#avatarPrev");
nickInput.value = u.nickname;
avatarPrev.src = u.profile_img_path;

const avatarFile = $("#avatarFile");
$("#avatarReset").addEventListener("click", ()=>{
  avatarPrev.src = "assets/img/avatar.jpg";
});

avatarFile.addEventListener("change", ()=>{
  const f = avatarFile.files?.[0];
  if(!f) return;
  const url = URL.createObjectURL(f);
  avatarPrev.src = url;
});

$("#doneBtn").addEventListener("click", ()=>{
  const newNick = nickInput.value.trim();
  if(!newNick){
    alert("닉네임을 입력해주세요.");
    return;
  }
  u.nickname = newNick;
  u.profile_img_path = avatarPrev.src;
  storage.set("nickname", newNick);

  alert("프로필 수정 완료! (목업)");
  window.location.href = "mypage.html";
});
