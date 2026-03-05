
ensureSeedLogin();


function getParam(name){

  const u = new URL(window.location.href);
  return u.searchParams.get(name);
}


const feedId = getParam("id") ?? String(MOCK.feeds[0].id);
const feed = MOCK.feeds.find(f => String(f.id) === String(feedId)) || MOCK.feeds[0];

function hasLiked(){

  const uid = storage.get("userId");
  return uid ? (feed.likes || []).map(String).includes(String(uid)) : false;
}

function toggleLike(){

  if(!isLoggedIn()){
    alert("로그인이 필요합니다.");
    window.location.href = "login.html";
    return;
  }
  const uid = storage.get("userId");
  feed.likes = feed.likes || [];
  const sUid = String(uid);
  const i = feed.likes.map(String).indexOf(sUid);
  if(i>=0) feed.likes.splice(i,1);
  else feed.likes.push(uid);
  render();
}

function deleteThisFeed(){

  if(!isLoggedIn()){
    alert("로그인이 필요합니다.");
    window.location.href = "login.html";
    return;
  }

  const uid = storage.get("userId");
  if(String(feed.user_id) !== String(uid)){
    alert("내 게시물만 삭제할 수 있습니다.");
    return;
  }

  if(!confirm("이 게시물을 삭제할까요?")) return;

  const idx = MOCK.feeds.findIndex(f => String(f.id) === String(feed.id));
  if(idx >= 0){
    MOCK.feeds.splice(idx, 1);
  }

  window.location.href = "index.html";
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
  (feed.comments||[]).forEach((c, idx)=>{ 

    if(!c._cid){
      const t = c.create_date ? new Date(c.create_date).getTime() : Date.now();
      c._cid = `${feed.id}-${t}-${idx}`;
    }

    const cu = getUserById(c.user_id);
    const row = document.createElement("div");
    row.className = "comment";
    row.dataset.cid = c._cid;

    const uid = storage.get("userId");
    const isMine = uid && (String(c.user_id) === String(uid));

    row.innerHTML = `
      <img class="avatar" src="${cu.profile_img_path}" alt="av" />
      <div class="bubble">
        <div class="who" style="display:flex; align-items:center; justify-content:space-between; gap:8px;">
          <div>
            ${cu.nickname}
            <span style="color:var(--muted); font-weight:800; font-size:11px;">· ${formatTimeAgo(c.create_date)}</span>
          </div>
          ${isMine ? `<button class="comment-del" type="button" title="댓글 삭제" aria-label="댓글 삭제" style="border:none; background:transparent; color:var(--muted); font-weight:900; cursor:pointer;">✕</button>` : ``}
        </div>
        <div class="txt">${escapeHtml(c.content)}</div>
      </div>
    `;
    root.appendChild(row);
  });
}

render();

const dComments = $("#dComments");
if(dComments){

  dComments.addEventListener("click", (e)=>{
    const btn = e.target.closest(".comment-del");
    if(!btn) return;

    if(!isLoggedIn()){
      alert("로그인이 필요합니다.");
      window.location.href = "login.html";
      return;
    }

    const row = btn.closest(".comment");
    const cid = row?.dataset?.cid;
    if(!cid) return;

    if(!confirm("이 댓글을 삭제할까요?")) return;

    const idx = (feed.comments||[]).findIndex(c => c._cid === cid);
    if(idx >= 0){
      (feed.comments||[]).splice(idx, 1);
    }
    render();
  });
}


const moreBtn = $("#detailMore");
if(moreBtn){

  moreBtn.addEventListener("click", deleteThisFeed);
}

function addComment(){

  if(!isLoggedIn()){
    alert("로그인이 필요합니다.");
    window.location.href = "login.html";
    return;
  }
  const txt = $("#dCommentInput").value.trim();
  if(!txt) return;
  feed.comments = feed.comments || [];
  feed.comments.push({ _cid: `${feed.id}-${Date.now()}-${Math.random().toString(16).slice(2)}`, user_id: Number(storage.get("userId")), content: txt, create_date: new Date().toISOString() });
  $("#dCommentInput").value = "";
  render();
}

$("#dSend").addEventListener("click", addComment);

$("#dCommentInput").addEventListener("keydown", (e)=>{ if(e.key==="Enter") addComment(); });
