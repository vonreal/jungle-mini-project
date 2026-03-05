
if(!requireAuth("login.html")) throw new Error("auth required");

ensureSeedLogin();

function escapeHtml(str){
  return String(str).replace(/[&<>"']/g, (m)=>({
    "&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#039;"
  }[m]));
}

const me = currentUser();
if(!me){
  window.location.href = "login.html";
}
function myFeeds(){
  const uid = storage.get("userId");
  return (MOCK.feeds || []).filter(f => f.user_id === uid);
}
function calcReceivedLikes(feeds){
  return (feeds || []).reduce((sum, f) => sum + ((f.likes && f.likes.length) ? f.likes.length : 0), 0);
}
function renderProfile(){
  const u = currentUser();
  $("#myNick").textContent = u?.nickname || "사용자";
  $("#myAvatar").src = u?.profile_img_path || "assets/img/avatar.jpg";
}

function renderStats(){
  const feeds = myFeeds();
  $("#statPosts").textContent = String(feeds.length);
  $("#statLikes").textContent = String(calcReceivedLikes(feeds));
}

function deleteMyFeed(feedId){
  const uid = storage.get("userId");
  const feed = MOCK.feeds.find(f => f.id === feedId);

  if(!feed){
    alert("게시물을 찾을 수 없습니다.");
    return;
  }
  if(feed.user_id !== uid){
    alert("내 게시물만 삭제할 수 있습니다.");
    return;
  }
  if(!confirm("이 게시물을 삭제할까요?")) return;

  const idx = MOCK.feeds.findIndex(f => f.id === feedId);
  if(idx >= 0){
    MOCK.feeds.splice(idx, 1);
  }
  render();
}

function goDetail(feedId){
  window.location.href = `feed_detail.html?id=${encodeURIComponent(feedId)}`;
}

function renderGrid(){
  const grid = $("#grid");
  const feeds = myFeeds();
  
  grid.innerHTML = "";
  
  feeds.forEach(feed => {
    const item = document.createElement("div");
    item.className = "grid-item";
    item.style.position = "relative";
    item.innerHTML = `
      <img src="${escapeHtml(feed.image_path)}" alt="내 피드" style="width:100%; aspect-ratio:1/1; object-fit:cover; border-radius:14px;" />
      <button class="mypage-del" aria-label="삭제"
        style="position:absolute; top:8px; right:8px; width:28px; height:28px; border:none; border-radius:999px;
               background: rgba(17,24,39,.65); color:#fff; font-size:18px; cursor:pointer; line-height:28px;">
        ✕
      </button>
    `;
    item.querySelector("img").addEventListener("click", ()=> goDetail(feed.id));

    item.querySelector(".mypage-del").addEventListener("click", (e)=>{
      e.stopPropagation();
      deleteMyFeed(feed.id);
    });

    grid.appendChild(item);
  });

  if(feeds.length === 0){
    const empty = document.createElement("div");
    empty.style.color = "var(--muted)";
    empty.style.fontWeight = "800";
    empty.style.fontSize = "13px";
    empty.style.padding = "20px 4px";
    empty.textContent = "아직 올린 피드가 없어요. 홈에서 인증샷을 올려보세요!";
    grid.appendChild(empty);
  }
}

function render(){
  renderProfile();
  renderStats();
  renderGrid();
}
$("#logoutBtn").addEventListener("click", ()=>{
  if(confirm("로그아웃 할까요?")){
    storage.del("token");
    storage.del("userId");
    storage.del("nickname");
    window.location.href = "index.html";
  }
});
render();
