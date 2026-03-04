
const $ = (sel, root=document) => root.querySelector(sel);
const $$ = (sel, root=document) => Array.from(root.querySelectorAll(sel));

const storage = {
  get(key, fallback=null){
    try { const v = localStorage.getItem(key); return v ? JSON.parse(v) : fallback; } catch { return fallback; }
  },
  set(key, value){ localStorage.setItem(key, JSON.stringify(value)); },
  del(key){ localStorage.removeItem(key); },
};

function isLoggedIn(){
  return !!storage.get("token");
}

function requireAuth(redirectTo="login.html"){
  if(!isLoggedIn()){
    window.location.href = redirectTo;
    return false;
  }
  return true;
}

function formatTimeAgo(iso){
  const t = new Date(iso).getTime();
  const diff = Date.now() - t;
  const m = Math.floor(diff/60000);
  if(m < 1) return "방금 전";
  if(m < 60) return `${m}분 전`;
  const h = Math.floor(m/60);
  if(h < 24) return `${h}시간 전`;
  const d = Math.floor(h/24);
  return `${d}일 전`;
}

function todayK(){
  const d = new Date();
  const mm = String(d.getMonth()+1).padStart(2,"0");
  const dd = String(d.getDate()).padStart(2,"0");
  return `${d.getFullYear()}.${mm}.${dd}`;
}

function navBack(fallback="index.html"){
  if(history.length > 1) history.back();
  else window.location.href = fallback;
}
