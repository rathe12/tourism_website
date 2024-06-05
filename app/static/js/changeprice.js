document.addEventListener('DOMContentLoaded', function () {
    // Получаем все чекбоксы
    let checkboxes = document.querySelectorAll('.baggage-checkbox');
    
    checkboxes.forEach(function (checkbox) {
        checkbox.addEventListener('change', function () {
            updateCheckbox(this);
            updatePrice(this);
        });
    });
});

function updateCheckbox(clickedCheckbox) {
    // Если кликнутый чекбокс неактивен, не делаем ничего
    if (!clickedCheckbox.checked) {
        return;
    }
    
    // Получаем все чекбоксы
    let checkboxes = document.querySelectorAll('.baggage-checkbox');

    // Проходимся по каждому чекбоксу
    checkboxes.forEach(function (checkbox) {
        // Если это не кликнутый чекбокс, делаем его неактивным
        if (checkbox !== clickedCheckbox) {
            checkbox.checked = false;
            updatePrice(checkbox)
        }
    });
}

function updatePrice(checkbox) {
    let priceElement = document.getElementById(checkbox.dataset.priceId);
    let linkElement = document.getElementById(checkbox.dataset.linkId);

    let basePrice = parseFloat(priceElement.dataset.basePrice);
    let newPrice = basePrice;

    // Получаем все чекбоксы
    let checkboxes = document.querySelectorAll('.baggage-checkbox');

    checkboxes.forEach(function (cb) {
        if (cb.checked && cb.dataset.priceId === checkbox.dataset.priceId) {
            newPrice += 1000;
        }
    });

    priceElement.textContent = newPrice.toFixed(0) + ' ₽';

    let originalHref = linkElement.href;
    let url = new URL(originalHref);
    let params = new URLSearchParams(url.search);
    params.set('total_price', newPrice);

    // Add the baggage parameter
    if (checkbox.checked) {
        params.set('baggage', 'True');
    } else {
        params.set('baggage', 'False');
    }

    url.search = params.toString();
    linkElement.href = url.toString();
}
