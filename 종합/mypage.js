
if(!requireAuth("login.html")) throw new Error("auth required");
ensureSeedLogin();

const u = currentUser() || MOCK.users[1];
$("#myNick").textContent = u.nickname;
$("#myAvatar").src = u.profile_img_path;

const myFeeds = MOCK.feeds.filter(f=>f.user_id === u.id);
$("#statPosts").textContent = String(myFeeds.length);
const receivedLikes = myFeeds.reduce((acc,f)=> acc + (f.likes?.length||0), 0);
$("#statLikes").textContent = String(receivedLikes);

const grid = $("#grid");
grid.innerHTML = "";
myFeeds.forEach(f=>{
  const a = document.createElement("a");
  a.href = "index.html"; 
  a.innerHTML = `<img src="${f.image_path}" alt="grid" />`;
  grid.appendChild(a);
});

$("#logoutBtn").addEventListener("click", ()=>{
  storage.del("token"); storage.del("userId"); storage.del("nickname");
  window.location.href = "index.html";
});
