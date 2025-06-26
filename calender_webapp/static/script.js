let busyDates = [];
let currentMonth;
let currentYear;

let selectedDate = null;
let selectedTime = null;

const urlParams = new URLSearchParams(window.location.search);
const selectedDuration = parseInt(urlParams.get("duration_minutes")) || 15;
const selectedServiceID = urlParams.get("service_id");
const selectedId = urlParams.get("client_id");
const selectedChatId = urlParams.get("chat_id");



// Проверка на отсутствие параметров
if (!selectedServiceID || !selectedId || !selectedChatId) {
    alert("Не всі параметри передані з Telegram. Перевір URL або оновіть додаток.");
}


// Получение занятых дат
async function fetchBusyDates(year, month) {
    const response = await fetch(`/api/busy-days?year=${year}&month=${month + 1}&duration=${selectedDuration}`);
    const data = await response.json();
    busyDates = data;
}

// Отправка данных на сервер
function sendDataToServer() {
    if (!(selectedDate && selectedTime)) return;

    fetch("/api/submit", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ date: selectedDate, time: selectedTime, serviceI: selectedServiceID,  user: selectedId, duration:  selectedDuration, chatID:selectedChatId}),
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === "success") {
            if (window.Telegram.WebApp) {
        window.Telegram.WebApp.close();
      }
        } /*else {
            alert("Ошибка: " + data.message);
        }
    })
    .catch(err => {
        alert("Ошибка отправки: " + err.message);
    */});
}
// Получение свободных слотов
function fetchFreeSlots(date) {
    return fetch(`/api/free-slots?date=${date}&duration=${selectedDuration}&service_id=${selectedServiceID}`)
        .then(response => response.json())
        .catch(error => {
            console.error("Ошибка при получении слотов:", error);
            return [];
        });
}

// Отрисовка календаря
function renderCalendar() {
    const monthNames = [
        "Січень", "Лютий", "Березень", "Квітень", "Травень", "Червень",
        "Липень", "Серпень", "Вересень", "Жовтень", "Листопад", "Грудень"
    ];

    document.querySelector(".month_name").textContent = monthNames[currentMonth] + " " + currentYear;

    const firstDay = new Date(currentYear, currentMonth, 1);
    const startDay = (firstDay.getDay() + 6) % 7;
    const daysInMonth = new Date(currentYear, currentMonth + 1, 0).getDate();

    const dataContainer = document.querySelector(".data");
    dataContainer.innerHTML = "";

    for (let i = 0; i < startDay; i++) {
        const empty = document.createElement("div");
        dataContainer.appendChild(empty);
    }

    for (let i = 1; i <= daysInMonth; i++) {
        const button = document.createElement("button");
        button.type = "button";
        button.textContent = i;

        const buttonDate = new Date(currentYear, currentMonth, i);
        const today = new Date();
        today.setHours(0, 0, 0, 0);
        buttonDate.setHours(0, 0, 0, 0);

        const isoDate = buttonDate.getFullYear() + "-" +
            String(buttonDate.getMonth() + 1).padStart(2, "0") + "-" +
            String(buttonDate.getDate()).padStart(2, "0");

        if (buttonDate < today) {
            button.disabled = true;
        }

        if (busyDates.includes(isoDate)) {
            button.disabled = true;
            button.classList.add("busy");
        }

        button.addEventListener("click", () => {
            selectedDate = isoDate;
            selectedTime = null;
            updateConfirmButtonState();
            highlightSelectedDate(button);
            showAvailableTimeSlots(isoDate);
        });

        dataContainer.appendChild(button);
    }
}

// Подсветка выбранной даты
function highlightSelectedDate(selectedBtn) {
    const buttons = document.querySelectorAll(".data button");
    buttons.forEach(btn => btn.classList.remove("selected"));
    selectedBtn.classList.add("selected");
}

// Показ доступных временных слотов на выбранную дату
function showAvailableTimeSlots(date) {
    const container = document.querySelector("#time-slots");
    container.innerHTML = "⏳ Завантаження вільного часу...";

    fetchFreeSlots(date).then(slots => {
        container.innerHTML = "";
        if (!slots.length) {
            container.textContent = "🚫 Немає вільного часу на цю дату.";
            return;
        }

        const wrapper = document.createElement("div");
        wrapper.classList.add("time-slots");

        slots.forEach(slot => {
            const btn = document.createElement("button");
            btn.type = "button";
            btn.textContent = slot;
            btn.classList.add("time-slot-btn");

            btn.addEventListener("click", () => {
                selectedTime = slot;
                updateConfirmButtonState();
                highlightSelectedTime(btn);
            });

            wrapper.appendChild(btn);
        });

        container.appendChild(wrapper);
    });
}

// Подсветка выбранного времени
function highlightSelectedTime(selectedBtn) {
    const buttons = document.querySelectorAll(".time-slot-btn");
    buttons.forEach(btn => btn.classList.remove("active"));
    selectedBtn.classList.add("active");
}

// Обновление состояния кнопки "Підтвердити"
function updateConfirmButtonState() {
    const btn = document.querySelector("#confirm-button");
    btn.disabled = !(selectedDate && selectedTime);
}

// Отправка данных в Telegram WebApp
function sendDataToTelegram() {
    if (window.Telegram && window.Telegram.WebApp) {
        const data = { date: selectedDate, time: selectedTime };
        window.Telegram.WebApp.sendData(JSON.stringify(data));
        console.log("Дані відправлені в Telegram:", data);
    } else {
        console.log("Telegram WebApp не доступен. Отправка невозможна.");
        alert("Telegram WebApp не доступен. Отправка невозможна.");
    }
}

// Инициализация при загрузке страницы
document.addEventListener("DOMContentLoaded", () => {
    const now = new Date();
    currentMonth = now.getMonth();
    currentYear = now.getFullYear();

    fetchBusyDates(currentYear, currentMonth).then(() => {
        renderCalendar();
    });

    document.querySelector(".prev").addEventListener("click", () => {
        if (currentMonth === 0) {
            currentMonth = 11;
            currentYear--;
        } else {
            currentMonth--;
        }
        selectedDate = null;
        selectedTime = null;
        updateConfirmButtonState();
        fetchBusyDates(currentYear, currentMonth).then(() => {
            renderCalendar();
            document.querySelector("#time-slots").innerHTML = "";
        });
    });

    document.querySelector(".next").addEventListener("click", () => {
        if (currentMonth === 11) {
            currentMonth = 0;
            currentYear++;
        } else {
            currentMonth++;
        }
        selectedDate = null;
        selectedTime = null;
        updateConfirmButtonState();
        fetchBusyDates(currentYear, currentMonth).then(() => {
            renderCalendar();
            document.querySelector("#time-slots").innerHTML = "";
        });
    });

    // Создаем и добавляем кнопку "Підтвердити"
    const confirmBtn = document.createElement("button");
    confirmBtn.id = "confirm-button";
    confirmBtn.textContent = "Підтвердити";
    confirmBtn.disabled = true;
    confirmBtn.style.position = "fixed";
    confirmBtn.style.bottom = "10px";
    confirmBtn.style.left = "50%";
    confirmBtn.style.transform = "translateX(-50%)";
    confirmBtn.style.padding = "12px 24px";
    confirmBtn.style.fontSize = "1.2rem";
    confirmBtn.style.borderRadius = "8px";
    confirmBtn.style.border = "none";
    confirmBtn.style.backgroundColor = "#2a9df4";
    confirmBtn.style.color = "white";
    confirmBtn.style.cursor = "pointer";
    confirmBtn.style.zIndex = "1000";

    confirmBtn.addEventListener("click", () => {
        sendDataToTelegram();
        sendDataToServer();
    });

    document.body.appendChild(confirmBtn);
});

