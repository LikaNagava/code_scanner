class AppStrings {
  final String scan;
  final String scanning;
  final String history;
  final String scanner;
  final String gallery;
  final String model;
  final String number;
  final String date;
  final String confidence;
  final String close;
  final String result;
  final String historyEmpty;
  final String historySubtitle;

  const AppStrings({
    required this.scan,
    required this.scanning,
    required this.history,
    required this.scanner,
    required this.gallery,
    required this.model,
    required this.number,
    required this.date,
    required this.confidence,
    required this.close,
    required this.result,
    required this.historyEmpty,
    required this.historySubtitle,
  });

  static const ru = AppStrings(
    scan: 'СКАНИРОВАТЬ',
    scanning: 'Распознаю…',
    history: 'История',
    scanner: 'Сканер',
    gallery: 'Галерея',
    model: 'Модель',
    number: 'Номер',
    date: 'Дата',
    confidence: 'Уверенность',
    close: 'ЗАКРЫТЬ',
    result: 'Результат',
    historyEmpty: 'История пуста.\nОтсканируйте что-нибудь.',
    historySubtitle: 'Последние 5 устройств хранятся только здесь.',
  );

  static const en = AppStrings(
    scan: 'SCAN',
    scanning: 'Recognizing…',
    history: 'History',
    scanner: 'Scanner',
    gallery: 'Gallery',
    model: 'Model',
    number: 'Serial',
    date: 'Date',
    confidence: 'Confidence',
    close: 'CLOSE',
    result: 'Result',
    historyEmpty: 'History is empty.\nScan something.',
    historySubtitle: 'Last 5 devices are stored only here.',
  );
}