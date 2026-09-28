import 'package:flutter/material.dart';
import 'package:intl/intl.dart';

import '../../domain/localization.dart';
import '../../domain/models/scan_result.dart';

class ResultScreen extends StatelessWidget {
  final ScanResult result;
  final AppStrings strings;

  const ResultScreen({
    super.key,
    required this.result,
    required this.strings,
  });

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        backgroundColor: const Color(0xFF225B77),
        foregroundColor: Colors.white,
        title: Text(strings.result),
      ),
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(20),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              _field(strings.model, result.model),
              const SizedBox(height: 14),
              _field(strings.number, result.serialNumber),
              const SizedBox(height: 14),
              _field(
                strings.date,
                DateFormat('dd.MM.yyyy HH:mm').format(result.date),
              ),
              const SizedBox(height: 20),
              _confidenceBar(result.confidence),
              const Spacer(),
              ElevatedButton(
                onPressed: () => Navigator.pop(context),
                style: ElevatedButton.styleFrom(
                  backgroundColor: const Color(0xFF225B77),
                  foregroundColor: Colors.white,
                  padding: const EdgeInsets.symmetric(vertical: 18),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(10),
                  ),
                ),
                child: Text(
                  strings.close,
                  style: const TextStyle(
                    fontSize: 17,
                    letterSpacing: 2,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _field(String label, String? value) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          '$label:',
          style: const TextStyle(fontSize: 16, fontWeight: FontWeight.w600),
        ),
        const SizedBox(height: 6),
        Container(
          width: double.infinity,
          padding: const EdgeInsets.all(14),
          decoration: BoxDecoration(
            border: Border.all(color: const Color(0xFF225B77), width: 1.5),
            borderRadius: BorderRadius.circular(10),
          ),
          child: Text(
            (value == null || value.isEmpty) ? '—' : value,
            style: const TextStyle(fontSize: 16),
          ),
        ),
      ],
    );
  }

  Widget _confidenceBar(double confidence) {
    final percent = (confidence * 100).round();
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text('${strings.confidence}: $percent%'),
        const SizedBox(height: 6),
        ClipRRect(
          borderRadius: BorderRadius.circular(6),
          child: LinearProgressIndicator(
            value: confidence.clamp(0.0, 1.0),
            backgroundColor: Colors.grey.shade300,
            color: const Color(0xFF225B77),
            minHeight: 8,
          ),
        ),
      ],
    );
  }
}