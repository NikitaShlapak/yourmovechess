const m_show = "Подробнее"
const m_hide = "Скрыть"

const btn = document.querySelector('#info-toggle');

btn.addEventListener('click', function() {
  btn.innerHTML =
    (btn.innerHTML === m_show) ? btn.innerHTML = m_hide : btn.innerHTML = m_show;
})