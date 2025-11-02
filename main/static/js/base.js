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

// 드롭다운 메뉴
document.addEventListener('DOMContentLoaded', () => {
    const profileButton = document.querySelector('.profile-button');
    const dropdownMenu = document.querySelector('.dropdown-menu');

    profileButton.addEventListener('click', (e) => {
        e.stopPropagation();
        dropdownMenu.classList.toggle('open');
    });

    document.addEventListener('click', (e) => {
        if (!dropdownMenu.contains(e.target) && !profileButton.contains(e.target)) {
            dropdownMenu.classList.remove('open');
        }
    });
});