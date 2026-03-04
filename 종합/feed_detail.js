
ensureSeedLogin();

function getParam(name){
  const u = new URL(window.location.href);
  return u.searchParams.get(name);
}

const feedId = Number(getParam("id")) || MOCK.feeds[0].id;
const feed = MOCK.feeds.find(f=>f.id === feedId) || MOCK.feeds[0];

function hasLiked(){
  const uid = storage.get("userId");
  return uid ? (feed.likes||[]).includes(uid) : false;
}
function toggleLike(){
  if(!isLoggedIn()){
    alert("로그인이 필요합니다.");
    window.location.href = "login.html";
    return;
  }
  const uid = storage.get("userId");
  feed.likes = feed.likes || [];
  const i = feed.likes.indexOf(uid);
  if(i>=0) feed.likes.splice(i,1);
  else feed.likes.push(uid);
  render();
}

function escapeHtml(str){
  return String(str).replace(/[&<>"']/g, (m)=>({
    "&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;","'":"&#039;"
  }[m]));
}

function render(){
  const u = getUserById(feed.user_id);
  $("#dHead").innerHTML = `
    <img class="avatar" src="${u.profile_img_path}" alt="avatar" />
    <div class="info">
      <div class="name">${u.nickname}</div>
      <div class="time">${formatTimeAgo(feed.create_date)}</div>
    </div>
  `;
  $("#dImg").innerHTML = `<img src="${feed.image_path}" alt="feed"/>`;

  $("#dActions").innerHTML = `
    <button class="icon-btn" id="likeBtn">${iconHeart(hasLiked())} <span class="count">${feed.likes?.length||0}</span></button>
    <button class="icon-btn" id="chatBtn">${iconChat()} <span class="count">${feed.comments?.length||0}</span></button>
    <span class="hash"># ${MOCK.mission.content}</span>
  `;
  $("#likeBtn").addEventListener("click", toggleLike);
  $("#chatBtn").addEventListener("click", ()=> $("#dCommentInput").focus());

  const root = $("#dComments");
  root.innerHTML = "";
  (feed.comments||[]).forEach(c=>{
    const cu = getUserById(c.user_id);
    const row = document.createElement("div");
    row.className = "comment";
    row.innerHTML = `
      <img class="avatar" src="${cu.profile_img_path}" alt="av" />
      <div class="bubble">
        <div class="who">${cu.nickname} <span style="color:var(--muted); font-weight:800; font-size:11px;">· ${formatTimeAgo(c.create_date)}</span></div>
        <div class="txt">${escapeHtml(c.content)}</div>
      </div>
    `;
    root.appendChild(row);
  });
}
render();

function addComment(){
  if(!isLoggedIn()){
    alert("로그인이 필요합니다.");
    window.location.href = "login.html";
    return;
  }
  const txt = $("#dCommentInput").value.trim();
  if(!txt) return;
  feed.comments = feed.comments || [];
  feed.comments.push({ user_id: storage.get("userId"), content: txt, create_date: new Date().toISOString() });
  $("#dCommentInput").value = "";
  render();
}
$("#dSend").addEventListener("click", addComment);
$("#dCommentInput").addEventListener("keydown", (e)=>{ if(e.key==="Enter") addComment(); });
