
ensureSeedLogin();

const todayText = $("#todayText");
todayText.textContent = `${todayK()}  ·  오늘`;

const topActions = $("#topActions");
const fab = $("#fab");
fab.innerHTML = iconCamera();

const fabTop = $("#fabTop");

function renderTop(){
  topActions.innerHTML = "";
  if(isLoggedIn()){
    const u = currentUser();
    const img = document.createElement("img");
    img.className = "avatar";
    img.src = u?.profile_img_path || "assets/img/avatar.jpg";
    img.alt = "프로필";
    img.style.cursor = "pointer";
    img.addEventListener("click", ()=> window.location.href="mypage.html");
    topActions.appendChild(img);
  }else{
    const login = document.createElement("button");
    login.className = "pill primary";
    login.textContent = "로그인";
    login.onclick = ()=> window.location.href="login.html";

    const signup = document.createElement("button");
    signup.className = "pill";
    signup.textContent = "가입하기";
    signup.onclick = ()=> window.location.href="signup.html";

    topActions.appendChild(login);
    topActions.appendChild(signup);
  }
}
renderTop();

$("#dayPill").textContent = `Day ${MOCK.mission.day}`;
$("#missionTitle").textContent = MOCK.mission.content;
$("#missionDate").textContent = `${todayK()} · 챌린지`;
$("#missionParticipants").textContent = `+ ${MOCK.mission.participants}명 참여중`;

const loginCta = $("#loginCta");
const ctaGoLogin = $("#ctaGoLogin");

ctaGoLogin.addEventListener("click", ()=> window.location.href="login.html");

function showLoginCta(){
  if(!isLoggedIn()) loginCta.classList.add("show");
}
function hideLoginCta(){ loginCta.classList.remove("show"); }

fab.addEventListener("click", ()=>{
  if(!isLoggedIn()){
    showLoginCta();
    return;
  }
  window.location.href = "create.html";
});

let sortMode = "latest";
$$(".tab", $("#tabs")).forEach(t=>{
  t.addEventListener("click", ()=>{
    $$(".tab", $("#tabs")).forEach(x=>x.classList.remove("active"));
    t.classList.add("active");
    sortMode = t.dataset.sort;
    renderFeed();
  });
});

function feedSorted(){
  const feeds = [...MOCK.feeds];
  if(sortMode === "likes"){
    feeds.sort((a,b)=> (b.likes?.length||0) - (a.likes?.length||0));
  }else if(sortMode === "comments"){
    feeds.sort((a,b)=> (b.comments?.length||0) - (a.comments?.length||0));
  }else{
    feeds.sort((a,b)=> new Date(b.create_date) - new Date(a.create_date));
  }
  return feeds;
}

function hasLiked(feed){
  const uid = storage.get("userId");
  if(!uid) return false;
  return (feed.likes||[]).includes(uid);
}

function toggleLike(feedId){
  if(!isLoggedIn()){
    showLoginCta();
    return;
  }
  const uid = storage.get("userId");
  const feed = MOCK.feeds.find(f=>f.id===feedId);
  feed.likes = feed.likes || [];
  const idx = feed.likes.indexOf(uid);
  if(idx >= 0) feed.likes.splice(idx,1);
  else feed.likes.push(uid);
  renderFeed();
}

function goDetail(feedId){
  window.location.href = `feed_detail.html?id=${encodeURIComponent(feedId)}`;
}

function renderFeed(){
  const root = $("#feedList");
  root.innerHTML = "";
  const feeds = feedSorted();
  feeds.forEach(feed=>{
    const u = getUserById(feed.user_id);
    const card = document.createElement("article");
    card.className = "feed-card";
    card.innerHTML = `
      <div class="feed-head">
        <img class="avatar" src="${u.profile_img_path}" alt="avatar" />
        <div class="info">
          <div class="name">${u.nickname}</div>
          <div class="time">${formatTimeAgo(feed.create_date)}</div>
        </div>
      </div>

      <div class="feed-img" role="button" tabindex="0">
        <img src="${feed.image_path}" alt="feed image" />
      </div>

      <div class="actions">
        <button class="icon-btn like-btn">${iconHeart(hasLiked(feed))} <span class="count">${feed.likes?.length||0}</span></button>
        <button class="icon-btn chat-btn">${iconChat()} <span class="count">${feed.comments?.length||0}</span></button>
        <span class="hash"># ${MOCK.mission.content}</span>
      </div>
    `;
    $(".feed-img", card).addEventListener("click", ()=> goDetail(feed.id));
    $(".chat-btn", card).addEventListener("click", ()=> goDetail(feed.id));
    $(".like-btn", card).addEventListener("click", (e)=>{ e.stopPropagation(); toggleLike(feed.id); });
    root.appendChild(card);
  });
}
renderFeed();


const app = document.querySelector(".app");
app.addEventListener("scroll", onScroll);
window.addEventListener("scroll", onScroll); 

function onScroll(){
  const y = app.scrollTop || window.scrollY || 0;
  if(y > 260) fabTop.classList.add("show");
  else fabTop.classList.remove("show");
}
fabTop.addEventListener("click", ()=>{
  if(app.scrollTo) app.scrollTo({top:0, behavior:"smooth"});
  window.scrollTo({top:0, behavior:"smooth"});
});

document.addEventListener("click", (e)=>{
  if(!loginCta.classList.contains("show")) return;
  const inside = loginCta.contains(e.target) || e.target === fab;
  if(!inside) hideLoginCta();
});
