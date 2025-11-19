// CSRF 토큰을 가져오는 함수
function getCsrfTokenFromDOM() {
    // 히든 필드로 cstf 토큰을 가져온 인풋을 찾아 토큰 값을 전달함
    const tokenInput = document.querySelector('input[name="csrfmiddlewaretoken"]');
    return tokenInput ? tokenInput.value : null;
}

const csrftokenforcategory = getCsrfTokenFromDOM();
const categoryDetailContainer = document.getElementById('category-detail');

$(document).ready(function() {
    // Nestable 초기화
    let nestable = $('#category-nestable').nestable({
        maxDepth: 2 // 최대 중첩 레벨
    });

    const reorderUrl = $('#category-nestable').data('reorder-url');

    // 드롭 이벤트 발생 시 AJAX 전송
    nestable.on('change', function(e) {
        // 변경된 트리 구조를 JSON으로 직렬화
        const serializedData = nestable.nestable('serialize');
        // AJAX로 Django 뷰에 전송
        $.ajax({
            url: reorderUrl, 
            type: 'POST',
            dataType: 'json',
            contentType: 'application/json',
            data: JSON.stringify(serializedData), // JSON 문자열로 전송
            headers: {
                // CSRF 토큰 전송
                "X-CSRFToken": csrftokenforcategory
            },
            success: function(response) {
                alert('카테고리 순서를 저장했습니다.');
                console.log(response);
            },
            error: function(xhr, status, error) {
                console.error("오류 발생:", error);
                alert("순서 저장에 실패했습니다.");
            }
        });
    });

    // 카테고리 더보기 버튼 클릭 시
$(document).on('click', '.moreBtn', function() {
    categoryDetailContainer.style.display = 'block';
    const item = $(this).closest('.dd-item');
    const categoryId = item.data('id');
    const categoryName = $(this).closest('.dd-item').children('.dd-handle-wrapper').find('.dd-handle').text()
    // delete form에 주소 채워줌
    $('#deleteCategoryForm').attr('action', `/category/${categoryId}/delete/`);
    // 삭제 버튼 활성화
    $('#deleteCategoryBtn').prop('disabled', false);

    // 선택한 카테고리 ID와 이름 저장
    $('#categoryEditBox')
        .data('category-id', categoryId);
    $('#categoryNameInput')
        .val(categoryName)
        .prop('disabled', false);
});

// 카테고리 더보기 닫기 버튼 클릭 시
$('#categoryEditBoxClostButton').on('click', function() {
    categoryDetailContainer.style.display = 'none';
});

// 수정 저장 버튼 클릭 시
$('#saveCategoryBtn').on('click', function() {
    const categoryId = $('#categoryEditBox').data('category-id');
    const name = $('#categoryNameInput').val();

    if (!categoryId || !name.trim()) {
        alert('카테고리를 선택하세요.');
        return;
    }

    $.ajax({
        url: `/category/${categoryId}/update/`,
        method: 'POST',
        data: {
            name: name,
            csrfmiddlewaretoken: csrftokenforcategory
        },
        success: function(resp) {
            if (resp.success) {
                const item = $(`.dd-item[data-id="${resp.id}"]`);
                item.children('.dd-handle-wrapper').find('.dd-handle').text(resp.name);

                $('#categoryNameInput').val('').prop('disabled', true);
                $('#categoryEditBox').removeData('category-id');
                // 삭제 폼 액션 비우기
                $('#deleteCategoryForm').attr('action', '');
                // 삭제 폼 버튼도 비활성화
                $('#deleteCategoryBtn').prop('disabled', true);
                alert('카테고리 업데이트 성공');
            } else {
                alert('업데이트 실패');
            }
        },
        error: function() {
            alert('서버 오류 발생');
        }
    });
});

// 삭제 버튼 클릭 시
    $('#deleteCategoryBtn').on('click', function(e) {
        // 폼 제출 막기
        e.preventDefault();
        const categoryId = $('#categoryEditBox').data('category-id');
        const confirmed = 
            confirm('이 카테고리를 삭제하시겠습니까?\n카테고리 및 하위 카테고리에 포함된 모든 글 또한 삭제됩니다.');

        if (!confirmed) return;

    $('#deleteCategoryForm').submit();
});

    // 모달 열기
    $('#CreateCategoryBtn').click(function() {
        $('#categoryModal').show();
        $('#categoryForm').attr('action', '/category/create/');
    });

    // 카테고리 생성 폼
    $('#categoryForm').submit(function(e) {
    e.preventDefault(); // 기본 submit 막기

    const formData = $(this).serialize();  // CSRF 포함
    const url = $(this).attr('action');

    $.ajax({
        url: url,
        method: 'POST',
        data: formData,
        success: function(resp) {
            alert('카테고리 생성 성공');
            if (resp.id) {
                // 리스트에 새 항목 추가
                const newItem = `<li class="dd-item" data-id="${resp.id}">
                <div class="dd-handle-wrapper">
                    <div class="dd-handle">${resp.name}</div>
                    <div class="dd-actions">
                        <button class="moreBtn" data-id="${resp.id}">⋮</button>
                    </div>
                    </div>
                </li>`;
                $('#category-nestable > .dd-list').append(newItem);
                // 생성 후 nestable 초기화
                nestable.nestable('destroy').nestable({ maxDepth: 2 });
            }
            $('#categoryModal').hide();
            $('#categoryForm')[0].reset();
        },
        error: function() { alert('저장 실패'); }
    });
});

    $('#modalClose').click(function() {
        $('#categoryModal').hide();
    });

});