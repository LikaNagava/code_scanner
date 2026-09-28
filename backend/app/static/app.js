// Этот файл отвечает только за поведение страницы: выбор изображения,
// запрос к API, показ результата и локальную историю на устройстве.
const HISTORY_KEY = "equipment_scan_history_v1";
const HISTORY_LIMIT = 5;

const input = document.querySelector("#file");
const drop = document.querySelector("#drop");
const send = document.querySelector("#send");
const result = document.querySelector("#result");
const fileName = document.querySelector("#fileName");
const historyList = document.querySelector("#historyList");
const emptyHistory = document.querySelector("#emptyHistory");
const downloadHistory = document.querySelector("#downloadHistory");
const clearHistory = document.querySelector("#clearHistory");

let selected = null;
let memoryHistory = [];

function choose(file) {
  selected = file;
  fileName.textContent = file ? file.name : "Перетащите фото сюда";
  send.disabled = !file;
}

// localStorage хранит историю отдельно на каждом телефоне или компьютере.
// Если браузер запретил localStorage, история всё равно работает до закрытия страницы.
function loadHistory() {
  try {
    const serialized = localStorage.getItem(HISTORY_KEY);
    if (serialized !== null) {
      const stored = JSON.parse(serialized);
      memoryHistory = Array.isArray(stored) ? stored.slice(0, HISTORY_LIMIT) : [];
    }
  } catch {
    // В режиме с ограниченным хранилищем используем текущую память страницы.
  }
  return memoryHistory;
}

function saveHistory(history) {
  memoryHistory = history.slice(0, HISTORY_LIMIT);
  try {
    localStorage.setItem(HISTORY_KEY, JSON.stringify(memoryHistory));
  } catch {
    // Ничего не делаем: резервная история уже осталась в memoryHistory.
  }
}

function addToHistory(data, sourceFileName) {
  const entry = {
    scanned_at: new Date().toISOString(),
    file_name: sourceFileName,
    status: data.status,
    model: data.model,
    serial_number: data.serial_number,
    confidence: data.confidence,
    bbox: data.bbox,
  };
  saveHistory([entry, ...loadHistory()].slice(0, HISTORY_LIMIT));
  renderHistory();
}

function addValue(container, label, value) {
  const block = document.createElement("div");
  block.className = "history-value";
  const caption = document.createElement("small");
  caption.textContent = label;
  const content = document.createElement("strong");
  content.textContent = value || "не найдено";
  block.append(caption, content);
  container.append(block);
}

// Вся разметка истории создаётся через textContent, поэтому OCR-текст не может
// превратиться в исполняемый HTML или JavaScript.
function renderHistory() {
  const history = loadHistory();
  historyList.replaceChildren();

  for (const entry of history) {
    const row = document.createElement("li");
    row.className = "history-item";
    addValue(row, "Модель", entry.model);
    addValue(row, "Серийный номер", entry.serial_number);

    const time = document.createElement("time");
    time.className = "history-time";
    time.dateTime = entry.scanned_at;
    time.textContent = new Date(entry.scanned_at).toLocaleString("ru-RU");
    row.append(time);
    historyList.append(row);
  }

  const hasHistory = history.length > 0;
  emptyHistory.hidden = hasHistory;
  downloadHistory.disabled = !hasHistory;
  clearHistory.disabled = !hasHistory;
}

// Браузер не может молча записать произвольный файл на телефон,
// поэтому JSON создаётся и скачивается только после нажатия пользователя.
function exportHistory() {
  const json = JSON.stringify(loadHistory(), null, 2);
  const blob = new Blob([json], { type: "application/json;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = "scan_history.json";
  link.click();
  setTimeout(() => URL.revokeObjectURL(url), 0);
}

input.addEventListener("change", () => choose(input.files[0]));

for (const name of ["dragenter", "dragover"]) {
  drop.addEventListener(name, (event) => {
    event.preventDefault();
    drop.classList.add("active");
  });
}

for (const name of ["dragleave", "drop"]) {
  drop.addEventListener(name, (event) => {
    event.preventDefault();
    drop.classList.remove("active");
  });
}

drop.addEventListener("drop", (event) => choose(event.dataTransfer.files[0]));

// Основной пользовательский сценарий: отправить файл и сохранить ответ.
send.addEventListener("click", async () => {
  if (!selected) return;

  send.disabled = true;
  send.textContent = "Распознаю…";
  result.classList.remove("show");
  const body = new FormData();
  body.append("file", selected);

  try {
    const response = await fetch("/recognize", { method: "POST", body });
    const data = await response.json();
    if (!response.ok) throw new Error(data.detail || "Ошибка сервера");

    document.querySelector("#model").textContent = data.model ?? "не найдено";
    document.querySelector("#serial").textContent = data.serial_number ?? "не найдено";
    const confidence = Math.round((data.confidence || 0) * 100);
    document.querySelector("#status").textContent =
      `Статус: ${data.status}. Уверенность: ${confidence}%`;
    document.querySelector("#status").classList.remove("error");
    addToHistory(data, selected.name);
  } catch (error) {
    document.querySelector("#model").textContent = "—";
    document.querySelector("#serial").textContent = "—";
    document.querySelector("#status").textContent = error.message;
    document.querySelector("#status").classList.add("error");
  } finally {
    result.classList.add("show");
    send.disabled = false;
    send.textContent = "Распознать";
  }
});

downloadHistory.addEventListener("click", exportHistory);
clearHistory.addEventListener("click", () => {
  if (!confirm("Очистить историю сканирования на этом устройстве?")) return;
  saveHistory([]);
  renderHistory();
});

renderHistory();
