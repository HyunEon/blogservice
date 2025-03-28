function confirmDelete() {
    return confirm('정말 삭제하시겠습니까?');
}

function validationcomment(par) {
    const validationtype = par;
    let commentvalue = '';
    
    switch (validationtype) {
        case 'normal':
            commentvalue = document.getElementsByClassName("postcommenttextarea")[0];
            break;
        case 'reply':
            commentvalue = document.getElementsByClassName("postcommentreplytextarea")[0];
            break;
        default:
            commentvalue = '';
        }

    if(commentvalue.value.trim() == '') {
        alert('내용을 입력해주세요!');
        return false;
    }
    return true;
}

function activateReplyWidget(event) {
    event.preventDefault();

    // 클릭한 답글 버튼의 부모 요소를 찾음 (해당 댓글 영역)
    let commentElement = event.target.closest('.postcommentlist');

    // 답글 입력창을 찾음
    let replyWidget = document.querySelector('.postreplytinput');

    // 기존에 다른 곳에서 활성화된 답글 입력창이 있다면 숨기기
    if (replyWidget.style.display === "block" && replyWidget.parentElement === commentElement) {
        replyWidget.style.display = "none";
        return;
    }

    // 해당 댓글 아래로 이동 후 보이도록 설정
    commentElement.after(replyWidget);
    replyWidget.style.display = "block";

    // 기존 폼 action을 현재 댓글의 답글 작성 URL로 변경
    let replyForm = replyWidget.querySelector('form');

    // 기존 action URL에서 댓글 ID 제거 (정확한 기본 URL 유지)
    let BaseUrl = replyForm.dataset.baseAction || replyForm.getAttribute('action'); // 처음 기본 URL 저장
    BaseUrl = BaseUrl.split('/comments/')[0] + '/comments/'; // 중복되는 comment_id 제거

    // 댓글 ID를 올바르게 가져오기 (GUID 지원)
    let actionUrl = commentElement.querySelector('form').action;
    let match = actionUrl.match(/\/comments\/([\w-]+)\//);  // '/comments/GUID/' 패턴 찾기
    let commentId = match ? match[1] : null;  // 매칭된 GUID(comment_id) 가져오기

    if (commentId) {
        replyForm.action = `${BaseUrl}${commentId}/`; // 최종 action 설정
    } else {
        console.error("댓글 ID를 찾을 수 없습니다.");
    }

    // 최초 기본 URL을 dataset으로 저장 (다음에 또 클릭할 때 중복 방지)
    if (!replyForm.dataset.baseAction) {
        replyForm.dataset.baseAction = BaseUrl;
    }
}

