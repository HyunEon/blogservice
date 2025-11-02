document.addEventListener('DOMContentLoaded', function () {
    const urlParams = new URLSearchParams(window.location.search);
    const nextParam = urlParams.get('next') || '/'; // 기본값은 메인 페이지

    console.log('Next Parameter Value:', nextParam);

    const googleDiv = document.getElementById('g_id_onload');
    if (googleDiv) {  // 존재 여부 확인
        googleDiv.setAttribute('your_own_param_next', nextParam);
    }
});