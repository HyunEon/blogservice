// CSRF 토큰을 가져오는 함수
function getCsrfTokenFromDOM() {
    // 히든 필드로 cstf 토큰을 가져온 인풋을 찾아 토큰 값을 전달함
    const tokenInput = document.querySelector('input[name="csrfmiddlewaretoken"]');
    return tokenInput ? tokenInput.value : null;
}
// CSRF 토큰 변수 초기화, 이거 전역 변수임.
const csrftoken = getCsrfTokenFromDOM();

document.querySelectorAll('#notification-content .notif-itme-close-btn').forEach(btn => {
    btn.addEventListener('click', function(){
        const item = this.closest('.notif-item');
        const notifId = this.dataset.notifId; // notif.id 값 가져오기
        
        // DOM에서 먼저 알림 숨김
        item.style.display = 'none'; 

        // 서버에 읽음/삭제 요청 보내기
        if (notifId) {
            fetch('/notifications/notificationread/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrftoken
                },
                body: JSON.stringify({ 'notification_ids': [notifId] })
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Network response was not ok');
                }
                return response.json();
            })
            .then(data => {
                console.log('Server response:', data);
                updateNotificationView();
            })
            .catch(error => {
                console.error('Fetch error:', error);
                alert('오류가 발생했습니다. ');
            });
        }
    });
});

document.querySelector('.notif-all-read-btn').addEventListener('click', function() {
    const popup = document.getElementById('notification-content');
    // 현재 알림 item을 모두 가져옴
    const notifIds = Array.from(popup.querySelectorAll('.notif-item')).map(item => {
        // 닫기 버튼에서 data-notif-id 값을 가져옴
        const closeBtn = item.querySelector('.notif-itme-close-btn');
        return closeBtn ? closeBtn.dataset.notifId : null;
    }).filter(id => id !== null);

    // 알림이 없으면 요청 보내지 않음
    if (notifIds.length === 0) {
        alert('읽음 처리할 알림이 없습니다.');
        return;
    }

    fetch('/notifications/notificationread/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken
        },
        body: JSON.stringify({ 'notification_ids': notifIds }) // 알림 아이템 ID 목록 JSON으로 던짐
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('Network response was not ok');
        }
        return response.json();
    })
    .then(data => {
        console.log('Server response (all Read):', data);
        // 모든 알림 아이템 display를 안 보이게 업데이트
        popup.querySelectorAll('.notif-item').forEach(item => {
            item.style.display = 'none';
        });
        // 알림 비활성화 로직 
        updateNotificationView();
    });
});

function updateNotificationView() {
    const popup = document.getElementById('notification-content');
    const visibleItems = popup.querySelectorAll('.notif-item:not([style*="display: none"])');
    
    // 팝업에 보이는 알림이 하나도 없는 경우
    if (visibleItems.length === 0) {
        let emptyDiv = popup.querySelector('.notif-item-none');
        
        // 알림 없음 요소가 존재하지 않으면 새로 생성함
        if (!emptyDiv) {
            emptyDiv = document.createElement('div');
            emptyDiv.className = 'notif-item-none';
            emptyDiv.textContent = '새로운 알림이 없습니다.';
            // 모두 읽음 버튼 위에 삽입
            popup.insertBefore(emptyDiv, popup.querySelector('.notif-all-read-btn'));
        } 
        
        // 알림 없음 요소를 보이게 설정
        emptyDiv.style.display = 'flex';

        // 알림 UI의 활성화 표시를 안 보이게 설정
        const notifactivesign = document.querySelector('.notif-dot'); 
        if (notifactivesign) { 
            notifactivesign.style.display = 'none'; 
        } 
    }
}