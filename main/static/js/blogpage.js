document.addEventListener('DOMContentLoaded', function() {
    // 모든 토글 버튼 요소를 찾습니다.
    const toggles = document.querySelectorAll('.category-toggle');

    toggles.forEach(toggle => {
        const iconSpan = toggle.querySelector('.material-symbols-outlined'); 

        toggle.addEventListener('click', function() {
            const targetId = this.getAttribute('data-target');
            const targetElement = document.querySelector(targetId);

            if (targetElement && iconSpan) {
                targetElement.classList.toggle('collapsed');

                // 토글 버튼의 아이콘 텍스트 변경
                if (targetElement.classList.contains('collapsed')) {
                    iconSpan.textContent = 'arrow_drop_down'; 
                } else {
                    iconSpan.textContent = 'arrow_drop_up';
                }
            }
        });
    });
});