function validationCheck() {
    if (createpostform.post_title.value == "") {
        alert("제목을 입력해주세요");
        return false;
    }

    else if (myEditor.getData() == "") {
        alert("내용을 입력해주세요");
        return false;
    }
}

