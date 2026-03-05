
const $ = (sel, root=document) => root.querySelector(sel);
const $$ = (sel, root=document) => Array.from(root.querySelectorAll(sel));

const storage = {
  get(key, fallback=null){
    try { const v = localStorage.getItem(key); return v ? JSON.parse(v) : fallback; } catch { return fallback; }
  },
  set(key, value){ localStorage.setItem(key, JSON.stringify(value)); },
  del(key){ localStorage.removeItem(key); },
};
//로그인 여부 판단 기준은 token
function isLoggedIn(){
  return !!storage.get("token");
}
//인증을 확인하고 아니라면 로그인창으로 이동
function requireAuth(redirectTo="login.html"){
  if(!isLoggedIn()){
    window.location.href = redirectTo;
    return false;
  }
  return true;
}
//시간 표시 게시물 시간 등록
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
//오늘 날짜
function todayK(){
  const d = new Date();
  const mm = String(d.getMonth()+1).padStart(2,"0");
  const dd = String(d.getDate()).padStart(2,"0");
  return `${d.getFullYear()}.${mm}.${dd}`;
}
//뒤로가기 기능
function navBack(fallback="index.html"){
  if(history.length > 1) history.back();
  else window.location.href = fallback;
}
//오늘의 챌린지 오전9시 초기화 설정
function startChallengeTimer(opts = {}){
  const timerEl = document.getElementById("challengeTimer");
  if(!timerEl) return;

  const cutoffHour = Number.isFinite(opts.cutoffHour) ? opts.cutoffHour : 9;

  const challengeDateKey = (d=new Date()) => {
    const x = new Date(d);
    const cutoff = new Date(x);
    cutoff.setHours(cutoffHour,0,0,0);
    if(x < cutoff) cutoff.setDate(cutoff.getDate() - 1); 
    const yy = cutoff.getFullYear();
    const mm = String(cutoff.getMonth()+1).padStart(2,"0");
    const dd = String(cutoff.getDate()).padStart(2,"0");
    return `${yy}-${mm}-${dd}`;
  };

  const nextCutoff = (now=new Date()) => {
    const t = new Date(now);
    t.setHours(cutoffHour,0,0,0);
    if(now >= t) t.setDate(t.getDate()+1);
    return t;
  };

  let lastKey = storage.get("challengeDateKey", null) || challengeDateKey(new Date());
  storage.set("challengeDateKey", lastKey);

  function render(){
    const now = new Date();
    const target = nextCutoff(now);
    let diff = target.getTime() - now.getTime();
    if(diff < 0) diff = 0;

    const h = Math.floor(diff / (1000*60*60));
    const m = Math.floor((diff % (1000*60*60)) / (1000*60));
    const s = Math.floor((diff % (1000*60)) / 1000);

    timerEl.textContent = `${String(h).padStart(2,"0")}:${String(m).padStart(2,"0")}:${String(s).padStart(2,"0")} 챌린지 종료까지 남은 시간`;

    const keyNow = challengeDateKey(now);
    if(keyNow !== lastKey){
      storage.set("challengeDateKey", keyNow);
      window.location.reload();
    }
  }

  render();
  setInterval(render, 1000);
}

window.startChallengeTimer = startChallengeTimer;

document.addEventListener("DOMContentLoaded", () => startChallengeTimer({ cutoffHour: 9 }));
