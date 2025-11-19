// django Message가 DOM에서 비활성화 되도록 변경, DOM에 활성화된 채로 남아있으면 사용자가 드래그 했을 때 select 되는 문제가 있음.
document.addEventListener('DOMContentLoaded', function() {
    const messageAlerts = document.querySelectorAll('.alert');

    messageAlerts.forEach(alertElement => {
        // animationend: 애니메이션이 끝나는 시점 감지
        alertElement.addEventListener('animationend', function(event) {
            if (event.animationName === 'fadeOut') {
                // 페이드 아웃 애니메이션 종료 시, display none 적용하여 비활성화
                alertElement.style.display = 'none';
            }
        });
    });
});

document.addEventListener('DOMContentLoaded', () => { 
    // 프로필 드롭다운
    const profileButton = document.querySelector('.profile-button');
    const dropdownMenu = document.querySelector('.dropdown-menu');

    // 알림 팝업
    const notifBtn = document.getElementById('notif-btn');
    const notifPopup = document.getElementById('notif-popup');

    if (profileButton) {
        profileButton.addEventListener('click', (e) => {
        e.stopPropagation();
        // 알림 팝업 닫기
        notifPopup.classList.remove('open'); 
        // 프로필 메뉴 토글
        dropdownMenu.classList.toggle('open');
    });
    
    notifBtn.addEventListener('click', (e) => {
        e.stopPropagation();     
        // 프로필 메뉴 닫기
        dropdownMenu.classList.remove('open'); 
        // 알림 팝업 토글
        notifPopup.classList.toggle('open');
        // 추후 읽음 표시 로직 추가 예정..
    });

    // 외부 클릭
    document.addEventListener('click', (e) => {
        // 프로필 드롭다운 닫기
        if (!dropdownMenu.contains(e.target) && !profileButton.contains(e.target)) {
            dropdownMenu.classList.remove('open');
        }
        // 알림 팝업 닫기
        if (!notifPopup.contains(e.target) && !notifBtn.contains(e.target)) {
            notifPopup.classList.remove('open');
        }
    });
    };
});

const toggleBtn = document.getElementById("theme-toggle");
const html = document.documentElement;

// 페이지 로드 시 로컬 스토리지 체크
const savedTheme = localStorage.getItem("data-theme");
if (savedTheme) {
  html.setAttribute("data-theme", savedTheme);
} else {
    localStorage.setItem("data-theme", "light");
}

// 토글 버튼 클릭
toggleBtn.addEventListener("click", () => {
  const currentTheme = html.getAttribute("data-theme");
  const newTheme = currentTheme === "light" ? "dark" : "light";
  
  html.setAttribute("data-theme", newTheme);
  localStorage.setItem("data-theme", newTheme);
});