document.getElementById('searchbox').addEventListener('keypress', function (e) {
    if (e.key === 'Enter') {
        searchpost();
    }
});

function searchpost() {
    const searchQuery = document.getElementById("searchbox").value;
    
    if (!(searchQuery.trim() == '')) {
        window.location.href = `/post/?q=${encodeURIComponent(searchQuery)}`;
    } else {
        alert('검색할 내용을 입력해주세요!');
    }

}