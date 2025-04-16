document.addEventListener('DOMContentLoaded', () => {
    fetch('components/header.html')
      .then(res => res.text())
      .then(data => {
        document.body.insertAdjacentHTML('afterbegin', data);
      });
  
    fetch('components/footer.html')
      .then(res => res.text())
      .then(data => {
        document.body.insertAdjacentHTML('beforeend', data);
      });

    fetch('components/modal.html')
      .then(res => res.text())
      .then(data => {
        document.body.insertAdjacentHTML('beforeend', data);
      });

  });

  