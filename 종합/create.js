
if(!requireAuth("login.html")) throw new Error("auth required");

$("#tagText").textContent = MOCK.mission.content;

const file = $("#file");
const drop = $("#drop");
const preview = $("#preview");
const previewImg = $("#previewImg");

function showPreview(src){
  drop.classList.add("hidden");
  preview.style.display = "block";
  previewImg.src = src;
}

drop.addEventListener("click", ()=> file.click());
file.addEventListener("change", ()=>{
  const f = file.files?.[0];
  if(!f) return;
  const url = URL.createObjectURL(f);
  showPreview(url);
});

$("#submitBtn").addEventListener("click", ()=>{
  // mock post create: add into feeds
  const u = currentUser();
  const imgSrc = previewImg.src || "assets/img/feed2.jpg";

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
