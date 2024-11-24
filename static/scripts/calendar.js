const calendar = document.querySelector('.calendar');
const monthYear = document.getElementById('month-year');
const daysContainer = document.querySelector('.days');
const prevWeek = document.querySelector('.prev-month'); // Renamed to prevWeek
const nextWeek = document.querySelector('.next-month'); // Renamed to nextWeek

let currentDate = new Date();

const months = ["Январь", "Февраль", "Март", "Апрель", "Май", "Июнь", "Июль", "Август", "Сентябрь", "Октябрь", "Ноябрь", "Декабрь"];
const daysOfWeek = ["Пн", "Вт", "Ср", "Чт", "Пт", "Сб", "Вс"];

const renderCalendar = () => {
  const firstDayOfWeek = currentDate.getDay() === 0 ? 6 : currentDate.getDay() -1;
  const firstDayOfCurrentWeek = new Date(currentDate);
  firstDayOfCurrentWeek.setDate(currentDate.getDate() - firstDayOfWeek);

  const month = months[firstDayOfCurrentWeek.getMonth()]; // Get month name
  const year = firstDayOfCurrentWeek.getFullYear();

  monthYear.textContent = month


  daysContainer.innerHTML = '';
  for (let i = 0; i < 7; i++) {
    const day = new Date(firstDayOfCurrentWeek);
    day.setDate(day.getDate() + i);
    const cell = document.createElement('div');
    cell.textContent = day.getDate();
    if (day.toDateString() === new Date().toDateString()) {
      cell.classList.add('current');
    }
    daysContainer.appendChild(cell);
  }
};


prevWeek.addEventListener('click', () => {
  currentDate.setDate(currentDate.getDate() - 7);
  renderCalendar();
});

nextWeek.addEventListener('click', () => {
  currentDate.setDate(currentDate.getDate() + 7);
  renderCalendar();
});

function formatShortDate(date) {
  return `${date.getDate()}.${date.getMonth() + 1}.${date.getFullYear()}`;
}


renderCalendar();
