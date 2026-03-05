//업로드 페이지 로그인하지 않으면 로그인 페이지로 이동
if(!requireAuth("login.html")) throw new Error("auth required");
//오늘 미션
$("#tagText").textContent = MOCK.mission.content;
//피드영역
const file = $("#file");
const drop = $("#drop");
const preview = $("#preview");
const previewImg = $("#previewImg");
//미리보기 교체
function showPreview(src){

  drop.classList.add("hidden");
  preview.style.display = "block";
  previewImg.src = src;
}

//사진 변경
drop.addEventListener("click", ()=> file.click());

file.addEventListener("change", ()=>{
  const f = file.files?.[0];
  if(!f) return;
  const url = URL.createObjectURL(f);
  showPreview(url);
});

$("#submitBtn").addEventListener("click", ()=>{
  const u = currentUser();
  const imgSrc = previewImg.src || "assets/img/feed2.jpg";
//좋아요 댓글 유저확인
  const newId = Math.max(...MOCK.feeds.map(f=>f.id))+1;
  MOCK.feeds.unshift({
    id:newId,
    mission_id: MOCK.mission.id,
    user_id: u.id,
    create_date: new Date().toISOString(),
    likes: [],
    comments: [],
    image_path: imgSrc
  });

  alert("업로드 완료! (목업)");
  window.location.href = "index.html";
});
