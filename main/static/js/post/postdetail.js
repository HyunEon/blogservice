document.addEventListener('DOMContentLoaded', () => {
    let template = null;
    // 숨겨진 템플릿 (폼)
    const templateContainer = document.getElementById('comment-edit-reply-form-template');
    if (templateContainer) {
        template = templateContainer.querySelector('form');
    }

    // 기존 폼 제거
    function removeExistingForm() {
        const existingForm = document.querySelector('.comment-edit-reply-form.active');
        if (existingForm) existingForm.remove();
    }

    // 폼 삽입 함수, 답글이면 hiddeninput 초기화
    function insertForm(targetElement, commentId, mode = 'reply', currentText = '') {
        removeExistingForm();

        // 폼 액티브 상태로 변경
        const formClone = template.cloneNode(true);
        formClone.classList.add('active');

        // 폼을 포스트 하는데 필요한 파라미터 초기화
        const hiddenInputParentId = formClone.querySelector('input[name="parent_comment_id"]');
        const hiddenInputCommentId = formClone.querySelector('input[name="comment_id"]');

        // 모드에 따른 파라미터 삽입
        if (mode === 'edit') {
            const textarea = formClone.querySelector('.edit-textarea');
            if (textarea) textarea.value = currentText;
            hiddenInputParentId.value = '';
            hiddenInputCommentId.value = commentId;
        } else {
            hiddenInputParentId.value = commentId;
        }

        // 취소 버튼
        const cancelBtn = formClone.querySelector('.cancel-edit-btn');
        if (cancelBtn) {
            cancelBtn.addEventListener('click', (e) => {
                e.preventDefault();
                formClone.remove();
            });
        }

        // 해당 위치에 폼 삽입
        targetElement.appendChild(formClone);
        // 폼이 생성된 후 스크롤을 해당 폼 위치로 이동시킴.
        formClone.scrollIntoView({
            behavior: 'smooth', // 부드럽게
            block: 'center' // 폼을 가운데 정렬한 위치로 스크롤 이동
        });

        return formClone;
    }

    // 답글 버튼
    document.querySelectorAll('.comment-reply-btn').forEach(button => {
        button.addEventListener('click', (e) => {
            e.preventDefault();
            const commentId = button.dataset.commentId;
            const mentionId = button.dataset.mentionId;
            const nickname = button.dataset.nickname;

            const commentItem = document.getElementById(`comment-${commentId}`);
            const formElement = insertForm(commentItem, commentId, 'reply');

            const textarea = formElement.querySelector('.edit-textarea');
            let mentionSpan = formElement.querySelector('.mention-to-user');
            const mentionInput = formElement.querySelector('#mention_id');

            if (mentionInput) mentionInput.value = mentionId; // hidden input에 mention ID 저장
            if (mentionSpan) mentionSpan.innerText = `@${nickname}님에게 답글 남기는 중..`;
            textarea.focus();
        });
    });

    // 더 보기 버튼
    document.querySelectorAll('.more-btn').forEach(button => {
        button.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            const commentId = button.dataset.commentId;
            const menu = document.getElementById(`more-menu-${commentId}`);

            // 다른 메뉴 닫기
            document.querySelectorAll('.more-menu.show').forEach(openMenu => {
                if (openMenu !== menu) openMenu.classList.remove('show');
            });

            menu.classList.toggle('show');
        });
    });

    // 수정 버튼
    document.querySelectorAll('.comment-edit-btn').forEach(editBtn => {
        editBtn.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();

            const commentId = editBtn.dataset.commentId;
            const commentItem = document.getElementById(`comment-${commentId}`);
            const commentText = commentItem.querySelector('.comment-body').innerText.trim();

            // 메뉴 닫기
            const menu = document.getElementById(`more-menu-${commentId}`);
            if (menu) menu.classList.remove('show');

            // 수정 폼 삽입
            insertForm(commentItem, commentId, 'edit', commentText);
        });
    });

    // 메뉴 외부 클릭 시 닫기
    document.addEventListener('click', () => {
        document.querySelectorAll('.more-menu.show').forEach(openMenu => {
            openMenu.classList.remove('show');
        });
    });

    // CSRF 토큰을 가져오는 함수
    function getCsrfTokenFromDOM() {
        // 히든 필드로 cstf 토큰을 가져온 인풋을 찾아 토큰 값을 전달함
        const tokenInput = document.querySelector('input[name="csrfmiddlewaretoken"]');
        return tokenInput ? tokenInput.value : null;
    }
    // CSRF 토큰 변수 초기화, 이거 전역 변수임.
    const csrftoken = getCsrfTokenFromDOM();

    // 좋아요 토글 버튼
    document.querySelectorAll('.like-btn').forEach(button => {
        button.addEventListener('click', (e) => {
            // 하위 span 태그가 계속 잡혀서 버튼만 잡히도록 고정
            const button = e.currentTarget
            let postId = ''
            if (button.dataset.postId) {
                postId = button.dataset.postId;
                fetch(`/post/${postId}/like/`, {
                    method: 'POST',
                    headers: {
                        'X-CSRFToken': csrftoken,
                    }
                })
                .then(res => res.json())
                .then(data => {
                    button.classList.toggle('liked', data.liked);
                    button.querySelector('.like-count').innerText = data.like_count;
                });
            };
        });
    });
});
