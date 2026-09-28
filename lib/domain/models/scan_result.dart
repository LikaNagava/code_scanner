class ScanResult {
  final String id;
  final String? model;
  final String? serialNumber;
  final double confidence;
  final String status;
  final DateTime date;
  final String? sourceFileName;

  ScanResult({
    required this.id,
    this.model,
    this.serialNumber,
    required this.confidence,
    required this.status,
    required this.date,
    this.sourceFileName,
  });

  factory ScanResult.fromApi(Map<String, dynamic> data, {String? fileName}) {
    return ScanResult(
      id: DateTime.now().millisecondsSinceEpoch.toString(),
      model: data['model'] as String?,
      serialNumber: data['serial_number'] as String?,
      confidence: (data['confidence'] as num?)?.toDouble() ?? 0.0,
      status: data['status'] as String? ?? 'not_found',
      date: DateTime.now(),
      sourceFileName: fileName,
    );
  }

  ScanResult copyWith({
    String? model,
    String? serialNumber,
    double? confidence,
    String? status,
    DateTime? date,
    String? sourceFileName,
  }) {
    return ScanResult(
      id: id,
      model: model ?? this.model,
      serialNumber: serialNumber ?? this.serialNumber,
      confidence: confidence ?? this.confidence,
      status: status ?? this.status,
      date: date ?? this.date,
      sourceFileName: sourceFileName ?? this.sourceFileName,
    );
  }

  Map<String, dynamic> toJson() => {
    'id': id,
    'model': model,
    'serial_number': serialNumber,
    'confidence': confidence,
    'status': status,
    'date': date.toIso8601String(),
    'source_file_name': sourceFileName,
  };

  factory ScanResult.fromJson(Map<String, dynamic> json) {
    return ScanResult(
      id: json['id'] as String,
      model: json['model'] as String?,
      serialNumber: json['serial_number'] as String?,
      confidence: (json['confidence'] as num?)?.toDouble() ?? 0.0,
      status: json['status'] as String? ?? 'not_found',
      date: DateTime.parse(json['date'] as String),
      sourceFileName: json['source_file_name'] as String?,
    );
  }
}