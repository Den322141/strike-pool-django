for (const form of document.querySelectorAll('.validated')) {
  const password = form.elements.password1;
  const repeat = form.elements.password2;
  function validatePasswords() {
    if (password && repeat) {
      password.setCustomValidity(password.value && password.value.length < 8 ? 'Введите не меньше 8 символов.' : '');
      repeat.setCustomValidity(repeat.value && password.value !== repeat.value ? 'Пароли должны совпадать.' : '');
    }
  }
  form.addEventListener('input', validatePasswords);
  form.addEventListener('submit', event => {
    validatePasswords();
    if (!form.reportValidity()) event.preventDefault();
  });
}

function listenForChanges(form, output, refresh) {
  let timer;
  let currentRequest;
  const update = () => {
    clearTimeout(timer);
    if (currentRequest) currentRequest.abort();
    const controller = new AbortController();
    currentRequest = controller;
    output.textContent = 'Загрузка…';
    timer = setTimeout(async () => {
      try {
        await refresh(controller.signal);
      } catch (error) {
        if (!controller.signal.aborted) output.textContent = 'Не удалось обновить данные. Попробуйте ещё раз.';
      }
    }, 250);
  };
  form.addEventListener('input', update);
  return update;
}

const booking = document.querySelector('[data-quote]');
if (booking) {
  const output = booking.querySelector('.quote-result');
  const refresh = listenForChanges(booking, output, async signal => {
    const fields = new FormData(booking);
    if (!fields.get('starts_at') || !fields.getAll('zones').length) {
      output.textContent = 'Выберите начало игры и хотя бы одну зону для расчёта.';
      return;
    }
    const params = new URLSearchParams();
    for (const key of ['starts_at', 'hours', 'guests', 'zones']) {
      for (const value of fields.getAll(key)) params.append(key, value);
    }
    if (booking.dataset.booking) params.set('booking', booking.dataset.booking);
    const response = await fetch(booking.dataset.quote + '?' + params, {signal});
    if (!response.ok && response.status !== 422) throw new Error('quote');
    const data = await response.json();
    if (signal.aborted) return;
    output.textContent = data.errors ? Object.values(data.errors).flat().map(item => item.message).join(' ')
      : 'Стоимость бронирования: ' + Number(data.total).toLocaleString('ru-RU') + ' ₽';
  });
  refresh();
}

const menu = document.querySelector('.menu-filter');
if (menu) {
  const status = document.querySelector('#search-status');
  const results = document.querySelector('#menu-results');
  listenForChanges(menu, status, async signal => {
    const url = new URL(menu.action);
    url.search = new URLSearchParams(new FormData(menu));
    const response = await fetch(url, {signal});
    if (!response.ok) throw new Error('search');
    const documentResult = new DOMParser().parseFromString(await response.text(), 'text/html');
    const found = documentResult.querySelector('#search-results');
    if (!found) throw new Error('results');
    if (signal.aborted) return;
    for (const link of found.querySelectorAll('a[href^="?"]')) {
      link.href = new URL(link.getAttribute('href'), url).href;
    }
    results.replaceChildren(...found.childNodes);
    status.textContent = documentResult.querySelector('#search-count').textContent;
  });
}
