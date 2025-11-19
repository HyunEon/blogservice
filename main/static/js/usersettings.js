document.getElementById('profile_image').addEventListener('change', e => {
  const [file] = e.target.files;
  if (file) {
    document.querySelector('.profile-preview').src = URL.createObjectURL(file);
  }
});