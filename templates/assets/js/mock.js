
const MOCK = {
  mission: {
    id: 1,
    day: 1,
    content: "파란색을 찾아보자!",
    create_date: new Date().toISOString(),
    participants: 239
  },
  users: [
    { id: 1, username:"joshua", nickname:"joshua_l", profile_img_path:"assets/img/avatar.jpg" },
    { id: 2, username:"semin", nickname:"세민", profile_img_path:"assets/img/avatar.jpg" },
    { id: 3, username:"tak", nickname:"김타코", profile_img_path:"assets/img/avatar.jpg" }
  ],
  feeds: [
    {
      id: 101,
      mission_id: 1,
      user_id: 1,
      create_date: new Date(Date.now()-2*60*60*1000).toISOString(),
      likes: [2,3,1,9,8,7,6,5,4,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28,29,30,31,32,33,34,35,36,37,38,39,40,41,42],
      comments: [
        { user_id:3, content:"사진에 대한 의미가 궁금해요! 김타코인가?", create_date:new Date(Date.now()-80*60*1000).toISOString() }
      ],
      image_path:"assets/img/feed1.jpg"
    },
    {
      id: 102,
      mission_id: 1,
      user_id: 1,
      create_date: new Date(Date.now()-3*60*60*1000).toISOString(),
      likes: [2,3,4,5,6,7,8],
      comments: [],
      image_path:"assets/img/feed2.jpg"
    },
    {
      id: 103,
      mission_id: 1,
      user_id: 3,
      create_date: new Date(Date.now()-26*60*60*1000).toISOString(),
      likes: [1,2],
      comments: [
        { user_id:1, content:"예뻐요!!", create_date:new Date(Date.now()-25*60*60*1000).toISOString() },
        { user_id:2, content:"내 꿀잼템 공유해요! @김타코", create_date:new Date(Date.now()-24*60*60*1000).toISOString() }
      ],
      image_path:"assets/img/feed3.jpg"
    }
  ]
};

function getUserById(id){
  return MOCK.users.find(u => u.id === id);
}

function currentUser(){
  const uid = storage.get("userId");
  return uid ? getUserById(uid) : null;
}

function ensureSeedLogin(){
  const nick = storage.get("nickname");
  if(nick && !storage.get("userId")){
    storage.set("userId", 2);
  }
}
